# Database

PostgreSQL 14+ is used. Tables are created automatically when the backend starts.
`schema.sql` is a reference copy of the same schema. Demo data lives in `backend/app/seed_data.py`
and is inserted on first start when `SEED_ON_STARTUP=true` and the `users` table is empty.

Note: there is no separate `admin_users` table; admins and moderators are rows in `users`
with `role = 'admin'` / `'moderator'` (role-based access control).

Reset the demo data: `docker compose down -v` (removes the volume) and start again.
