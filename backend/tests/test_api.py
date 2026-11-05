from conftest import login

SAFE = "The city council approved the annual budget on Tuesday after a public hearing, according to meeting minutes."
RISKY = "SHOCKING EXPOSED: Vaccines cause autism in children, the mainstream media won't tell you, wake up and share before it's deleted!!!"


def test_register_and_duplicate(client, user_h):
    r = client.post("/api/auth/register", json={"username": "tester", "email": "other@truthshield.demo", "password": "Tester@1234"})
    assert r.status_code == 409
    bad = client.post("/api/auth/register", json={"username": "x", "email": "not-an-email", "password": "123"})
    assert bad.status_code == 422


def test_login_valid_and_invalid(client, user_h):
    assert client.post("/api/auth/login", json={"email": "tester@truthshield.demo", "password": "wrong-password"}).status_code == 401
    assert login(client, "tester@truthshield.demo", "Tester@1234")


def test_protected_route(client, user_h):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer garbage"}).status_code == 401
    r = client.get("/api/auth/me", headers=user_h)
    assert r.status_code == 200 and r.json()["username"] == "tester"


def test_ai_analysis_and_verification(client, user_h):
    r = client.post("/api/ai/analyze", json={"text": RISKY}, headers=user_h)
    assert r.status_code == 200
    body = r.json()
    assert body["risk_score"] > 50 and body["reasons"] and "disclaimer" in body
    v = client.post("/api/verification/check", json={"claim": "Vaccines cause autism in children"}, headers=user_h).json()
    assert v["status"] == "FALSE"
    u = client.post("/api/verification/check", json={"claim": "My neighbour bought a red bicycle yesterday"}, headers=user_h).json()
    assert u["status"] == "UNVERIFIED"  # unknown claim is never auto-labelled FALSE


def test_create_post_safe_and_risky(client, user_h):
    safe = client.post("/api/posts", data={"text": SAFE, "category": "Politics"}, headers=user_h)
    assert safe.status_code == 201 and safe.json()["status"] in ("PUBLISHED", "WARNING")
    assert safe.json()["analysis"]["reasons"]
    risky = client.post("/api/posts", data={"text": RISKY, "category": "Health"}, headers=user_h)
    assert risky.status_code == 201 and risky.json()["status"] in ("UNDER_REVIEW", "BLOCKED")
    feed_ids = [p["id"] for p in client.get("/api/posts").json()]
    assert risky.json()["id"] not in feed_ids and safe.json()["id"] in feed_ids


def test_file_validation(client, user_h, monkeypatch):
    bad = client.post("/api/posts", data={"text": "hello world", "category": "General"},
                      files={"file": ("virus.exe", b"MZ", "application/octet-stream")}, headers=user_h)
    assert bad.status_code == 400
    from app.config import settings
    monkeypatch.setattr(settings, "MAX_UPLOAD_MB", 0)
    big = client.post("/api/posts", data={"text": "hello world", "category": "General"},
                      files={"file": ("a.png", b"not really big", "image/png")}, headers=user_h)
    assert big.status_code == 413


def test_report_flow(client, user_h):
    post = client.post("/api/posts", data={"text": SAFE, "category": "General"}, headers=user_h).json()
    r = client.post("/api/reports", json={"post_id": post["id"], "reason": "Fake News", "description": "test"}, headers=user_h)
    assert r.status_code == 201 and r.json()["status"] == "PENDING"
    assert client.post("/api/reports", json={"post_id": post["id"], "reason": "Fake News"}, headers=user_h).status_code == 409
    assert client.put(f"/api/reports/{r.json()['report_id']}", json={"status": "RESOLVED"}, headers=user_h).status_code == 403


def test_admin_authorization(client, user_h, admin_h):
    assert client.get("/api/admin/dashboard").status_code == 401
    assert client.get("/api/admin/dashboard", headers=user_h).status_code == 403
    r = client.get("/api/admin/dashboard", headers=admin_h)
    assert r.status_code == 200 and r.json()["total_users"] >= 6


def test_admin_approve_block_and_notify(client, user_h, admin_h):
    post = client.post("/api/posts", data={"text": RISKY, "category": "Health"}, headers=user_h).json()
    ok = client.put(f"/api/admin/posts/{post['id']}", json={"action": "approve", "note": "checked"}, headers=admin_h)
    assert ok.status_code == 200 and ok.json()["status"] == "PUBLISHED"
    blocked = client.put(f"/api/admin/posts/{post['id']}", json={"action": "block"}, headers=admin_h)
    assert blocked.json()["status"] == "BLOCKED"
    notes = client.get("/api/notifications", headers=user_h).json()["items"]
    assert any(n["type"] == "ADMIN_DECISION" for n in notes)
    assert client.put(f"/api/admin/posts/{post['id']}", json={"action": "approve"}, headers=user_h).status_code == 403
    rep = client.get("/api/admin/feedback-dataset", headers=admin_h).json()
    assert len(rep) >= 2  # human decisions stored for controlled retraining


def test_admin_report_review_and_kb(client, user_h, admin_h):
    reports = client.get("/api/admin/reports", headers=admin_h).json()
    assert reports
    rid = reports[0]["report_id"]
    r = client.put(f"/api/admin/reports/{rid}", json={"status": "RESOLVED", "resolution_note": "ok"}, headers=admin_h)
    assert r.status_code == 200 and r.json()["status"] == "RESOLVED"
    kb = {"claim": "Test claim about gravity", "verified_fact": "Gravity is real.", "source": "Test", "category": "Science", "verification_status": "TRUE"}
    created = client.post("/api/admin/knowledge-base", json=kb, headers=admin_h)
    assert created.status_code == 201
    kid = created.json()["knowledge_id"]
    assert client.delete(f"/api/admin/knowledge-base/{kid}", headers=admin_h).status_code == 200
