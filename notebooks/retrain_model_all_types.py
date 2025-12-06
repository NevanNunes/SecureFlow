"""
Complete Fraud Detection Model Retraining Script
This script trains the model with ALL 5 transaction types to fix the LabelEncoder error
"""

import numpy as np
import pandas as pd
import pickle
import warnings
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, f1_score, accuracy_score
from lightgbm import LGBMClassifier
from imblearn.over_sampling import SMOTE
from collections import Counter

warnings.filterwarnings('ignore')

print("="*80)
print("FRAUD DETECTION MODEL RETRAINING - ALL TRANSACTION TYPES")
print("="*80)

# ============================================================================
# STEP 1: LOAD DATA
# ============================================================================
print("\n[1/8] Loading dataset...")
df = pd.read_csv('PS_20174392719_1491204439457_log.csv')
print(f"✓ Dataset loaded: {df.shape[0]:,} rows, {df.shape[1]} columns")

# Check transaction types in dataset
print(f"\nTransaction types in dataset:")
print(df['type'].value_counts())

# ============================================================================
# STEP 2: FEATURE ENGINEERING
# ============================================================================
print("\n[2/8] Creating features...")

# Create engineered features
df['origBalanceDiff'] = df['oldbalanceOrg'] - df['newbalanceOrig']
df['destBalanceDiff'] = df['oldbalanceDest'] - df['newbalanceDest']
df['origBalanceError'] = df['amount'] - df['origBalanceDiff']
df['destBalanceError'] = df['amount'] + df['destBalanceDiff']
df['origBalanceZero'] = (df['oldbalanceOrg'] == 0).astype(int)
df['destBalanceZero'] = (df['oldbalanceDest'] == 0).astype(int)
df['day'] = df['step'] // 24
df['hour'] = df['step'] % 24

print("✓ Features created: origBalanceDiff, destBalanceDiff, origBalanceError,")
print("  destBalanceError, origBalanceZero, destBalanceZero, day, hour")

# ============================================================================
# STEP 3: ENCODE TRANSACTION TYPES - ALL 5 TYPES
# ============================================================================
print("\n[3/8] Encoding transaction types...")

# Create LabelEncoder for ALL 5 transaction types
label_encoder = LabelEncoder()

# Explicitly fit on all 5 types to ensure they're all included
all_transaction_types = ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'CASH_IN']
label_encoder.fit(all_transaction_types)

# Transform the transaction type column
df['type_encoded'] = label_encoder.transform(df['type'])

print("✓ LabelEncoder trained on ALL transaction types:")
for i, trans_type in enumerate(label_encoder.classes_):
    print(f"  {trans_type} → {i}")

# ============================================================================
# STEP 4: PREPARE FEATURES AND TARGET
# ============================================================================
print("\n[4/8] Preparing features and target...")

# Drop unnecessary columns
columns_to_drop = ['nameOrig', 'nameDest', 'isFlaggedFraud', 'type']
df_processed = df.drop(columns=columns_to_drop, errors='ignore')

# Separate features and target
X = df_processed.drop('isFraud', axis=1)
y = df_processed['isFraud']

print(f"✓ Features shape: {X.shape}")
print(f"✓ Target distribution: Non-Fraud={Counter(y)[0]:,}, Fraud={Counter(y)[1]:,}")
print(f"✓ Fraud rate: {(Counter(y)[1]/len(y)*100):.4f}%")

# ============================================================================
# STEP 5: TRAIN-TEST SPLIT
# ============================================================================
print("\n[5/8] Splitting data...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"✓ Training set: {X_train.shape[0]:,} samples")
print(f"✓ Test set: {X_test.shape[0]:,} samples")

# ============================================================================
# STEP 6: FEATURE SCALING
# ============================================================================
print("\n[6/8] Scaling features...")

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("✓ Features scaled using StandardScaler")

# ============================================================================
# STEP 7: HANDLE CLASS IMBALANCE WITH SMOTE
# ============================================================================
print("\n[7/8] Handling class imbalance with SMOTE...")

print(f"Before SMOTE: {Counter(y_train)}")
smote = SMOTE(random_state=42, k_neighbors=5)
X_train_balanced, y_train_balanced = smote.fit_resample(X_train_scaled, y_train)
print(f"After SMOTE:  {Counter(y_train_balanced)}")
print("✓ Classes balanced")

# ============================================================================
# STEP 8: TRAIN LIGHTGBM MODEL
# ============================================================================
print("\n[8/8] Training LightGBM model...")

lgbm = LGBMClassifier(
    random_state=42,
    n_estimators=100,
    max_depth=7,
    class_weight='balanced',
    learning_rate=0.1,
    verbose=-1
)

lgbm.fit(X_train_balanced, y_train_balanced)
print("✓ LightGBM model trained")

# ============================================================================
# EVALUATE MODEL
# ============================================================================
print("\n" + "="*80)
print("MODEL EVALUATION")
print("="*80)

y_pred = lgbm.predict(X_test_scaled)
y_pred_proba = lgbm.predict_proba(X_test_scaled)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred)

print(f"\nAccuracy: {accuracy:.4f}")
print(f"F1-Score: {f1:.4f}")

print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=['Non-Fraud', 'Fraud']))

print("\nConfusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(f"True Negatives:  {cm[0][0]:,}")
print(f"False Positives: {cm[0][1]:,}")
print(f"False Negatives: {cm[1][0]:,}")
print(f"True Positives:  {cm[1][1]:,}")

# ============================================================================
# SAVE MODEL, SCALER, AND ENCODER
# ============================================================================
print("\n" + "="*80)
print("SAVING MODEL FILES")
print("="*80)

# Save model
with open('best_fraud_detection_model_LightGBM.pkl', 'wb') as f:
    pickle.dump(lgbm, f)
print("✓ Model saved: best_fraud_detection_model_LightGBM.pkl")

# Save scaler
with open('scaler.pkl', 'wb') as f:
    pickle.dump(scaler, f)
print("✓ Scaler saved: scaler.pkl")

# Save label encoder
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)
print("✓ Label encoder saved: label_encoder.pkl")

# ============================================================================
# TEST WITH ALL 5 TRANSACTION TYPES
# ============================================================================
print("\n" + "="*80)
print("TESTING WITH ALL 5 TRANSACTION TYPES")
print("="*80)

print("\nVerifying LabelEncoder can handle all types:")
for trans_type in ['PAYMENT', 'TRANSFER', 'CASH_OUT', 'DEBIT', 'CASH_IN']:
    encoded = label_encoder.transform([trans_type])[0]
    print(f"  {trans_type:12s} → {encoded} ✓")

# ============================================================================
# FEATURE IMPORTANCE
# ============================================================================
print("\n" + "="*80)
print("TOP 10 MOST IMPORTANT FEATURES")
print("="*80)

feature_importance = pd.DataFrame({
    'Feature': X.columns,
    'Importance': lgbm.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n", feature_importance.head(10).to_string(index=False))

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("✅ RETRAINING COMPLETE!")
print("="*80)
print("\nWhat was fixed:")
print("  • LabelEncoder now supports ALL 5 transaction types")
print("  • Model retrained with complete feature engineering")
print("  • All pickle files updated and saved")
print("\nFiles saved in current directory:")
print("  1. best_fraud_detection_model_LightGBM.pkl")
print("  2. scaler.pkl")
print("  3. label_encoder.pkl")
print("\nYour Flask app should now work with all transaction types!")
print("="*80)

