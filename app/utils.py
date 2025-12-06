from flask import current_app


def validate_transaction_data(data):
    """Validate transaction data"""
    required_fields = [
        'step', 'type', 'amount', 'oldbalanceOrg',
        'newbalanceOrig', 'oldbalanceDest', 'newbalanceDest'
    ]

    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f'Missing required field: {field}'

    # Validate transaction type
    valid_types = ['CASH_OUT', 'TRANSFER']
    if data['type'] not in valid_types:
        return False, f'Invalid transaction type. Must be one of: {valid_types}'

    # Validate numeric fields
    numeric_fields = ['step', 'amount', 'oldbalanceOrg', 'newbalanceOrig',
                      'oldbalanceDest', 'newbalanceDest']

    for field in numeric_fields:
        try:
            float(data[field])
        except (ValueError, TypeError):
            return False, f'{field} must be a numeric value'

    # Validate positive values
    if data['amount'] <= 0:
        return False, 'Amount must be greater than 0'

    return True, 'Valid'


def allowed_file(filename):
    """Check if file extension is allowed"""
    allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'csv'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions