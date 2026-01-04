# # streamlit_cardio_ui.py
# import streamlit as st
# import joblib
# import io
# import os
# import numpy as np
# from sklearn.pipeline import Pipeline

# st.set_page_config(page_title="Cardio Risk Predictor", layout="centered")
# st.title("Cardio Risk Predictor")

# FEATURES = ['gender','height','weight','ap_hi','ap_lo','cholesterol','gluc','smoke','alco','active','Age_Year']
# MODEL_PATH = "model.pkl"

# @st.cache_resource
# def load_model_from_path(path):
#     try:
#         return joblib.load(path)
#     except Exception as e:
#         return None

# @st.cache_resource
# def load_model_from_bytes(b):
#     try:
#         return joblib.load(io.BytesIO(b))
#     except Exception:
#         # try pickle.loads fallback
#         import pickle
#         try:
#             return pickle.loads(b)
#         except Exception:
#             return None

# def apply_optional_scaler(scaler, X):
#     # scaler can be a transformer with transform method
#     if scaler is None:
#         return X
#     try:
#         return scaler.transform(X)
#     except Exception:
#         return X

# # --- Load model (from disk if exists) ---
# model = None
# if os.path.exists(MODEL_PATH):
#     model = load_model_from_path(MODEL_PATH)
#     if model is None:
#         st.error(f"Failed to load model from {MODEL_PATH} (file may be incompatible). You can upload it below.")

# # Allow user to upload model if disk load failed or they prefer upload
# st.markdown("### Model (auto-loads `model.pkl` if present)")
# uploaded_model = st.file_uploader("Upload model.pkl (joblib/pickle)", type=["pkl","joblib"], accept_multiple_files=False)
# if uploaded_model is not None:
#     b = uploaded_model.read()
#     uploaded_model.seek(0)
#     model = load_model_from_bytes(b)
#     if model is None:
#         st.error("Failed to load uploaded model. Make sure it's a scikit-learn estimator or Pipeline saved with joblib/pickle.")
#     else:
#         st.success("Model loaded from upload.")

# # Optional scaler upload (if you trained model without pipeline and used a scaler)
# st.markdown("### (Optional) Upload scaler if you used one during training")
# uploaded_scaler = st.file_uploader("Upload scaler.pkl (e.g., StandardScaler saved with joblib)", type=["pkl","joblib"], key="scaler")
# scaler = None
# if uploaded_scaler is not None:
#     try:
#         scaler = load_model_from_bytes(uploaded_scaler.read())
#         if scaler is None:
#             st.error("Failed to load uploaded scaler.")
#         else:
#             st.success("Scaler loaded.")
#     except Exception as e:
#         st.error(f"Scaler load error: {e}")

# st.markdown("---")
# st.subheader("Enter patient features")

# col1, col2 = st.columns(2)
# with col1:
#     gender = st.selectbox("Gender (0=female,1=male)", options=[0,1], index=0)
#     height = st.number_input("Height (cm)", min_value=50, max_value=300, value=170)
#     weight = st.number_input("Weight (kg)", min_value=10.0, max_value=500.0, value=70.0, format="%.2f")
#     ap_hi = st.number_input("Systolic BP (ap_hi)", min_value=50, max_value=300, value=120)
# with col2:
#     ap_lo = st.number_input("Diastolic BP (ap_lo)", min_value=30, max_value=200, value=80)
#     cholesterol = st.selectbox("Cholesterol (1=normal,2=above,3=well above)", [1,2,3], index=0)
#     gluc = st.selectbox("Glucose (1=normal,2=above,3=well above)", [1,2,3], index=0)
#     smoke = st.selectbox("Smoker (0=no,1=yes)", [0,1], index=0)

# col3, col4 = st.columns(2)
# with col3:
#     alco = st.selectbox("Alcohol (0=no,1=yes)", [0,1], index=0)
#     active = st.selectbox("Active (0=no,1=yes)", [0,1], index=1)
# with col4:
#     Age_Year = st.number_input("Age (years)", min_value=0, max_value=120, value=45)

# # Predict button
# if st.button("Predict"):
#     if model is None:
#         st.error("No model loaded. Put model.pkl in the folder or upload it.")
#     elif ap_lo > ap_hi:
#         st.error("ap_lo cannot be greater than ap_hi.")
#     else:
#         # Build feature vector in correct order
#         X = np.array([[gender, height, weight, ap_hi, ap_lo,
#                        cholesterol, gluc, smoke, alco, active, Age_Year]], dtype=float)
#         try:
#             # if model is a pipeline, it will handle scaling itself
#             if isinstance(model, Pipeline):
#                 pred = model.predict(X)
#                 proba = None
#                 if hasattr(model, "predict_proba"):
#                     try:
#                         proba = model.predict_proba(X)[0]
#                     except Exception:
#                         proba = None
#             else:
#                 # If user supplied a scaler, apply it
#                 X_to_use = apply_optional_scaler(scaler, X)
#                 pred = model.predict(X_to_use)
#                 proba = None
#                 if hasattr(model, "predict_proba"):
#                     try:
#                         proba = model.predict_proba(X_to_use)[0]
#                     except Exception:
#                         proba = None

#             label = int(pred[0])
#             st.success(f"Predicted cardio: {label}  (0 = No, 1 = Yes)")

#             if proba is not None:
#                 # show probability for class 1 if binary
#                 if len(proba) > 1:
#                     p1 = proba[1]
#                     st.info(f"Probability cardio=1: {p1:.3f}")
#                     st.progress(min(max(p1, 0.0), 1.0))
#                 else:
#                     st.write(f"Probability: {proba[0]:.3f}")
#         except Exception as e:
#             st.error(f"Prediction failed: {e}")

# st.markdown("---")
# st.caption("Notes: If you used scaling (StandardScaler/MinMaxScaler) during training, either save and upload that scaler as scaler.pkl or re-save your model as a Pipeline (scaler + model) using joblib so the UI can use raw input values directly.")



# streamlit_cardio_ui.py
import streamlit as st
import joblib
import io
import os
import numpy as np
from sklearn.pipeline import Pipeline
import pickle

st.set_page_config(page_title="Cardio Risk Predictor", layout="centered")
st.title("Cardio Risk Predictor")

FEATURES = ['gender','height','weight','ap_hi','ap_lo','cholesterol','gluc','smoke','alco','active','Age_Year']
MODEL_PATH = "model1.pkl"   # <<---- STATIC MODEL NAME

# -------------------------------------------------------
# Load model helpers
# -------------------------------------------------------
@st.cache_resource
def load_model_from_path(path):
    try:
        return joblib.load(path)
    except:
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except:
            return None

@st.cache_resource
def load_model_from_bytes(b):
    try:
        return joblib.load(io.BytesIO(b))
    except:
        try:
            return pickle.loads(b)
        except:
            return None

# -------------------------------------------------------
# Load model (disk → upload override)
# -------------------------------------------------------
model = None

# Auto load model1.pkl if exists
if os.path.exists(MODEL_PATH):
    model = load_model_from_path(MODEL_PATH)
    if model is not None:
        st.success("Auto-loaded model1.pkl from folder.")
    else:
        st.error("model1.pkl exists but cannot be loaded (corrupted or incompatible).")

# Upload model1.pkl manually
st.markdown("### Upload Model File (`model1.pkl`)")
uploaded_model = st.file_uploader(
    "Upload model1.pkl (joblib / pickle format)",
    type=["pkl", "joblib"],
    accept_multiple_files=False
)

if uploaded_model is not None:
    b = uploaded_model.read()
    uploaded_model.seek(0)
    model = load_model_from_bytes(b)
    if model is None:
        st.error("Failed to load uploaded model. Ensure it's a valid scikit-learn model or Pipeline.")
    else:
        st.success("Model loaded successfully from upload!")

st.markdown("---")
st.subheader("Enter Patient Features")

# -------------------------------------------------------
# INPUT FIELDS
# -------------------------------------------------------
col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Gender (0=female,1=male)", [0,1])
    height = st.number_input("Height (cm)", min_value=50, max_value=250, value=165)
    weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=70.0)
    ap_hi = st.number_input("Systolic BP (ap_hi)", min_value=50, max_value=300, value=120)

with col2:
    ap_lo = st.number_input("Diastolic BP (ap_lo)", min_value=30, max_value=200, value=80)
    cholesterol = st.selectbox("Cholesterol (1=normal,2=above,3=well above)", [1,2,3])
    gluc = st.selectbox("Glucose (1=normal,2=above,3=well above)", [1,2,3])
    smoke = st.selectbox("Smoker (0=no,1=yes)", [0,1])

col3, col4 = st.columns(2)
with col3:
    alco = st.selectbox("Alcohol (0=no,1=yes)", [0,1])
    active = st.selectbox("Active (0=no,1=yes)", [0,1])

with col4:
    Age_Year = st.number_input("Age (years)", min_value=1, max_value=120, value=40)

# -------------------------------------------------------
# Prediction
# -------------------------------------------------------

if st.button("Predict"):
    if model is None:
        st.error("❌ No model loaded. Place model1.pkl in the folder or upload it above.")
    elif ap_lo > ap_hi:
        st.error("❌ ap_lo cannot be greater than ap_hi.")
    else:
        X = np.array([[gender, height, weight, ap_hi, ap_lo,
                       cholesterol, gluc, smoke, alco, active, Age_Year]], dtype=float)

        try:
            pred = model.predict(X)
            proba = None

            if hasattr(model, "predict_proba"):
                try:
                    proba = model.predict_proba(X)[0]
                except:
                    proba = None

            label = int(pred[0])
            st.success(f"Predicted cardio: **{label}**  (0 = No, 1 = Yes)")

            if proba is not None:
                p1 = proba[1] if len(proba) > 1 else proba[0]
                st.info(f"Probability cardio=1: **{p1:.3f}**")
                st.progress(float(p1))

        except Exception as e:
            st.error(f"Prediction failed: {e}")

st.markdown("---")
st.caption("This version uses only `model1.pkl`. No scaler upload. If scaling was used, include it inside a Pipeline before saving.")
