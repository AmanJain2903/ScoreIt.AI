# model_store.py
from sentence_transformers import SentenceTransformer
from src.utils import config
import torch
from huggingface_hub import hf_hub_download
import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"



config = config.Config()

def download_from_huggingface(repo_id, filename, destination=None):
    """
    Downloads a file from Hugging Face Hub and saves it locally.

    Args:
        repo_id (str): The repo ID on Hugging Face, e.g., 'username/model-repo'
        filename (str): The file name in the repo, e.g., 'model.pt'
        destination (str): Optional custom path to save the file. If not provided, returns HF cache path.

    Returns:
        str: Path to the downloaded file
    """

    file_path = hf_hub_download(repo_id=repo_id, filename=filename)

    if destination:
        import shutil
        shutil.copy(file_path, destination)
        print(f"✅ File copied to {destination}")
        return destination

    return file_path

print("Downloading models from Hugging Face...")

repo_id = "AmanJain2903/ScoreIt.AI"

model_files = {
    config.MODEL_1_WEIGHTS: "model1.pt",
    config.MODEL_2_WEIGHTS: "model2.pt",
}

for filename, file_id in model_files.items():
    if not os.path.exists(filename):
        download_from_huggingface(repo_id, file_id, filename)

print("Models downloaded successfully")



print("⏳ Preloading SentenceTransformer models...")

model1 = SentenceTransformer(config.MODEL_NAME_1)
model1.load_state_dict(torch.load(config.MODEL_1_WEIGHTS, map_location=torch.device('cpu'), weights_only=False))    
model2 = SentenceTransformer(config.MODEL_NAME_2)
model2.load_state_dict(torch.load(config.MODEL_2_WEIGHTS, map_location=torch.device('cpu'), weights_only=False))
print("✅ Models loaded and ready")