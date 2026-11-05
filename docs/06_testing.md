# 06 - Testing
* `tests/test_ai.py` - preprocessing, prediction shape, heuristics, fact statuses (incl. UNVERIFIED and negation), risk ordering.
* `backend/tests/test_api.py` - registration, duplicate/invalid input, login, protected routes (missing/invalid token), AI analysis,
  fact verification, create post (safe vs risky, hidden from public feed), upload validation (type, size), reports (+duplicate, role check),
  admin authorization, approve/block + notification + feedback dataset, report review, knowledge-base CRUD.
* Backend tests use a temporary SQLite database (same SQLAlchemy models); the app itself targets PostgreSQL.

Run: `python -m pytest tests/test_ai.py` (repo root) and `cd backend && python -m pytest tests -v`.
Manual end-to-end checklist: register -> login -> create safe/risky post -> view AI analysis -> report -> login as admin -> review report ->
approve/block -> check user notification -> check logs.
Frontend automated tests are not included in this prototype.
