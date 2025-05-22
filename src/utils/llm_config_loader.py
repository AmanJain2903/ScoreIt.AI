# src/utils/config_loader.py

import yaml
import importlib.resources

class Config:
    def __init__(self):
        try:
            # Correctly load config.yml from the installed package
            configPath = importlib.resources.files('src.utils').joinpath('llm_model_config.yml')
            with configPath.open('r') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load config.yml: {e}")

        # Set class attributes from config keys
        self.MODEL_NAMES = config.get("MODEL_NAMES")