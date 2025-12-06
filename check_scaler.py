import pickle
import sys

scaler_path = r'd:/Fraud_app/models/scaler.pkl'

try:
    with open(scaler_path, 'rb') as f:
        scaler = pickle.load(f)
    
    if hasattr(scaler, 'feature_names_in_'):
        with open('scaler_features.txt', 'w') as f_out:
            for name in scaler.feature_names_in_:
                f_out.write(f"{name}\n")
        print("Features written to scaler_features.txt")
    else:
        print("Scaler has no feature_names_in_")

except Exception as e:
    print(f"Error: {e}")
