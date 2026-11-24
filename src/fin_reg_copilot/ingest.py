""" PDFs -> text-> chunks -> embeddings -> Qdrant. Run uv python -m fin_reg_copilot.ingest """

import uuid
from fastembed import TextEmbedding
from pypdf import PdfReader
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from fin_reg_copilot import config


def load_pages(pdf_path):
    # Yield (page_number, text) for each page that has text.
    reader =PdfReader(pdf_path)

    for i, page in enumerate(reader.pages, start= 1):
        text = (page.extract_text() or "").strip()
        if text:
            yield i, text

def chunk_text(text, size= config.CHUNK_SIZE, overlap= config.CHUNK_OVERLAP):
    chunks, start = [],0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

def build_records():
    records = []
    pdfs = sorted(config.RAW_DIR.glob("*.pdf"))
    if not pdfs:
        raise SystemExit(f"No PDFs found in {config.RAW_DIR}")
    for pdf in pdfs:
        for page_no, text in load_pages(pdf):
            for chunk in chunk_text(text):
                records.append({"text": chunk, "source": pdf.name, "page": page_no})
    return records

def main():
    records = build_records()
    print(f"Chunks: {len(records)}")
    embedder = TextEmbedding(config.EMBED_MODEL)
    vectors = list(embedder.embed([r["text"] for r in records]))
    client = QdrantClient(path= str(config.QDRANT_PATH))

    if client.collection_exists(config.COLLECTION):
        client.delete_collection(config.COLLECTION)
    client.create_collection(
        config.COLLECTION,
        vectors_config = VectorParams(size= len(vectors[0]), distance= Distance.COSINE),
    )

    client.upsert(
        config.COLLECTION,
        points= [
            PointStruct(id=str(uuid.uuid4()), vector= v.tolist(), payload=r)
            for v,r in zip(vectors, records)
        
        ],
    )

    print(f"Stored {len(records)} chunks in '{config.COLLECTION}")

if __name__ == "__main__":
    main()

