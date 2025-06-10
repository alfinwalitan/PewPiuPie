import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
rf_model_path = os.path.join(BASE_DIR, "models", "random_forest", "random_forest_model_97.pkl")
rf_model = joblib.load(rf_model_path)

def classify_res(features):
    df = pd.DataFrame([features])
    return rf_model.predict(df)[0]