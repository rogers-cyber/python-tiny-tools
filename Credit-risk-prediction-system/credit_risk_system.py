"""
CreditRiskPro v1.1
Enterprise Credit Risk Prediction System
Single-File | Industry-Style | Beginner-Friendly

Run modes:
1) python generate_sample_data.py
2) python credit_risk_system.py --mode train --data train_data.csv
"""

# =========================
# Imports
# =========================
import os
import sys
import argparse
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix

# =========================
# Configuration
# =========================
MODEL_PATH = "credit_risk_model.joblib"
DEFAULT_TRAIN_DATA = "train_data.csv"
DEFAULT_PREDICT_DATA = "new_applicants.csv"
TARGET_COL = "default"
RANDOM_STATE = 42


# =========================
# Utilities
# =========================
def log(msg):
    print(f"[CreditRiskPro] {msg}")


# =========================
# Validation
# =========================
def validate_dataset(df):
    if TARGET_COL not in df.columns:
        raise ValueError(f"Missing target column '{TARGET_COL}'")

    if df.empty:
        raise ValueError("Dataset is empty")


# =========================
# Preprocessing
# =========================
def build_preprocessor(df):
    numeric_features = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    numeric_features.remove(TARGET_COL)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features)
        ]
    )

    return preprocessor


# =========================
# Model
# =========================
def build_model():
    return LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE
    )


# =========================
# Training
# =========================
def train_model(data_path):
    log(f"Loading training data: {data_path}")
    df = pd.read_csv(data_path)

    validate_dataset(df)

    X = df.drop(columns=[TARGET_COL])
    y = df[TARGET_COL]

    preprocessor = build_preprocessor(df)
    model = build_model()

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.25,
        stratify=y,
        random_state=RANDOM_STATE
    )

    log("Training model...")
    pipeline.fit(X_train, y_train)

    log("Evaluating model...")
    probs = pipeline.predict_proba(X_test)[:, 1]
    preds = (probs >= 0.5).astype(int)

    print("\nAUC:", round(roc_auc_score(y_test, probs), 4))
    print("\nClassification Report:")
    print(classification_report(y_test, preds))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, preds))

    joblib.dump(pipeline, MODEL_PATH)
    log(f"Model saved → {MODEL_PATH}")


# =========================
# Prediction
# =========================
def predict(data_path):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError("Model not found. Train the model first.")

    log(f"Loading model: {MODEL_PATH}")
    pipeline = joblib.load(MODEL_PATH)

    log(f"Loading prediction data: {data_path}")
    df = pd.read_csv(data_path)

    probs = pipeline.predict_proba(df)[:, 1]

    results = df.copy()
    results["risk_score"] = probs
    results["risk_class"] = np.where(probs >= 0.5, "HIGH", "LOW")

    output_file = "credit_risk_predictions.csv"
    results.to_csv(output_file, index=False)

    log(f"Predictions saved → {output_file}")
    print(results[["risk_score", "risk_class"]].head())


# =========================
# Main Logic (FIXED)
# =========================
def main():
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("--mode", choices=["train", "predict"])
    parser.add_argument("--data")

    args, _ = parser.parse_known_args()

    # ---------- AUTO MODE ----------
    if args.mode is None:
        log("No arguments provided → Auto mode enabled")

        if not os.path.exists(MODEL_PATH):
            if not os.path.exists(DEFAULT_TRAIN_DATA):
                log(f"ERROR: '{DEFAULT_TRAIN_DATA}' not found")
                sys.exit(1)

            log("Model not found → Training new model")
            train_model(DEFAULT_TRAIN_DATA)
        else:
            if not os.path.exists(DEFAULT_PREDICT_DATA):
                log(f"ERROR: '{DEFAULT_PREDICT_DATA}' not found")
                sys.exit(1)

            log("Model found → Running prediction")
            predict(DEFAULT_PREDICT_DATA)

        return

    # ---------- MANUAL MODE ----------
    if not args.data:
        log("ERROR: --data is required when --mode is specified")
        sys.exit(1)

    if args.mode == "train":
        train_model(args.data)
    elif args.mode == "predict":
        predict(args.data)


# =========================
# Entry Point
# =========================
if __name__ == "__main__":
    main()
