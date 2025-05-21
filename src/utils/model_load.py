# model_store.py
from sentence_transformers import SentenceTransformer

print("⏳ Preloading SentenceTransformer models...")

model1 = SentenceTransformer("all-mpnet-base-v2")
model2 = SentenceTransformer("paraphrase-MiniLM-L3-v2")

print("✅ Models loaded and ready")