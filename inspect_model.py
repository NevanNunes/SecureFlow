import pickle
import pandas as pd
import os
import sys

model_path = r'd:/Fraud_app/models/best_fraud_detection_model_LightGBM.pkl'
scaler_path = r'd:/Fraud_app/models/scaler.pkl'
encoder_path = r'd:/Fraud_app/models/label_encoder.pkl'

print(f"Loading model from {model_path}...")
try:
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    print("Model loaded.")
    if hasattr(model, 'feature_name_'):
        print("Model feature names (LightGBM):")
        for name in model.feature_name_:
            print(f"- {name}")
except Exception as e:
    print(f"Error loading model: {e}")

print(f"\nLoading scaler from {scaler_path}...")
try:
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    print("Scaler loaded.")
    if hasattr(scaler, 'feature_names_in_'):
        print("Scaler expected features:")
        for name in scaler.feature_names_in_:
            print(f"- {name}")
except Exception as e:
    print(f"Error loading scaler: {e}")

print(f"\nLoading encoder from {encoder_path}...")
try:
    with open(encoder_path, 'rb') as f:
        encoder = pickle.load(f)
    print("Encoder loaded.")
    if hasattr(encoder, 'classes_'):
        print("Encoder known classes:")
        for cls in encoder.classes_:
            print(f"- '{cls}'")
    else:
        print("Encoder does not expose classes_.")
except Exception as e:
    print(f"Error loading encoder: {e}")
