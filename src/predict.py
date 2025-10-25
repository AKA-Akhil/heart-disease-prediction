# src/predict.py
import streamlit as st
import joblib
import numpy as np
import os

MODEL_PATH = "models/model-latest.joblib"

st.set_page_config(page_title="Heart Disease Predictor", layout="centered")

st.title("Heart Disease Prediction")
st.markdown("Fill the fields below (use typical clinical values). The model is a RandomForest trained on a heart disease dataset.")

# Left column: Demographics
st.header("Demographics")
age = st.number_input("Age (years)", min_value=1, max_value=120, value=55)
sex = st.selectbox("Sex", ("Male", "Female"))

# Middle column: Vitals / Symptoms
st.header("Symptoms & Vitals")
cp = st.selectbox("Chest pain type (1-4)", (1,2,3,4))
trestbps = st.number_input("Resting blood pressure (mm Hg)", min_value=50, max_value=250, value=130)
chol = st.number_input("Serum cholesterol (mg/dl)", min_value=50, max_value=600, value=250)
fbs = st.selectbox("Fasting blood sugar > 120 mg/dl", ("No","Yes"))

# Right column: ECG / Exercise
st.header("ECG & Exercise")
restecg = st.selectbox("Resting ECG results (0-2)", (0,1,2))
thalach = st.number_input("Max heart rate achieved", min_value=50, max_value=250, value=150)
exang = st.selectbox("Exercise induced angina", ("No","Yes"))

# Additional features: for minimal model we will set defaults if not present in dataset
oldpeak = st.number_input("ST depression (oldpeak)", value=1.0, format="%.1f")
slope = st.selectbox("Slope of peak exercise ST segment (0-2)", (0,1,2))
ca = st.selectbox("Number of major vessels colored by fluoroscopy (0-4)", (0,1,2,3,4))
thal = st.selectbox("Thalassemia (1 = normal; 2 = fixed defect; 3 = reversible defect)", (1,2,3))

# Predict button
if st.button("Predict"):
    # load model
    if not os.path.exists(MODEL_PATH):
        st.error("Model not found. Run training (python src/train.py) to generate models/model-latest.joblib.")
    else:
        data = joblib.load(MODEL_PATH)
        model = data["model"]
        # Construct feature vector consistent with training preprocess:
        sex_num = 1 if sex == "Male" else 0
        fbs_num = 1 if fbs == "Yes" else 0
        exang_num = 1 if exang == "Yes" else 0

        # Order of features: we select numeric columns from training df,
        # but to keep simple, assume model trained on common features:
        X = np.array([[age, sex_num, cp, trestbps, chol, fbs_num, restecg, thalach, exang_num, oldpeak, slope, ca, thal]])
        try:
            pred = model.predict(X)
            proba = model.predict_proba(X) if hasattr(model, "predict_proba") else None
            label = "Likely Heart Disease" if pred[0] == 1 else "Unlikely Heart Disease"
            st.subheader("Result")
            st.write(label)
            if proba is not None:
                st.write(f"Confidence (no disease / disease): {proba[0][0]:.2f} / {proba[0][1]:.2f}")
        except Exception as e:
            st.error(f"Failed to predict: {e}")
