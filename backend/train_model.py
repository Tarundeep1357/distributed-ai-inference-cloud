from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier 

def train_model() -> None:
    iris= load_iris()

    x= iris.data
    y= iris.target

    model= RandomForestClassifier(
        n_estimators= 100,
        random_state= 42
    )

    model.fit(x,y)

    model_dir= Path("models")
    model_dir.mkdir(exist_ok= True)

    model_path= model_dir / "iris_model.joblib"

    joblib.dump(model , model_path)

    print(f"model saved to: {model_path}")


if __name__== "__main__":
    train_model()


