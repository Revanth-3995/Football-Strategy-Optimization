import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from backend.model import train_model, evaluate_model, get_feature_importance

def test_train_model():
    X_train = pd.DataFrame({'f1': [1, 0, 1, 0], 'f2': [0, 1, 0, 1]})
    y_train = pd.Series([1, 0, 1, 0])

    model = train_model(X_train, y_train)
    assert isinstance(model, RandomForestClassifier)

def test_evaluate_model():
    X_train = pd.DataFrame({'f1': [1, 0, 1, 0], 'f2': [0, 1, 0, 1]})
    y_train = pd.Series([1, 0, 1, 0])
    model = train_model(X_train, y_train)

    metrics = evaluate_model(model, X_train, y_train)
    assert 'accuracy' in metrics
    assert 'precision' in metrics
    assert 'recall' in metrics
    assert 'f1' in metrics
    assert 'report_text' in metrics

def test_get_feature_importance():
    X_train = pd.DataFrame({'f1': [1, 0, 1, 0], 'f2': [0, 1, 0, 1]})
    y_train = pd.Series([1, 0, 1, 0])
    model = train_model(X_train, y_train)

    importances = get_feature_importance(model, ['f1', 'f2'])
    assert len(importances) == 2

    # Check it's sorted descending
    assert importances[0]['importance'] >= importances[1]['importance']
