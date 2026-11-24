""" Retrieve top-k chunks, ask the LLM to answer ONLY from them, with citations."""
from functools import lru_cache
import litellm
from fastembed import TextEmbedding 
from qdrant_client import QdrantClient
from fin_reg_copilot import config


PROMPT = """ You answer questions about financial regulatory documents. Use Only the context below. If the answer is not in the context, say "I don't know based on the documents. Cite sources like [file.pdf p.3] after each claim.

context: {context}
Question: {question}
Answer:"""

# lru_cache
@lru_cache
def _embedder():
    return TextEmbedding(config.EMBED_MODEL)

@lru_cache
def _client():
    return QdrantClient(path=str(config.QDRANT_PATH))

def retrieve(question, k= config.TOP_K):
    qvec = next(iter(_embedder().embed([question]))).tolist()
    hits = _client().query_points(config.COLLECTION, query= qvec, limit= k).points
    return [{**h.payload, "score": round(h.score, 3)} for h in hits]

def answer(question):
    if not config.LLM_MODEL:
        raise RuntimeError("Set LLM_MODEL in .env")
    chunks = retrieve(question)
    context = "\n\n".join(f"[{c['source']} p.{c['page']}]\n{c['text']}" for c in chunks)
    resp = litellm.completion(
        model=config.LLM_MODEL,
        messages=[{"role": "user", "content": PROMPT.format(context=context, question=question)}],
        temperature=0,
        # LiteLLM's model map wrongly says this model doesn't support temperature; the API accepts it (tested 24 Nov 2026)
        num_retries=3,
        allowed_openai_params=["temperature"],
    )
    return {"answer": resp.choices[0].message.content, "sources": chunks}