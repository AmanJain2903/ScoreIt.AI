import os
import yaml
import importlib.resources

# This is a configuration class for the JD-ExtractorAgent.
# It loads configuration settings from a YAML file named "Config.yml".
# The configuration settings include API name, model name, and the path to the default system prompt.


class Config:
    def __init__(self):
        try:
            # Correctly load config.yml from the installed package
            configPath = importlib.resources.files('src.resume_extractor_agent').joinpath('config.yml')
            with configPath.open('r') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load config.yml: {e}")

        # Set class attributes from config keys
        self.API_NAME = config.get("API_NAME")
        self.MODEL_NAME = config.get("MODEL_NAME")
        self.DEFAULT_SYSTEM_PROMPT_PATH = config.get("DEFAULT_SYSTEM_PROMPT_PATH")
        self.MAX_INPUT_LENGTH = config.get("MAX_INPUT_LENGTH")