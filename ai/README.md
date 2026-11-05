# TruthShield AI - AI module (academic prototype)

| File | Purpose |
|---|---|
| `preprocessing.py` | text cleaning + transparent rule-based signals (clickbait, caps, vague sources...) |
| `train.py` | trains **TF-IDF + Logistic Regression** on `dataset/news.csv` -> `model/model.joblib` |
| `predict.py` | returns `label`, `fake_probability`, `real_probability`, `confidence` |
| `fact_check.py` | TF-IDF cosine match against the knowledge base -> TRUE / FALSE / MISLEADING / UNVERIFIED |
| `analyzer.py` | combines everything into one explainable risk score (0-100) |

```
python -m ai.train        # run from the repository root
```

**Risk score** = 45% ML fake probability + 35% fact-check risk + 20% rule signals.
A claim that matches a known FALSE record is floored at 65 (always human review); a TRUE match is capped at 40.

## Honest limitations
* The sample dataset has only ~90 short, hand-written sentences. The model mostly learns *writing style*
  (sensational vs neutral), not truth. The 100% hold-out score printed by `train.py` is **meaningless**
  on such a tiny, easy dataset - do not quote it as accuracy.
* The fact check only knows claims in the knowledge base. Unknown claim => **UNVERIFIED**, never automatically FALSE.
* A post that *negates* a known claim ("vaccines do NOT cause autism") is sent to UNVERIFIED for human review
  instead of being judged automatically.
* Predictions are probabilistic. Human moderators make the final decision.
* Feedback loop: moderator decisions are stored in the `feedback_dataset` table (export CSV from the admin API).
  Retraining is manual and controlled - the model is never retrained automatically.
