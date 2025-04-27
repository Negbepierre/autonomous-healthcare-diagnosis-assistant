# dashboard_healthcare.py

import streamlit as st
import pandas as pd
import boto3
import gzip
import io
import json

# AWS S3 Config
BUCKET_NAME = "healthcare-diagnosis-negbepierre"
REGION = "eu-west-2"
PREFIX = "2025/04/27/01/"

# Load patient data from S3
s3 = boto3.client("s3", region_name=REGION)
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)

patient_records = []

for obj in response.get("Contents", []):
    key = obj["Key"]
    if key.endswith(".json.gz"):
        obj_data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        bytestream = io.BytesIO(obj_data["Body"].read())
        with gzip.GzipFile(fileobj=bytestream, mode="rb") as f:
            lines = f.read().decode("utf-8").splitlines()
            for line in lines:
                try:
                    patient_records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

# Convert to DataFrame
if patient_records:
    df = pd.DataFrame(patient_records)
else:
    df = pd.DataFrame()

# Streamlit App
st.set_page_config(page_title="🏥 Healthcare Diagnosis Assistant", layout="wide")
st.title("🏥 Healthcare Diagnosis Assistant")

if df.empty:
    st.warning("No patient data found.")
else:
    st.subheader("📋 All Patient Records")
    st.dataframe(df)

    # Simple diagnosis function
    def diagnose(symptoms):
        symptoms = symptoms.lower()
        if "fever" in symptoms and "chest pain" in symptoms:
            return "Possible Pneumonia"
        elif "sore throat" in symptoms and "fatigue" in symptoms:
            return "Possible Viral Infection"
        elif "joint pain" in symptoms:
            return "Possible Arthritis"
        elif "muscle pain" in symptoms and "headache" in symptoms:
            return "Possible Dengue Fever"
        elif "unconsciousness" in symptoms:
            return "Possible Stroke or Severe Infection"
        else:
            return "Further Tests Required"

    # Apply diagnosis
    df["diagnosis"] = df["symptoms"].apply(diagnose)

    st.subheader("🩺 Diagnosed Patients")
    st.dataframe(df[["patient_id", "symptoms", "diagnosis"]])

    # Highlight critical patients (unconsciousness, chest pain, etc.)
    critical = df[df["symptoms"].str.contains("chest pain|unconsciousness|shortness of breath", case=False, na=False)]

    st.subheader("🚨 Critical Cases")
    if not critical.empty:
        st.dataframe(critical[["patient_id", "symptoms", "diagnosis"]])
    else:
        st.info("✅ No critical cases detected.")
