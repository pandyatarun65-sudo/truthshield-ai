# 04 - API documentation
Live, interactive docs: `/docs` (Swagger) and `/redoc`. Auth: `Authorization: Bearer <JWT>`. Errors are JSON `{"detail": "..."}`.

| Method & path | Auth | Purpose |
|---|---|---|
| POST /api/auth/register, /api/auth/login | - | create account / get JWT |
| GET /api/auth/me | user | current user |
| GET, PUT /api/users/{id}; POST /api/users/{id}/photo | user | profile |
| POST /api/posts (multipart: text, category, file?) | user | analyse + decide + store |
| GET /api/posts?q=&category=&mine= | optional | feed / search (public posts only) |
| GET, PUT, DELETE /api/posts/{id} | optional/owner | details incl. AI analysis, edit (re-analysed), soft delete |
| POST /api/posts/{id}/like, /share; GET, POST /api/posts/{id}/comments | user | interactions |
| POST /api/ai/analyze | user | preview analysis (nothing stored) |
| POST /api/verification/check | user | check a claim |
| POST /api/reports; GET /api/reports; PUT /api/reports/{id} | user / staff | report flow |
| GET /api/notifications; PUT /api/notifications/{id}/read, /read-all | user | notifications |
| GET /api/admin/dashboard, /users, /posts, /reports, /analytics, /logs, /feedback-dataset | staff | moderation data |
| PUT /api/admin/posts/{id} `{action: approve/block/restore/remove}` | staff | human decision |
| PUT /api/admin/reports/{id} | staff | review / resolve / reject |
| PUT /api/admin/users/{id} `{is_active}` | admin | suspend / activate |
| GET, POST /api/admin/knowledge-base; PUT, DELETE /api/admin/knowledge-base/{id} | staff | knowledge base CRUD |

Status codes: 400 invalid file, 401 not logged in / expired JWT, 403 forbidden, 404 not found, 409 duplicate,
413 file too large, 422 validation, 429 rate limit, 503 database unavailable.
