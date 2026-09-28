from fastapi.testclient import TestClient
from app import database
from app.auth import issue_development_token
from app.main import app

def seed(conn,user,studio,role="OWNER_ADMIN"):
    conn.execute("INSERT OR IGNORE INTO studios(id,name,timezone) VALUES(?,?,?)",(studio,studio,"America/Santiago")); conn.execute("INSERT INTO users(id,email,created_at) VALUES(?,?,?)",(user,f"{user}@local.test","2026-01-01T00:00:00+00:00")); conn.execute("INSERT INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",(studio,user,role)); conn.commit()

def test_agenda_has_no_automatic_sale_and_is_isolated(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"agenda.sqlite3"))
    with TestClient(app) as client:
        conn=database.connection(); seed(conn,"owner","a"); seed(conn,"pro","a","PROFESSIONAL"); seed(conn,"other","b"); conn.close()
        owner={"Authorization":f"Bearer {issue_development_token('owner')}"}; pro={"Authorization":f"Bearer {issue_development_token('pro')}"}; other={"Authorization":f"Bearer {issue_development_token('other')}"}
        customer=client.post("/studios/a/clients",json={"name":"Camila","contact":None},headers=owner); assert customer.status_code==201
        appointment=client.post("/studios/a/appointments",json={"client_id":customer.json()["id"],"professional_id":"pro","service_name":"Manicure","start_at":"2026-09-29T10:00:00"},headers=owner); assert appointment.status_code==201
        assert client.get("/studios/a/performed-services",headers=owner).json()["items"]==[]
        assert len(client.get("/studios/a/appointments",headers=pro).json()["items"])==1
        assert client.get("/studios/a/clients",headers=pro).status_code==403
        assert client.get("/studios/a/appointments",headers=other).status_code==403
        assert client.post(f"/studios/a/appointments/{appointment.json()['id']}/status",json={"status":"ATENDIDA"},headers=owner).status_code==200
        assert client.put(f"/studios/a/appointments/{appointment.json()['id']}",json={"client_id":customer.json()["id"],"professional_id":"pro","service_name":"Pedicure","start_at":"2026-09-29T11:00:00"},headers=owner).status_code==409
