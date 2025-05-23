# model_store.py
from sentence_transformers import SentenceTransformer
from src.utils import config
import torch
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

config = config.Config()

print("⏳ Preloading SentenceTransformer models...")

model1 = SentenceTransformer(config.MODEL_NAME_1)
model1.load_state_dict(torch.load(config.MODEL_1_WEIGHTS, map_location=torch.device('cpu')))    
model2 = SentenceTransformer(config.MODEL_NAME_2)
model2.load_state_dict(torch.load(config.MODEL_2_WEIGHTS, map_location=torch.device('cpu')))
print("✅ Models loaded and ready")