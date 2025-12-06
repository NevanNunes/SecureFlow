import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    MODEL_PATH = os.path.join('models', 'best_fraud_detection_model_XGBoost.pkl')
    SCALER_PATH = os.path.join('models', 'scaler.pkl')
    ENCODER_PATH = os.path.join('models', 'label_encoder.pkl')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'csv', 'json'}