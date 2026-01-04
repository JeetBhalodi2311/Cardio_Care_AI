import joblib
import pandas as pd
import numpy as np

model = joblib.load("model1.pkl")

# Rows from Cardio_cleaned.csv
# Row 3 (id 1): cardo=1, gender=1, height=156, weight=85.0, ap_hi=140, ap_lo=90, cholesterol=3, gluc=1, smoke=0, alco=0, active=1, Age_Year=55
# Row 5 (id 3): cardo=1, gender=2, height=169, weight=82.0, ap_hi=150, ap_lo=100, cholesterol=1, gluc=1, smoke=0, alco=0, active=1, Age_Year=48

samples = [
    {
        "name": "Row 3 (ID 1) - High Chol/BP",
        "data": [1, 156, 85, 140, 90, 3, 1, 0, 0, 1, 55]
    },
    {
        "name": "Row 5 (ID 3) - High BP",
        "data": [2, 169, 82, 150, 100, 1, 1, 0, 0, 1, 48]
    }
]

feature_names = ['gender', 'height', 'weight', 'ap_hi', 'ap_lo', 'cholesterol', 'gluc', 'smoke', 'alco', 'active', 'Age_Year']

for s in samples:
    df = pd.DataFrame([s['data']], columns=feature_names)
    pred = model.predict(df)[0]
    proba = model.predict_proba(df)[0]
    print(f"Sample: {s['name']}")
    print(f"  Prediction: {pred}")
    print(f"  Proba: {proba}")
    print(f"  Risk %: {round(proba[1]*100, 2)}%")
    print("-" * 20)
