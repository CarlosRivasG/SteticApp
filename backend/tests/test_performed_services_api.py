from fastapi.testclient import TestClient
from app import database
from app.auth import issue_development_token
from app.main import app
def seed(conn,user,studio):
    conn.execute("INSERT INTO studios(id,name,timezone) VALUES(?,?,?)",(studio,studio,"America/Santiago")); conn.execute("INSERT INTO users(id,email,created_at) VALUES(?,?,?)",(user,f"{user}@test.local","2026-01-01T00:00:00+00:00")); conn.execute("INSERT INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",(studio,user,"OWNER_ADMIN")); conn.commit()
def test_performed_services_authorization_and_idempotency(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"test.sqlite3")); payload={"professional_name":"Maira","service_name":"Manicure","list_price_clp":25000,"discount_clp":0,"commission_percentage":"50","materials_provider":"LOCAL","operating_date":"2026-09-26"}
    with TestClient(app) as client:
        conn=database.connection(); seed(conn,"u1","s1"); seed(conn,"u2","s2"); conn.close(); headers={"Authorization":f"Bearer {issue_development_token('u1')}","Idempotency-Key":"request-1"}
        first=client.post("/studios/s1/performed-services",json=payload,headers=headers); assert first.status_code==201
        assert client.get("/studios/s1/performed-services",headers=headers).json()["items"][0]["id"]==first.json()["id"]
        second=client.post("/studios/s1/performed-services",json=payload,headers=headers); assert second.status_code==201 and second.json()["id"]==first.json()["id"]
        assert client.post("/studios/s1/performed-services",json={**payload,"discount_clp":1},headers=headers).status_code==409
        other={"Authorization":f"Bearer {issue_development_token('u2')}","Idempotency-Key":"other"}; assert client.get("/studios/s1/performed-services",headers=other).status_code==403
        assert client.post("/studios/s1/performed-services",json={**payload,"extra":True},headers={**headers,"Idempotency-Key":"request-2"}).status_code==422
