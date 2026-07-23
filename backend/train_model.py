from pathlib import Path

import joblib
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier 

def train_model():
    iris= load_iris()

    x= iris.data
    y= iris.target

    
