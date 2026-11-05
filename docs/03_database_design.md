# 03 - Database design (PostgreSQL)

Collections requested in the brief are implemented as relational tables. Admins/moderators are `users.role`
(no separate `admin_users` table). Extra table: `feedback_dataset`.

```mermaid
erDiagram
  USERS ||--o{ POSTS : writes
  POSTS ||--|| AI_ANALYSIS : has
  POSTS ||--o{ FACT_VERIFICATIONS : checked_by
  KNOWLEDGE_BASE ||--o{ FACT_VERIFICATIONS : matched_in
  POSTS ||--o{ REPORTS : receives
  USERS ||--o{ REPORTS : files
  USERS ||--o{ NOTIFICATIONS : receives
  POSTS ||--o{ DECISION_LOGS : has
  USERS ||--o{ DECISION_LOGS : decides
  POSTS ||--o{ COMMENTS : has
  POSTS ||--o{ LIKES : has
  USERS ||--o{ ACTIVITY_LOGS : generates
  POSTS ||--o{ FEEDBACK_DATASET : feeds
  USERS { int id PK string username string email string password_hash string role bool is_active int trust_score }
  POSTS { int id PK int user_id FK text text string status int risk_score string risk_level }
  AI_ANALYSIS { int id PK int post_id FK float fake_probability float confidence int risk_score json reasons }
  FACT_VERIFICATIONS { int id PK int post_id FK int knowledge_id FK string status float similarity }
  KNOWLEDGE_BASE { int knowledge_id PK text claim text verified_fact string source string verification_status }
  REPORTS { int report_id PK int post_id FK int user_id FK string reason string status int reviewed_by FK }
  NOTIFICATIONS { int id PK int user_id FK string type string message bool is_read }
  DECISION_LOGS { int id PK int post_id FK int decided_by FK string source string decision }
```
Full DDL: [`database/schema.sql`](../database/schema.sql). Posts are soft-deleted (`status = REMOVED`) to keep the audit trail.
