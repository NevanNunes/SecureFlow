from flask import Blueprint, render_template, request, jsonify, current_app
from app.models import fraud_model
from app.utils import validate_transaction_data, allowed_file
import pandas as pd
import os

main = Blueprint('main', __name__)


@main.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@main.route('/predict-page')
def predict_page():
    """Prediction form page"""
    return render_template('predict.html')


@main.route('/dashboard')
def dashboard():
    """Analytics dashboard"""
    return render_template('dashboard.html')


@main.route('/api/predict', methods=['POST'])
def predict():
    """API endpoint for single transaction prediction"""
    try:
        data = request.get_json()

        # Validate input
        is_valid, message = validate_transaction_data(data)
        if not is_valid:
            return jsonify({'error': message}), 400

        # Make prediction
        result = fraud_model.predict(data)

        current_app.logger.info(f'Prediction made: {result}')

        return jsonify({
            'success': True,
            'result': result,
            'transaction_data': data
        }), 200

    except Exception as e:
        current_app.logger.error(f'Prediction error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@main.route('/api/predict-batch', methods=['POST'])
def predict_batch():
    """API endpoint for batch prediction (CSV upload)"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file format. Only CSV allowed'}), 400

        # Read CSV
        df = pd.read_csv(file)

        # Make batch predictions
        results = fraud_model.predict_batch(df)

        # Add results to dataframe
        df['prediction'] = [r['is_fraud'] for r in results]
        df['fraud_probability'] = [r['fraud_probability'] for r in results]
        df['risk_level'] = [r['risk_level'] for r in results]

        return jsonify({
            'success': True,
            'total_transactions': len(df),
            'fraud_detected': sum(df['prediction']),
            'results': results[:100]  # Return first 100 for display
        }), 200

    except Exception as e:
        current_app.logger.error(f'Batch prediction error: {str(e)}')
        return jsonify({'error': str(e)}), 500


@main.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model_loaded': fraud_model.model is not None
    }), 200


@main.route('/api/stats', methods=['GET'])
def get_stats():
    """Get model statistics"""
    # This would typically come from a database
    # For now, return mock data
    return jsonify({
        'total_predictions': 10523,
        'fraud_detected': 127,
        'accuracy': 0.9876,
        'last_update': '2024-12-06'
    }), 200