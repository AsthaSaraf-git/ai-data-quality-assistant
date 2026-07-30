"""
Sprint 1 / Week 3 / Day 2 (Day 12 overall) — Real Pipeline on Azure AI Search

Ports Day 10's consolidated logic (section-aware chunking, embeddings,
metadata, threshold-based retrieval) onto Azure AI Search instead of Chroma.

Setup:
    pip3 install azure-search-documents openai

Run:
    python3 day12_azure_pipeline.py build
    python3 day12_azure_pipeline.py query
"""

import os
import sys
from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, VectorSearchProfile,
)
from azure.search.documents.models import VectorizedQuery

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
EMBED_MODEL = "text-embedding-3-small"
EMBED_DIMENSIONS = 1536  # from Day 4 -- text-embedding-3-small's fixed output size
CHAT_MODEL = "gpt-4o-mini"
MAX_DISTANCE_SCORE = 0.56  # recalibrated: relevant matches bottomed out at 0.5875,
                            # off-topic (biryani) topped out at 0.5431 -- 0.35 let everything through

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
key = os.environ["AZURE_SEARCH_KEY"]
credential = AzureKeyCredential(key)
INDEX_NAME = "dq-assistant-index"

index_client = SearchIndexClient(endpoint=endpoint, credential=credential)
search_client = SearchClient(endpoint=endpoint, index_name=INDEX_NAME, credential=credential)


def embed(text):
    return openai_client.embeddings.create(model=EMBED_MODEL, input=text).data[0].embedding


def section_aware_chunk(text, source_name):
    chunks = []
    for section in text.split("\n## "):
        section = section.strip()
        if not section:
            continue
        lines = section.split("\n", 1)
        title = lines[0].replace("##", "").strip()
        body = lines[1].strip() if len(lines) > 1 else ""
        paragraphs = [p.strip() for p in body.split("\n\n") if p.strip()] or ([body] if body else [])
        for para in paragraphs:
            chunks.append({"text": para, "section": title, "source": source_name})
    return chunks


documents = {
    "dq_assistant_design_notes": """
## Overview
Data Quality Assistant monitors Delta tables for anomalies

## Checks Performed
- Null value spikes
- Schema drift detection
- Row count deviation
- Duplicate key violations

## Architecture
Uses Unity Catalog for lineage tracking. Runs as a scheduled Databricks job nightly.

## Known Limitations
- Root cause matching is keyword-based, not semantic
- Planned fix: RAG pipeline with vector store retrieval
""".strip(),

    "oncall_runbook": """
## Rotation
On-call rotation is weekly, starting Monday 9am IST

## Escalation
Escalation path is Slack #data-platform-oncall, then PagerDuty after 15 minutes

## Rollback
Revert the Databricks Asset Bundle deployment via the previous git tag, then re-run the nightly job manually
""".strip(),
}


def create_index_with_vector_field():
    """
    Rebuilds the index from Day 11 to ADD a vector field. Azure needs to
    know the vector's dimension count and similarity algorithm (HNSW,
    same name from Day 6's concept discussion) up front, in the schema.
    """
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
        SearchField(name="section", type=SearchFieldDataType.String, filterable=True),
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
    print(f"Index '{INDEX_NAME}' updated with a vector field ({EMBED_DIMENSIONS} dimensions, HNSW).")


def build():
    create_index_with_vector_field()

    docs_to_upload = []
    doc_id = 0
    for source_name, text in documents.items():
        for c in section_aware_chunk(text, source_name):
            docs_to_upload.append({
                "id": str(doc_id),
                "content": c["text"],
                "source": c["source"],
                "section": c["section"],
                "content_vector": embed(c["text"]),
            })
            doc_id += 1

    result = search_client.upload_documents(documents=docs_to_upload)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(docs_to_upload)} chunks to Azure AI Search.")
    print("Now run: python3 day12_azure_pipeline.py query")


def retrieve(question, top_k=3, source_filter=None):
    q_vector = embed(question)
    vector_query = VectorizedQuery(vector=q_vector, k_nearest_neighbors=top_k, fields="content_vector")

    filter_str = f"source eq '{source_filter}'" if source_filter else None

    results = search_client.search(
        search_text=None,
        vector_queries=[vector_query],
        filter=filter_str,
        select=["content", "source", "section"],
        top=top_k,
    )

    kept = []
    for r in results:
        score = r["@search.score"]  # Azure's cosine similarity: higher = better
        if score > MAX_DISTANCE_SCORE:
            kept.append((r["content"], r["source"], r["section"], score))
    return kept


def answer(question, source_filter=None):
    retrieved = retrieve(question, source_filter=source_filter)
    print(f"\nQuestion: {question}")
    if not retrieved:
        print("No chunk cleared the relevance threshold -- correctly answering nothing.")
        return

    for content, source, section, score in retrieved:
        print(f"[score {score:.4f}] ({source} / {section}) {content[:70]}...")

    context = "\n\n".join(f"[{s}/{sec}]: {c}" for c, s, sec, _ in retrieved)
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL, temperature=0,
        messages=[
            {"role": "system", "content": "Answer using ONLY the excerpts, citing source and section."},
            {"role": "user", "content": f"Excerpts:\n{context}\n\nQuestion: {question}"},
        ],
    )
    print(f"Answer: {response.choices[0].message.content}")


def query_loop():
    answer("How does the system currently figure out root cause?")
    print("=" * 60)
    answer("What is the recipe for biryani?")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode == "build":
        build()
    elif mode == "query":
        query_loop()
    else:
        print("Usage: python3 day12_azure_pipeline.py [build|query]")
