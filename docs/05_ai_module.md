# 05 - AI module
* **Model:** TF-IDF (1-2 grams) + Logistic Regression, trained on a small hand-written demo dataset (`ai/dataset/news.csv`).
* **Rule signals:** capital letters, exclamation marks, clickbait phrases, vague sources, conspiracy wording; credible-source phrases reduce the score.
* **Fact verification:** TF-IDF cosine similarity (threshold 0.35, configurable) between the post and `knowledge_base.claim`.
  Results: TRUE / FALSE / MISLEADING from the matched record, otherwise **UNVERIFIED** (never auto-FALSE).
  Negation mismatch (post negates a known claim) -> UNVERIFIED for human review.
* **Risk score** = 45% ML + 35% fact risk (TRUE 0, UNVERIFIED .3, MISLEADING .7, FALSE 1) + 20% rules. Known-FALSE match => at least 65.
* **Explainability:** every analysis stores a list of reasons shown in the "AI Analysis" panel.
* **Feedback loop:** moderator decisions -> `feedback_dataset` (AI label vs human decision). Retraining is manual and controlled.
* **Optional external API:** Google Fact Check Tools when `DEMO_MODE=false` and `FACT_CHECK_API_KEY` is set.
* **Limits:** tiny dataset; high hold-out score on it is not meaningful; probabilistic output; media analysis = validation + optional OCR only.
