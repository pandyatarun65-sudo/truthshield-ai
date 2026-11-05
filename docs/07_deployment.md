# 07 - Deployment
Target: Frontend -> Backend API -> PostgreSQL (+ AI module inside the backend image).

**Local Docker:** `docker compose up --build` (db + backend + frontend).

**Render:** use `render.yaml` (Blueprint). Set `FRONTEND_URL` on the API to the static-site URL and `VITE_API_URL` on the static site to `https://<api>/api`.
**Railway / Fly.io:** deploy `docker/backend.Dockerfile` (build context = repo root) with the same env vars and a Postgres add-on; host `frontend/dist` on any static host.
**Managed Postgres (Neon, Supabase, Render):** put the connection string in `DATABASE_URL` (`postgres://` is converted automatically).

**Production checklist:** long random `JWT_SECRET`; replace/disable demo accounts (`SEED_ON_STARTUP=false` after first run); restrict `FRONTEND_URL`;
HTTPS only; persistent storage for `/srv/uploads` (ephemeral on free tiers); backups; consider Alembic migrations.
