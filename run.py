from api.app import create_app
from sentence_transformers import SentenceTransformer

print("⏳ Preloading Hugging Face models...")

SentenceTransformer('all-mpnet-base-v2')
SentenceTransformer('paraphrase-MiniLM-L3-v2')

print("✅ Hugging Face models loaded and cached")

app = create_app()