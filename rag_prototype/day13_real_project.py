"""
Sprint 1 / Week 3 / Day 3 (Day 13 overall) — Index the REAL Project README

Replaces all placeholder text used through Weeks 1-2 with your actual
ai-data-quality-assistant README content, chunked and indexed into the
same Azure AI Search index from Day 12.

Setup: same as Day 12 (azure-search-documents, openai already installed)

Run:
    python3 day13_real_project.py build
    python3 day13_real_project.py query
"""

import os
import sys
from openai import OpenAI
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
MAX_SCORE = 0.56  # starting point from Day 12 -- recalibrate below if needed

endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
key = os.environ["AZURE_SEARCH_KEY"]
search_client = SearchClient(endpoint=endpoint, index_name="dq-assistant-index",
                              credential=AzureKeyCredential(key))

# Your ACTUAL README content, pulled from github.com/AsthaSaraf-git/ai-data-quality-assistant
# Chunked manually by real section, since the "⸻" divider isn't a reliable
# auto-split point (it's a stylistic character, not consistent markdown).
readme_chunks = [
    {"section": "Overview", "text":
        "Data Quality Assistant is a metadata-driven data quality framework built in "
        "Python that validates datasets using configurable YAML rules, tracks quality "
        "trends over time, and generates dashboards for monitoring data health. The "
        "framework follows a simple principle: new datasets should be onboarded through "
        "configuration, not code changes."},

    {"section": "Validation Rules", "text":
        "Supported validation rules: Not Null Validation, Regex Validation, Min Value "
        "Validation, Max Value Validation, Unique Validation, Accepted Values Validation."},

    {"section": "Framework Capabilities", "text":
        "Framework capabilities include metadata-driven architecture, multi-table "
        "validation, YAML-based rule configuration, detailed validation reports, "
        "quality score calculation, historical quality tracking, trend chart "
        "generation, and HTML dashboard generation."},

    {"section": "Architecture", "text":
        "The architecture flow is: CSV Files feed into YAML Rules, which feed into the "
        "Validation Engine, which produces a Validation Report, which generates Quality "
        "Metrics. Quality metrics branch into a Summary Report, History Tracking, Trend "
        "Charts, and an HTML Dashboard."},

    {"section": "Project Structure", "text":
        "The src folder contains file_loader.py, rule_engine.py, report_generator.py, "
        "dashboard_generator.py, history_tracker.py, trend_dashboard.py, and validator.py. "
        "Data lives in the data folder as CSV files. Rules live in the rules folder as "
        "YAML files. Reports are written to the reports folder."},

    {"section": "Roadmap - Phase 1", "text":
        "Phase 1, the Data Quality Framework, is complete: multi-table validation, "
        "metadata-driven rules, quality scoring, historical tracking, trend analysis, "
        "and dashboard generation."},

    {"section": "Roadmap - Phase 2", "text":
        "Phase 2, Observability, is planned: quality alerts, SLA monitoring, data "
        "freshness checks, and volume anomaly detection."},

    {"section": "Roadmap - Phase 3", "text":
        "Phase 3, AI Assistant, is planned: OpenAI integration, root cause analysis, "
        "natural language investigation, and remediation recommendations. Example: "
        "asking why a customer quality score dropped this week should surface primary "
        "causes like duplicate customer IDs, invalid email formats, and missing customer "
        "names, along with recommended actions such as validating customer IDs at "
        "source and adding email validation during ingestion."},

    {"section": "Tech Stack", "text":
        "The tech stack is Python, Pandas, Matplotlib, YAML, HTML, Git, and GitHub. "
        "Notably, this does not currently include Databricks, Delta Lake, or Unity "
        "Catalog -- the framework currently reads plain CSV files, not managed tables."},
]


def embed(text):
    return openai_client.embeddings.create(model=EMBED_MODEL, input=text).data[0].embedding


def build():
    docs_to_upload = []
    for i, c in enumerate(readme_chunks):
        docs_to_upload.append({
            "id": f"readme-{i}",
            "content": c["text"],
            "source": "ai_data_quality_assistant_readme",
            "section": c["section"],
            "content_vector": embed(c["text"]),
        })
    result = search_client.upload_documents(documents=docs_to_upload)
    succeeded = sum(1 for r in result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(docs_to_upload)} real README chunks.")
    print("Now run: python3 day13_real_project.py query")


def retrieve(question, top_k=3, source_filter="ai_data_quality_assistant_readme"):
    q_vector = embed(question)
    vector_query = VectorizedQuery(vector=q_vector, k_nearest_neighbors=top_k, fields="content_vector")
    filter_str = f"source eq '{source_filter}'" if source_filter else None
    results = search_client.search(
        search_text=None, vector_queries=[vector_query], filter=filter_str,
        select=["content", "source", "section"], top=top_k,
    )
    kept = []
    for r in results:
        score = r["@search.score"]
        kept.append((r["content"], r["section"], score))  # print ALL scores today, unfiltered, for calibration
    return kept


def answer(question):
    retrieved = retrieve(question)
    print(f"\nQuestion: {question}")
    for content, section, score in retrieved:
        flag = "" if score > MAX_SCORE else "  <-- below current threshold"
        print(f"[score {score:.4f}]{flag} ({section}) {content[:80]}...")

    kept = [(c, s, sc) for c, s, sc in retrieved if sc > MAX_SCORE]
    if not kept:
        print("Answer: [No chunk cleared the threshold]")
        return

    context = "\n\n".join(f"[{sec}]: {c}" for c, sec, _ in kept)
    response = openai_client.chat.completions.create(
        model=CHAT_MODEL, temperature=0,
        messages=[
            {"role": "system", "content": "Answer using ONLY the excerpts, citing the section."},
            {"role": "user", "content": f"Excerpts:\n{context}\n\nQuestion: {question}"},
        ],
    )
    print(f"Answer: {response.choices[0].message.content}")


def query_loop():
    answer("What validation rules does this framework support?")
    print("=" * 60)
    answer("What is planned for the AI assistant phase?")
    print("=" * 60)
    answer("Does this project use Databricks or Unity Catalog?")


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode == "build":
        build()
    elif mode == "query":
        query_loop()
    else:
        print("Usage: python3 day13_real_project.py [build|query]")
