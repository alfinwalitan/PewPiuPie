import os
import joblib
import pandas as pd

rf_model = None  # global cache

def load_rf_model():
    global rf_model
    if rf_model is None:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        rf_model_path = os.path.join(BASE_DIR, "models", "random_forest", "random_forest_model_95_new.pkl")
        rf_model = joblib.load(rf_model_path)
    return rf_model

def classify_res(features):
    model = load_rf_model()
    df = pd.DataFrame([features])
    return model.predict(df)[0]