import os
import yaml
import importlib.resources

# This is a configuration class for the Designation Matchmaker.
# It loads configuration settings from a YAML file named "Config.yml".
# The configuration settings include model names.


class Config:
    def __init__(self):
        try:
            # Correctly load config.yml from the installed package
            configPath = importlib.resources.files('src.designation_matchmaker').joinpath('config.yml')
            with configPath.open('r') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load config.yml: {e}")

        # Set class attributes from config keys
        self.MODEL_NAME_1 = config.get("MODEL_NAME_1")
        self.MODEL_NAME_2 = config.get("MODEL_NAME_2")
        self.MAX_INPUT_LENGTH = config.get("MAX_INPUT_LENGTH")