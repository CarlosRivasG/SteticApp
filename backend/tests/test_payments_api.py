from fastapi.testclient import TestClient
from app import database
from app.auth import issue_development_token
from app.main import app

def seed(conn,user,studio):
    conn.execute("INSERT INTO studios(id,name,timezone) VALUES(?,?,?)",(studio,studio,"America/Santiago")); conn.execute("INSERT INTO users(id,email,created_at) VALUES(?,?,?)",(user,f"{user}@test.local","2026-01-01T00:00:00+00:00")); conn.execute("INSERT INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",(studio,user,"OWNER_ADMIN")); conn.commit()

def service_payload(): return {"professional_name":"Maira","service_name":"Manicure","list_price_clp":25000,"discount_clp":0,"commission_percentage":"50","materials_provider":"LOCAL","operating_date":"2026-09-27"}

def test_partial_payments_are_authorized_idempotent_and_do_not_change_commission(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"payments.sqlite3"))
    with TestClient(app) as client:
        conn=database.connection(); seed(conn,"owner","studio-a"); seed(conn,"other","studio-b"); conn.close()
        owner={"Authorization":f"Bearer {issue_development_token('owner')}"}; other={"Authorization":f"Bearer {issue_development_token('other')}"}
        service=client.post("/studios/studio-a/performed-services",json=service_payload(),headers={**owner,"Idempotency-Key":"service-1"}).json(); url=f"/studios/studio-a/performed-services/{service['id']}/payments"
        cash=client.post(url,json={"amount_clp":10000,"method":"EFECTIVO"},headers={**owner,"Idempotency-Key":"payment-1"}); assert cash.status_code==201
        retry=client.post(url,json={"amount_clp":10000,"method":"EFECTIVO"},headers={**owner,"Idempotency-Key":"payment-1"}); assert retry.status_code==201 and retry.json()["id"]==cash.json()["id"]
        transfer=client.post(url,json={"amount_clp":15000,"method":"TRANSFERENCIA"},headers={**owner,"Idempotency-Key":"payment-2"}); assert transfer.status_code==201
        assert client.post(url,json={"amount_clp":1,"method":"OTRO"},headers={**owner,"Idempotency-Key":"payment-3"}).status_code==422
        assert client.post(url,json={"amount_clp":9999,"method":"TARJETA"},headers={**owner,"Idempotency-Key":"payment-1"}).status_code==409
        assert client.get(url,headers=other).status_code==403
        listed=client.get("/studios/studio-a/performed-services",headers=owner).json()["items"][0]
        assert sum(payment["amount_clp"] for payment in listed["payments"])==25000
        assert listed["commission_clp"]==12500

def test_full_payment_leaves_no_pending_balance(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"full-payment.sqlite3"))
    with TestClient(app) as client:
        conn=database.connection(); seed(conn,"owner","studio-a"); conn.close()
        owner={"Authorization":f"Bearer {issue_development_token('owner')}"}
        service=client.post("/studios/studio-a/performed-services",json=service_payload(),headers={**owner,"Idempotency-Key":"service-full"}).json()
        url=f"/studios/studio-a/performed-services/{service['id']}/payments"
        payment=client.post(url,json={"amount_clp":25000,"method":"TARJETA"},headers={**owner,"Idempotency-Key":"payment-full"})
        assert payment.status_code==201
        listed=client.get(url,headers=owner).json()["items"]
        assert sum(row["amount_clp"] for row in listed)==service["final_price_clp"]
