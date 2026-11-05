-- Reference PostgreSQL schema. The backend creates these tables automatically on startup
-- (SQLAlchemy create_all), so running this file is OPTIONAL (e.g. for manual setup / viva demo).
CREATE TABLE users (
  id SERIAL PRIMARY KEY, username VARCHAR(30) UNIQUE NOT NULL, email VARCHAR(120) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL, role VARCHAR(20) NOT NULL DEFAULT 'user',   -- user | moderator | admin
  is_active BOOLEAN NOT NULL DEFAULT TRUE, trust_score INTEGER NOT NULL DEFAULT 80, photo_url VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE knowledge_base (
  knowledge_id SERIAL PRIMARY KEY, claim TEXT NOT NULL, verified_fact TEXT NOT NULL, source VARCHAR(200) NOT NULL,
  category VARCHAR(50) NOT NULL, verification_status VARCHAR(15) NOT NULL,         -- TRUE | FALSE | MISLEADING
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE posts (
  id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), text TEXT NOT NULL,
  category VARCHAR(50) NOT NULL DEFAULT 'General', media_path VARCHAR(255), media_type VARCHAR(10),
  status VARCHAR(20) NOT NULL,        -- PUBLISHED | WARNING | UNDER_REVIEW | BLOCKED | REMOVED
  risk_score INTEGER NOT NULL DEFAULT 0, risk_level VARCHAR(20) NOT NULL DEFAULT 'SAFE',
  decision VARCHAR(30) NOT NULL DEFAULT 'PUBLISH', shares_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(), updated_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE INDEX ix_posts_user ON posts(user_id);
CREATE INDEX ix_posts_status ON posts(status);

CREATE TABLE ai_analysis (                                   -- Post 1 -> 1 AI analysis
  id SERIAL PRIMARY KEY, post_id INTEGER UNIQUE NOT NULL REFERENCES posts(id),
  fake_probability DOUBLE PRECISION NOT NULL, real_probability DOUBLE PRECISION NOT NULL,
  confidence DOUBLE PRECISION NOT NULL, credibility DOUBLE PRECISION NOT NULL, risk_score INTEGER NOT NULL,
  risk_level VARCHAR(20) NOT NULL, ml_label VARCHAR(10) NOT NULL, reasons JSON NOT NULL, ocr_text TEXT,
  model_version VARCHAR(60) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE fact_verifications (                            -- Knowledge base -> fact verification
  id SERIAL PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id),
  knowledge_id INTEGER REFERENCES knowledge_base(knowledge_id), status VARCHAR(15) NOT NULL,
  similarity DOUBLE PRECISION NOT NULL DEFAULT 0, explanation TEXT NOT NULL, source VARCHAR(200),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE reports (                                       -- Post 1 -> many reports, User 1 -> many reports
  report_id SERIAL PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), user_id INTEGER NOT NULL REFERENCES users(id),
  reason VARCHAR(40) NOT NULL, description TEXT, status VARCHAR(15) NOT NULL DEFAULT 'PENDING',
  reviewed_by INTEGER REFERENCES users(id), resolution_note TEXT, created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE notifications (                                 -- User 1 -> many notifications
  id SERIAL PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES users(id), post_id INTEGER REFERENCES posts(id),
  type VARCHAR(30) NOT NULL, message VARCHAR(300) NOT NULL, is_read BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE decision_logs (                                 -- Admin 1 -> many decisions (decided_by NULL = AI)
  id SERIAL PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), decided_by INTEGER REFERENCES users(id),
  source VARCHAR(10) NOT NULL, decision VARCHAR(30) NOT NULL, risk_score INTEGER NOT NULL, note TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE comments (
  id SERIAL PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), user_id INTEGER NOT NULL REFERENCES users(id),
  text VARCHAR(500) NOT NULL, created_at TIMESTAMPTZ NOT NULL DEFAULT now());

CREATE TABLE likes (
  id SERIAL PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), user_id INTEGER NOT NULL REFERENCES users(id),
  CONSTRAINT uq_like UNIQUE (post_id, user_id));

CREATE TABLE activity_logs (
  id SERIAL PRIMARY KEY, user_id INTEGER REFERENCES users(id), action VARCHAR(40) NOT NULL, detail VARCHAR(300),
  ip VARCHAR(45), created_at TIMESTAMPTZ NOT NULL DEFAULT now());
CREATE INDEX ix_activity_action ON activity_logs(action);

CREATE TABLE feedback_dataset (                              -- AI prediction vs final human decision
  id SERIAL PRIMARY KEY, post_id INTEGER NOT NULL REFERENCES posts(id), text TEXT NOT NULL, ai_label VARCHAR(10) NOT NULL,
  ai_risk_score INTEGER NOT NULL, human_decision VARCHAR(20) NOT NULL, moderator_id INTEGER NOT NULL REFERENCES users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now());
