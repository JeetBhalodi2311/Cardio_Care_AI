import joblib
import pickle
import os
import numpy as np

MODEL_PATH = "model1.pkl"

def check_model():
    model = None
    if os.path.exists(MODEL_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            print(f"Model loaded with joblib: {type(model)}")
        except:
            try:
                with open(MODEL_PATH, "rb") as f:
                    model = pickle.load(f)
                print(f"Model loaded with pickle: {type(model)}")
            except Exception as e:
                print(f"Failed to load: {e}")
                return

    if model:
        if hasattr(model, "feature_names_in_"):
            print(f"Feature names model expects: {model.feature_names_in_}")
        
        if hasattr(model, "predict_proba"):
            print("Model supports predict_proba")
            # Try a dummy prediction
            try:
                # 11 features expected
                dummy = np.zeros((1, 11))
                proba = model.predict_proba(dummy)
                print(f"Dummy prediction proba: {proba}")
            except Exception as e:
                print(f"predict_proba failed during execution: {e}")
        else:
            print("Model DOES NOT support predict_proba")
            if hasattr(model, "decision_function"):
                print("Model has decision_function")
            else:
                print("Model has neither predict_proba nor decision_function")

check_model()
