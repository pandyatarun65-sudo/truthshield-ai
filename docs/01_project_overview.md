# 01 - Project overview

**TruthShield AI** is a pre-publication content-moderation prototype for social media. Assume a platform has allowed
TruthShield to integrate: a new post is *not* public until it has been analysed.

**Goals:** reduce the spread of misinformation, keep humans in control, make every decision explainable and auditable.

**Roles:** *User* (post, like, comment, report) · *Moderator* (review posts/reports, knowledge base) · *Admin* (everything + suspend users).

**Decision engine (configurable):**
| Risk score | Level | Action |
|---|---|---|
| 0-30 | SAFE | publish |
| 31-60 | WARNING | publish with warning label |
| 61-80 | REVIEW | hold for moderator |
| 81-100 | HIGH RISK | block + send to moderator (never auto-deleted) |

**Scope & honesty:** academic prototype; see limitations in the README. UNVERIFIED does not mean FALSE.
