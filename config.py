import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    basedir = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    MODEL_PATH = os.path.join(basedir, 'models', 'best_fraud_detection_model_LightGBM.pkl')
    SCALER_PATH = os.path.join(basedir, 'models', 'scaler.pkl')
    ENCODER_PATH = os.path.join(basedir, 'models', 'label_encoder.pkl')
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'csv', 'json'}

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}