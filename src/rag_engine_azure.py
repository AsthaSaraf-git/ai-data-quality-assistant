import ast
import os

import pandas as pd
from openai import AzureOpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
)

# Azure OpenAI addresses models by deployment name, not model id -- this is
# the name of the deployment in the Azure OpenAI resource, not a model id.
EMBED_DEPLOYMENT = "dq-embed-small"

# Assumes the "dq-embed-small" deployment is backed by text-embedding-3-small
# (1536 dims), matching the plain-OpenAI version in rag_engine.py. Update
# this if the deployment is ever repointed at a different base model.
EMBED_DIMENSIONS = 1536

# Same index as the plain-OpenAI version (rag_engine.py) -- either script can
# populate/query it, as long as EMBED_DIMENSIONS stays consistent between them.
INDEX_NAME = "dq-reports-index"

# Sample size for the failed-row indices embedded in each validation-failure
# chunk. Calibrated against this project's actual reports/validation_report.csv
# (2026-07-30, real Unity Catalog data): per-rule failed row counts range from
# 4 to 35, median 14 (25th percentile 8). Capping at 10 keeps the full list for
# anything at/below the 25th percentile while stopping high-failure columns
# (e.g. 35 duplicate customer_ids) from dumping dozens of raw indices into the
# embedding text. Re-check this distribution and adjust if failure volumes
# change significantly -- don't just bump the number on a hunch.
FAILED_ROWS_SAMPLE_SIZE = 10


def _chunk_validation_failures(validation_report_path):
    df = pd.read_csv(validation_report_path)
    failures = df[df["status"] == "FAILED"]

    chunks = []
    for i, row in failures.reset_index(drop=True).iterrows():
        failed_rows = ast.literal_eval(row["failed_rows"])
        sample = failed_rows[:FAILED_ROWS_SAMPLE_SIZE]
        remainder = len(failed_rows) - len(sample)

        sample_text = ", ".join(str(idx) for idx in sample)
        if remainder > 0:
            sample_text += f" (and {remainder} more)"

        content = (
            f"Table '{row['table_name']}', column '{row['column']}', rule "
            f"'{row['rule']}' FAILED: {row['failed_count']} of "
            f"{row['total_records']} records failed "
            f"({row['failure_percentage']}% failure rate). "
            f"Sample failed row indices: {sample_text}."
        )

        chunks.append({
            "id": f"validation-{row['table_name']}-{row['column']}-{row['rule']}-{i}",
            "content": content,
            "table_name": row["table_name"],
            "type": "validation_failure",
        })

    return chunks


def _chunk_history_entries(history_path):
    df = pd.read_csv(history_path)

    chunks = []
    for i, row in df.reset_index(drop=True).iterrows():
        content = (
            f"On {row['run_timestamp']}, table '{row['table_name']}' had a "
            f"quality score of {row['quality_score']}% "
            f"({row['passed_rules']} of {row['total_rules']} rules passed, "
            f"{row['failed_rules']} failed)."
        )

        chunks.append({
            "id": f"history-{row['table_name']}-{i}",
            "content": content,
            "table_name": row["table_name"],
            "type": "history_entry",
        })

    return chunks


def chunk_reports(reports_folder="reports"):
    validation_report_path = os.path.join(reports_folder, "validation_report.csv")
    history_path = os.path.join(reports_folder, "history.csv")

    chunks = []
    chunks.extend(_chunk_validation_failures(validation_report_path))
    chunks.extend(_chunk_history_entries(history_path))

    return chunks


def embed_chunks(chunks):
    azure_client = AzureOpenAI(
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        api_version=os.environ["AZURE_OPENAI_API_VERSION"],
    )

    embedded_chunks = []
    for chunk in chunks:
        vector = azure_client.embeddings.create(
            model=EMBED_DEPLOYMENT, input=chunk["content"]
        ).data[0].embedding
        embedded_chunks.append({**chunk, "content_vector": vector})

    return embedded_chunks


def _create_index_with_vector_field(index_client):
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="table_name", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="type", type=SearchFieldDataType.String, filterable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=EMBED_DIMENSIONS,
            vector_search_profile_name="default-profile",
        ),
    ]

    vector_search = VectorSearch(
        algorithms=[HnswAlgorithmConfiguration(name="default-hnsw")],
        profiles=[VectorSearchProfile(name="default-profile", algorithm_configuration_name="default-hnsw")],
    )

    index = SearchIndex(name=INDEX_NAME, fields=fields, vector_search=vector_search)
    index_client.create_or_update_index(index)


def store_in_azure_search(embedded_chunks):
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_KEY"]
    credential = AzureKeyCredential(key)

    index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
    search_client = SearchClient(endpoint=endpoint, index_name=INDEX_NAME, credential=credential)

    _create_index_with_vector_field(index_client)

    docs_to_upload = [
        {
            "id": chunk["id"],
            "content": chunk["content"],
            "table_name": chunk["table_name"],
            "type": chunk["type"],
            "content_vector": chunk["content_vector"],
        }
        for chunk in embedded_chunks
    ]

    result = search_client.upload_documents(documents=docs_to_upload)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(docs_to_upload)} chunks to '{INDEX_NAME}'.")

    return succeeded, len(docs_to_upload)
