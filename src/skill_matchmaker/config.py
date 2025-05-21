import yaml
import importlib.resources

# This is a configuration class for the Skill Matchmaker.
# It loads configuration settings from a YAML file named "Config.yml".
# The configuration settings include model names.


class Config:
    def __init__(self):
        try:
            # Correctly load config.yml from the installed package
            configPath = importlib.resources.files('src.skill_matchmaker').joinpath('config.yml')
            with configPath.open('r') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load config.yml: {e}")

        # Set class attributes from config keys
        self.TECHNICAL_MAX_INPUT_LENGTH = config.get("TECHNICAL_MAX_INPUT_LENGTH")
        self.SOFT_MAX_INPUT_LENGTH = config.get("SOFT_MAX_INPUT_LENGTH")