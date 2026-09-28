from fastapi.testclient import TestClient
from app import database
from app.auth import issue_development_token
from app.main import app

def test_smoke_health_database_and_auth(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"smoke.sqlite3"))
    with TestClient(app) as client:
        assert client.get("/health").json()=={"status":"ok"}
        conn=database.connection()
        conn.execute("INSERT INTO studios(id,name,timezone) VALUES(?,?,?)",("smoke-studio","Smoke","America/Santiago"))
        conn.execute("INSERT INTO users(id,email,created_at) VALUES(?,?,?)",("smoke-owner","owner@smoke.test","2026-01-01T00:00:00+00:00"))
        conn.execute("INSERT INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",("smoke-studio","smoke-owner","OWNER_ADMIN")); conn.commit(); conn.close()
        headers={"Authorization":f"Bearer {issue_development_token('smoke-owner')}"}
        assert client.get("/studios/smoke-studio/performed-services",headers=headers).status_code==200
        assert client.get("/studios/smoke-studio/performed-services").status_code==401
