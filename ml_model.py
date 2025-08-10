# ml_model.py
"""
ML model for predicting next-day stock movement based on Strategy 2,
using only the most relevant features from EDA.
"""

import logging
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, balanced_accuracy_score, classification_report
from collections import Counter

# Based on feature importance & correlation analysis from EDA
FEATURE_COLUMNS = ["RSI", "SMA20", "SMA50", "MACD", "MACD_SIGNAL", "Volume"]

def prepare_ml_data(df):
    """
    Prepare features and labels for ML training using Strategy 2 rules:
      BUY (1): RSI < 30 AND SMA20 > SMA50
      SELL (-1): RSI > 70 AND SMA20 < SMA50
    """
    df = df.copy()

    # Generate labels
    buy_cond = (df["RSI"] < 30) & (df["SMA20"] > df["SMA50"])
    sell_cond = (df["RSI"] > 70) & (df["SMA20"] < df["SMA50"])

    df["Label"] = 0
    df.loc[buy_cond, "Label"] = 1
    df.loc[sell_cond, "Label"] = -1

    # Select features
    X = df[FEATURE_COLUMNS].copy().ffill().fillna(0)
    y = df["Label"]

    # Remove non-signal rows (Label == 0)
    mask = y != 0
    X, y = X[mask], y[mask]

    return X, y

def train_model(df):
    """
    Train Decision Tree model based on filtered strategy signals.
    Returns: model, balanced_accuracy, next_signal
    """
    X, y = prepare_ml_data(df)

    if X.empty:
        logging.warning("⚠️ No BUY/SELL signals found in dataset for training.")
        return None, 0, None

    # Train-test split (time-series safe: no shuffling)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, shuffle=False
    )

    # Model: Simple & interpretable
    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X_train, y_train)

    # Predictions & metrics
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    bal_acc = balanced_accuracy_score(y_test, y_pred)

    logging.info(f"📊 Accuracy: {acc*100:.2f}% | Balanced Accuracy: {bal_acc*100:.2f}%")
    logging.info(f"📊 Test Set Class Distribution: {Counter(y_test)}")
    logging.info("\n" + classification_report(y_test, y_pred, digits=2))

    # Predict next-day movement
    next_signal = predict_next_day(model, df.iloc[-1])

    return model, bal_acc, next_signal

def predict_next_day(model, last_row):
    """
    Predict next-day BUY/SELL signal based on last available indicators.
    """
    X_last = last_row[FEATURE_COLUMNS].ffill().fillna(0).values.reshape(1, -1)
    pred = model.predict(X_last)[0]
    return "BUY" if pred == 1 else "SELL"

