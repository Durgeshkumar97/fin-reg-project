import os 
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT/ "data/raw"
EMBED_CACHE = ROOT / "data" / "models"
QDRANT_PATH = ROOT / "data"/"qdrant"

# all collections will be stored in this collection name
COLLECTION = "fin_docs"

EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/gemini/gemini-3.5-flash-lite")

LLM_MODEL =os.getenv("LLM_MODEL", "")

CHUNK_SIZE = 1000 # characters

CHUNK_OVERLAP = 150

TOP_K = 5

