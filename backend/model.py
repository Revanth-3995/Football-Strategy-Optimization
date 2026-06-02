import os
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report

MODEL_PATH = "outputs/model.pkl"
COLUMNS_PATH = "outputs/model_columns.pkl"

def train_model(X_train, y_train) -> RandomForestClassifier:
    """
    Train RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced').
    Save trained model to MODEL_PATH using joblib.dump.
    Save X_train.columns.tolist() to COLUMNS_PATH.
    Return the trained model.
    """
    model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    joblib.dump(X_train.columns.tolist(), COLUMNS_PATH)

    return model

def evaluate_model(model, X_test, y_test) -> dict:
    """
    Return dict with keys: accuracy, precision, recall, f1, report_text.
    Use sklearn.metrics functions with zero_division=0.
    Round accuracy/precision/recall/f1 to 4 decimal places.
    report_text = classification_report(y_test, y_pred) as a string.
    """
    y_pred = model.predict(X_test)

    return {
        "accuracy": round(accuracy_score(y_test, y_pred), 4),
        "precision": round(precision_score(y_test, y_pred, zero_division=0), 4),
        "recall": round(recall_score(y_test, y_pred, zero_division=0), 4),
        "f1": round(f1_score(y_test, y_pred, zero_division=0), 4),
        "report_text": classification_report(y_test, y_pred, zero_division=0)
    }

def get_feature_importance(model, feature_names: list) -> list[dict]:
    """
    Return list of dicts sorted by importance descending:
    [{"feature": "location_x", "importance": 0.281}, ...]
    Round importance to 4 decimal places.
    """
    importances = model.feature_importances_

    feature_imp = [
        {"feature": name, "importance": round(imp, 4)}
        for name, imp in zip(feature_names, importances)
    ]

    return sorted(feature_imp, key=lambda x: x["importance"], reverse=True)

def predict_press_success(model, feature_row: dict, training_columns: list) -> dict:
    """
    Given a single observation as a dict and the training column list,
    return {"probability": float, "prediction": int}.
    Must align columns with training_columns (add missing dummies as 0).
    """
    df = pd.DataFrame([feature_row])

    # Needs a dummy encoding step manually because pd.get_dummies wouldn't know the categories
    # So first let's just pd.get_dummies then align
    df_dummies = pd.get_dummies(df)

    # Align
    for col in training_columns:
        if col not in df_dummies.columns:
            df_dummies[col] = 0

    # Ensure exact same order
    X = df_dummies[training_columns]

    prob = model.predict_proba(X)[0][1]
    pred = model.predict(X)[0]

    return {
        "probability": float(prob),
        "prediction": int(pred)
    }

def load_model():
    """
    Load model from MODEL_PATH and columns from COLUMNS_PATH.
    If files don't exist, raise FileNotFoundError with message:
    'Model not trained yet. POST /api/train first.'
    """
    if not os.path.exists(MODEL_PATH) or not os.path.exists(COLUMNS_PATH):
        raise FileNotFoundError("Model not trained yet. POST /api/train first.")

    model = joblib.load(MODEL_PATH)
    columns = joblib.load(COLUMNS_PATH)

    return model, columns
