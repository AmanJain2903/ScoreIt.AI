import yaml
import importlib.resources



class Config:
    def __init__(self):
        try:
            # Correctly load config.yml from the installed package
            configPath = importlib.resources.files('src.utils').joinpath('config.yml')
            model1_weights_path = importlib.resources.files('src.utils').joinpath('models/model1.pt')
            model2_weights_path = importlib.resources.files('src.utils').joinpath('models/model2.pt')
            with configPath.open('r') as file:
                config = yaml.safe_load(file)
        except Exception as e:
            raise RuntimeError(f"Failed to load config.yml: {e}")

        # Set class attributes from config keys
        self.MODEL_NAME_1 = config.get("MODEL_NAME_1")
        self.MODEL_NAME_2 = config.get("MODEL_NAME_2")
        self.MODEL_1_WEIGHTS = model1_weights_path
        self.MODEL_2_WEIGHTS = model2_weights_path