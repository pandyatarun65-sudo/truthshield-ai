# 🛡 TruthShield AI - Real-Time Fake News Prevention System

> **Academic prototype** (B.Tech CSE college project). Not a production social network and **not** a perfect
> fake-news detector. AI predictions are probabilistic; human moderation is required for ambiguous or high-impact content.

## Problem statement
On social media, misinformation spreads before anyone can check it. Most platforms react *after* a post goes viral.
TruthShield AI sits **in front of publication**: every new post is analysed first, scored for risk, and routed to
publish / warn / human review / block.

## Objectives
* Analyse a post *before* it becomes public (text + basic media checks).
* Explain every decision (explainable AI) and keep humans in the loop.
* Provide user, moderator and admin workflows with a full audit trail.
* Run completely locally (no paid API) in `DEMO_MODE`.

## Features
Auth (register / login / JWT / roles) · feed, search, like, comment, share simulation · create post with text/image/video/audio ·
ML + fact-check + rules risk engine · configurable decision thresholds · report system · moderator/admin panel
(dashboard, users, posts, reports, knowledge base CRUD, analytics, logs) · notifications · feedback dataset ·
file-upload validation · rate limiting · audit logs · Swagger (`/docs`) & ReDoc (`/redoc`).

## Architecture
```
React (Vite, Tailwind)  --REST/JSON-->  FastAPI  --SQLAlchemy-->  PostgreSQL
                                          |
                                          +--> ai/ (TF-IDF + LogReg, rules, fact check vs knowledge_base)
```
Post flow: `Create post -> AI analysis -> fact verification -> risk score -> decision engine ->
SAFE publish | WARNING publish+label | REVIEW moderator | HIGH RISK block + moderator -> DB + notification + audit log`.
Details and Mermaid diagrams: [`docs/`](docs).

## Technology stack
React 18, Vite, Tailwind CSS 3, Axios, React Router · Python 3.12, FastAPI, SQLAlchemy 2, Pydantic 2, PyJWT, bcrypt ·
**PostgreSQL** · scikit-learn, pandas, NumPy, OpenCV (+ optional Tesseract OCR) · Docker / Docker Compose.

## Folder structure
```
TruthShield-AI/
├── ai/            ML model, dataset, training, fact check, analyzer
├── backend/       FastAPI app (app/), requirements.txt, tests/
├── frontend/      React app (src/pages, src/components)
├── database/      schema.sql + notes
├── docs/          college documentation (8 files + diagrams)
├── tests/         AI module tests
├── docker/        Dockerfiles + nginx.conf
├── docker-compose.yml, render.yaml, .env.example, LICENSE
```

## Run with Docker (easiest)
```bash
cp .env.example .env        # optional; sensible defaults exist
docker compose up --build
```
* App: http://localhost:3000  · API docs: http://localhost:8000/docs
* PostgreSQL runs in a container (data kept in a Docker volume). Reset demo data: `docker compose down -v`.

## Run locally without Docker
Prerequisites: Python 3.11+, Node 18+, a PostgreSQL database (local, or free Neon/Supabase/Render).
```bash
# 1) database (example, local Postgres)
createdb truthshield     # or create a DB + user of your choice

# 2) backend
cp .env.example .env     # then edit DATABASE_URL and JWT_SECRET (the backend reads .env automatically)
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000              # the AI model trains itself on first use (or: cd .. && python -m ai.train)

# 3) frontend (new terminal)
cd frontend && npm install && npm run dev                # http://localhost:5173 (proxies /api to :8000)
```
Tables are created and demo data is seeded automatically on the first start.

## Environment variables
See [`.env.example`](.env.example). Key ones: `DATABASE_URL`, `JWT_SECRET` (**required in production**), `FRONTEND_URL` (CORS),
`DEMO_MODE`, `FACT_CHECK_API_KEY` (optional), `SAFE_MAX` / `WARNING_MAX` / `REVIEW_MAX` (decision thresholds), `MAX_UPLOAD_MB`.
Frontend: `VITE_API_URL` (only when the API is on another domain).

## Demo credentials (fictional, local use only)
| Role | Email | Password |
|---|---|---|
| Admin | admin@truthshield.demo | Admin@12345 |
| Moderator | moderator@truthshield.demo | Mod@12345 |
| Users | alice@ / bob@ / carol@ / dave@truthshield.demo | User@12345 |

Change or delete these accounts before any public deployment.

## API documentation
Interactive docs at `/docs` (Swagger) and `/redoc`. Endpoint list: [`docs/04_api_documentation.md`](docs/04_api_documentation.md).

## AI model explanation
TF-IDF + Logistic Regression (fake vs real language), a TF-IDF similarity fact check against the `knowledge_base`
table, and transparent rule signals are combined into a 0-100 risk score with human-readable reasons.
See [`ai/README.md`](ai/README.md) and [`docs/05_ai_module.md`](docs/05_ai_module.md).

## Deployment (Render example, with Postgres)
1. Push the repo to GitHub.
2. Render dashboard -> **New + -> Blueprint** -> select the repo (uses `render.yaml`): creates Postgres, the API (Docker) and the static frontend.
3. Edit the two URL values in the blueprint/env: `FRONTEND_URL` (API) = your static-site URL, `VITE_API_URL` (frontend) = `https://<your-api>.onrender.com/api`.
4. Open `https://<your-api>/docs` to confirm it is up. Neon/Supabase work too: paste their connection string into `DATABASE_URL`
   (`postgres://` is converted automatically; keep `?sslmode=require`).
5. Production checklist: strong `JWT_SECRET`, change demo passwords (or `SEED_ON_STARTUP=false`), restrict `FRONTEND_URL`.
> Uploaded media is stored on the server disk. On free hosts the disk is **ephemeral** (files vanish on redeploy); use a
> persistent disk or object storage (S3/Cloudinary) for real use. Full guide: [`docs/07_deployment.md`](docs/07_deployment.md).

## Testing
```bash
python -m pytest tests/test_ai.py                  # AI module (repo root)
cd backend && python -m pytest tests -v            # API tests (uses a temporary SQLite DB, no Postgres needed)
```
Backend tests cover registration, login, protected routes, post creation, AI analysis, fact verification, reports,
admin authorization, post approval and blocking, upload validation.

## Limitations
* Academic prototype; tiny sample dataset; the model mainly recognises sensational *style*.
* AI predictions are probabilistic and cannot catch all misinformation. **UNVERIFIED does not mean FALSE.**
* Media analysis is limited (file validation + optional OCR text); no deepfake detection.
* Human moderation is required for ambiguous/high-impact content. External fact-check APIs need their own keys.
* Rate limiting is in-memory (per server process). Tables are created with `create_all` (no migrations).
* Not security-audited. Do not market it as a perfect fake-news detector.

## Future scope
Larger real datasets and transformer models (Hugging Face), multilingual support, deepfake/image-forensics models,
Alembic migrations, object storage for media, Redis rate limiting, real-time WebSocket notifications, appeals workflow.
