import sys
import os
from flask import Flask, current_app

# Add project root to path
sys.path.append(os.getcwd())

from app.models import FraudDetectionModel

app = Flask(__name__)
app.config['MODEL_PATH'] = r'd:/Fraud_app/models/best_fraud_detection_model_LightGBM.pkl'
app.config['SCALER_PATH'] = r'd:/Fraud_app/models/scaler.pkl'
app.config['ENCODER_PATH'] = r'd:/Fraud_app/models/label_encoder.pkl'

# Mock transaction data
data = {
    "step": 1,
    "type": "PAYMENT",
    "amount": 9839.64,
    "oldbalanceOrg": 170136.0,
    "newbalanceOrig": 160296.36,
    "oldbalanceDest": 0.0,
    "newbalanceDest": 0.0
}

with app.app_context():
    model = FraudDetectionModel()
    model.load_models() # Ensure loaded
    print("Scaler expected features:", model.scaler.feature_names_in_)
    try:
        result = model.predict(data)
        print("Prediction successful!")
        print(result)
    except Exception as e:
        print(f"Prediction error: {e}")
        # Print full traceback if needed
        import traceback
        traceback.print_exc()
