from dotenv import load_dotenv

from rag_engine_azure import chunk_reports, embed_chunks, store_in_azure_search, EMBED_DIMENSIONS

load_dotenv()

chunks = chunk_reports()
print(f"Chunked {len(chunks)} report entries.")

sample = chunks[:2]
embedded = embed_chunks(sample)

for chunk in embedded:
    vector_length = len(chunk["content_vector"])
    status = "OK" if vector_length == EMBED_DIMENSIONS else "MISMATCH"
    print(f"{chunk['id']}: vector length {vector_length} ({status})")

store_in_azure_search(embedded)
