# model_store.py
from sentence_transformers import SentenceTransformer
from utils.config import Config

config = Config()

print("⏳ Preloading SentenceTransformer models...")

model1 = SentenceTransformer(config.MODEL_NAME_1)
model2 = SentenceTransformer(config.MODEL_NAME_2)

print("✅ Models loaded and ready")