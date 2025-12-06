import pickle
import numpy as np
import pandas as pd
from flask import current_app
import os
import logging


class FraudDetectionModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self._initialized = False

    def _ensure_loaded(self):
        """Lazy load models when first needed"""
        if not self._initialized:
            self.load_models()
            self._initialized = True

    def load_models(self):
        """Load the trained model, scaler, and encoder"""
        try:
            model_path = current_app.config['MODEL_PATH']
            scaler_path = current_app.config['SCALER_PATH']
            encoder_path = current_app.config['ENCODER_PATH']

            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)

            with open(scaler_path, 'rb') as f:
                self.scaler = pickle.load(f)

            with open(encoder_path, 'rb') as f:
                self.encoder = pickle.load(f)

            current_app.logger.info('Models loaded successfully')
        except Exception as e:
            logging.error(f'Error loading models: {str(e)}')
            raise

    def preprocess_transaction(self, transaction_data):
        """Preprocess transaction data for prediction"""
        df = pd.DataFrame([transaction_data])

        # Feature engineering (same as training)
        df['origBalanceDiff'] = df['oldbalanceOrg'] - df['newbalanceOrig']
        df['destBalanceDiff'] = df['oldbalanceDest'] - df['newbalanceDest']
        df['origBalanceError'] = df['amount'] - df['origBalanceDiff']
        df['destBalanceError'] = df['amount'] + df['destBalanceDiff']
        df['origBalanceZero'] = (df['oldbalanceOrg'] == 0).astype(int)
        df['destBalanceZero'] = (df['oldbalanceDest'] == 0).astype(int)
        df['day'] = df['step'] // 24
        df['hour'] = df['step'] % 24

        # Encode transaction type
        df['type'] = self.encoder.transform(df['type'])

        # Ensure columns are in the correct order for the scaler
        expected_columns = [
            'step', 'type', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
            'oldbalanceDest', 'newbalanceDest', 'origBalanceDiff', 'destBalanceDiff',
            'origBalanceError', 'destBalanceError', 'origBalanceZero', 'destBalanceZero',
            'day', 'hour'
        ]
        df = df[expected_columns]

        return df

    def predict(self, transaction_data):
        """Make prediction on a single transaction"""
        self._ensure_loaded()
        try:
            # Preprocess
            df = self.preprocess_transaction(transaction_data)

            # Scale
            df_scaled = self.scaler.transform(df)

            # Predict
            prediction = self.model.predict(df_scaled)[0]
            probability = self.model.predict_proba(df_scaled)[0]

            result = {
                'is_fraud': bool(prediction),
                'fraud_probability': float(probability[1]),
                'confidence': float(max(probability)),
                'risk_level': self._get_risk_level(probability[1])
            }

            return result
        except Exception as e:
            current_app.logger.error(f'Prediction error: {str(e)}')
            raise

    def _get_risk_level(self, probability):
        """Determine risk level based on fraud probability"""
        if probability >= 0.8:
            return 'CRITICAL'
        elif probability >= 0.6:
            return 'HIGH'
        elif probability >= 0.4:
            return 'MEDIUM'
        elif probability >= 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'

    def predict_batch(self, transactions_df):
        """Make predictions on multiple transactions"""
        self._ensure_loaded()
        results = []
        for _, transaction in transactions_df.iterrows():
            result = self.predict(transaction.to_dict())
            results.append(result)
        return results


# Initialize model instance (but don't load models yet)
fraud_model = FraudDetectionModel()