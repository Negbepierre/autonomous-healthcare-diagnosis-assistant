# diagnose_patient.py

import pandas as pd
import boto3
import gzip
import io
import json

# AWS S3 Config
BUCKET_NAME = "healthcare-diagnosis-negbepierre"   # your bucket name
REGION = "eu-west-2"                               # your AWS region (London)
PREFIX = "2025/04/27/01/"                           # folder path where your sample_patients.json.gz is stored

# Load patient data from S3
s3 = boto3.client("s3", region_name=REGION)
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)

patients = []

# Read .json.gz file
for obj in response.get("Contents", []):
    key = obj["Key"]
    if key.endswith(".json.gz"):
        obj_data = s3.get_object(Bucket=BUCKET_NAME, Key=key)
        bytestream = io.BytesIO(obj_data["Body"].read())
        with gzip.GzipFile(fileobj=bytestream, mode="rb") as f:
            lines = f.read().decode("utf-8").splitlines()
            for line in lines:
                try:
                    patients.append(json.loads(line))
                except json.JSONDecodeError:
                    pass

# Convert to DataFrame
if patients:
    df = pd.DataFrame(patients)
else:
    df = pd.DataFrame()

# Check if important fields exist
if not df.empty and all(col in df.columns for col in ["patient_id", "symptoms", "age", "gender", "medical_history"]):
    print(df.head())

    # Simple diagnosis logic
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

    # Apply diagnosis to each patient
    df["diagnosis"] = df["symptoms"].apply(diagnose)

    # Print diagnosed patients
    print("\n✅ Diagnosed Patients:")
    print(df[["patient_id", "symptoms", "diagnosis"]])

else:
    print("❌ Required fields missing in patient data. Please check your sample_patients.json.gz file.")
