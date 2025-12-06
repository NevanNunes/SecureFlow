import pickle
import numpy as np
import pandas as pd
from flask import current_app
import os
import logging
import shap


class FraudDetectionModel:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.encoder = None
        self.explainer = None
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

            # Initialize SHAP explainer (TreeExplainer is best for LightGBM/XGBoost)
            try:
                self.explainer = shap.TreeExplainer(self.model)
                current_app.logger.info('Models and SHAP explainer loaded successfully')
            except Exception as e:
                current_app.logger.warning(f'Could not initialize SHAP explainer: {e}')
                self.explainer = None

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
        if df['type'].dtype == 'object':
            df['type_encoded'] = self.encoder.transform(df['type'])
        
        # Ensure columns are in the correct order for the scaler
        expected_columns = [
            'step', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
            'oldbalanceDest', 'newbalanceDest', 'origBalanceDiff', 'destBalanceDiff',
            'origBalanceError', 'destBalanceError', 'origBalanceZero', 'destBalanceZero',
            'day', 'hour', 'type_encoded'
        ]
        
        # Add missing columns if any
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0

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
            fraud_prob = probability[1]

            # Calculate SHAP values
            reasons = []
            if self.explainer:
                try:
                    shap_values = self.explainer.shap_values(df_scaled)
                    
                    if isinstance(shap_values, list):
                        sv = shap_values[1][0]
                    else:
                        if len(shap_values.shape) > 1:
                            sv = shap_values[0]
                        else:
                            sv = shap_values

                    feature_names = df.columns.tolist()
                    
                    for i, feature in enumerate(feature_names):
                        reasons.append({
                            "feature": feature,
                            "impact": float(sv[i])
                        })
                    
                    reasons.sort(key=lambda x: abs(x['impact']), reverse=True)
                    reasons = reasons[:3]
                except Exception as e:
                    current_app.logger.error(f"SHAP calculation error: {e}")
                    reasons = []

            result = {
                'risk_score': float(fraud_prob * 100),
                'fraud_probability': float(fraud_prob),
                'is_fraud': int(prediction),
                'risk_level': self._get_risk_level(fraud_prob),
                'reasons': reasons
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


# Initialize model instance (Global singleton)
fraud_model = FraudDetectionModel()