from pathlib import Path

import joblib

class ModelService:
    def __init__(self) -> None:
        model_path= (
            Path(__file__).resolve().parent.parent
            /"models"
            /"iris_model.joblib"
        )

        if not model_path.exists():
            raise FileNotFoundError(
                f"Model not found at: {model_path}"
            )

        self.model= joblib.load(model_path)

    def predict(self,features: list [float]) -> int:
        prediction= self.model.predict([features])

        return int(prediction[0])