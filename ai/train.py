"""Train TF-IDF + Logistic Regression. Run from repo root:  python -m ai.train"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from ai.preprocessing import clean_text

BASE = Path(__file__).resolve().parent
DATASET = BASE / "dataset" / "news.csv"
MODEL = BASE / "model" / "model.joblib"
METRICS = BASE / "model" / "metrics.json"
VERSION = "tfidf-logreg-0.1-prototype"


def build_pipeline():
    return Pipeline([
        ("tfidf", TfidfVectorizer(preprocessor=clean_text, ngram_range=(1, 2), stop_words="english", sublinear_tf=True)),
        ("clf", LogisticRegression(max_iter=1000, class_weight="balanced", C=2.0)),
    ])


def train(verbose=True):
    df = pd.read_csv(DATASET).dropna()
    y = (df["label"] == "fake").astype(int)
    X_tr, X_te, y_tr, y_te = train_test_split(df["text"], y, test_size=0.25, random_state=42, stratify=y)
    pipe = build_pipeline().fit(X_tr, y_tr)
    acc = accuracy_score(y_te, pipe.predict(X_te))
    if verbose:
        print(classification_report(y_te, pipe.predict(X_te), target_names=["real", "fake"]))
        print(f"Hold-out accuracy: {acc:.2f} on {len(X_te)} samples (tiny demo dataset!)")
    final = build_pipeline().fit(df["text"], y)  # refit on all data for the shipped model
    MODEL.parent.mkdir(exist_ok=True)
    joblib.dump({"pipeline": final, "version": VERSION}, MODEL)
    METRICS.write_text(json.dumps({"holdout_accuracy": round(acc, 3), "samples": int(len(df)),
                                   "version": VERSION, "note": "Academic prototype, tiny dataset."}, indent=2))
    return acc


if __name__ == "__main__":
    train()
