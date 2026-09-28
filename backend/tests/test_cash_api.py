from fastapi.testclient import TestClient
from app import database
from app.auth import issue_development_token
from app.main import app

def seed(conn,user,studio,role="OWNER_ADMIN"):
    conn.execute("INSERT OR IGNORE INTO studios(id,name,timezone) VALUES(?,?,?)",(studio,studio,"America/Santiago"))
    conn.execute("INSERT INTO users(id,email,created_at) VALUES(?,?,?)",(user,f"{user}@test.local","2026-01-01T00:00:00+00:00"))
    conn.execute("INSERT INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",(studio,user,role)); conn.commit()

def service_payload(day):
    return {"professional_name":"Maira","service_name":"Manicure","list_price_clp":25000,"discount_clp":0,"commission_percentage":"50","materials_provider":"LOCAL","operating_date":day}

def test_cash_movements_close_reopen_and_permissions(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"cash.sqlite3")); day="2026-09-28"
    with TestClient(app) as client:
        conn=database.connection(); seed(conn,"owner","studio-a"); seed(conn,"professional","studio-a","PROFESSIONAL"); seed(conn,"other","studio-b"); conn.close()
        owner={"Authorization":f"Bearer {issue_development_token('owner')}"}; professional={"Authorization":f"Bearer {issue_development_token('professional')}"}; other={"Authorization":f"Bearer {issue_development_token('other')}"}
        service=client.post("/studios/studio-a/performed-services",json=service_payload(day),headers={**owner,"Idempotency-Key":"service"}).json()
        payment_url=f"/studios/studio-a/performed-services/{service['id']}/payments"
        assert client.post(payment_url,json={"amount_clp":25000,"method":"EFECTIVO"},headers={**owner,"Idempotency-Key":"payment"}).status_code==201
        movement={"type":"OWNER_WITHDRAWAL","amount_clp":4000,"method":"EFECTIVO","paid":True,"note":"retiro","operating_date":day}
        created=client.post("/studios/studio-a/movements",json=movement,headers={**owner,"Idempotency-Key":"move"}); assert created.status_code==201
        assert client.post("/studios/studio-a/movements",json=movement,headers={**owner,"Idempotency-Key":"move"}).json()["id"]==created.json()["id"]
        assert client.post("/studios/studio-a/movements",json={**movement,"amount_clp":1},headers={**owner,"Idempotency-Key":"move"}).status_code==409
        summary=client.get(f"/studios/studio-a/summaries/daily?operating_date={day}",headers=owner).json(); assert summary["cash_day"]["expected_cash_clp"]==21000
        assert client.put(f"/studios/studio-a/cash-days/{day}",json={"counted_cash_clp":19000},headers={**owner,"Idempotency-Key":"count"}).status_code==200
        closed=client.post(f"/studios/studio-a/cash-days/{day}/close",json={"counted_cash_clp":19000,"reason":"cierre"},headers={**owner,"Idempotency-Key":"close"}); assert closed.status_code==200 and closed.json()["cash_day"]["difference_clp"]==-2000
        assert client.post("/studios/studio-a/movements",json=movement,headers={**owner,"Idempotency-Key":"after-close"}).status_code==409
        assert client.post(f"/studios/studio-a/cash-days/{day}/reopen",json={"reason":"corrección"},headers={**owner,"Idempotency-Key":"reopen"}).status_code==200
        pending={"type":"OPERATING_EXPENSE","amount_clp":3000,"method":"EFECTIVO","paid":False,"note":"pendiente","operating_date":day}
        assert client.post("/studios/studio-a/movements",json=pending,headers={**owner,"Idempotency-Key":"pending"}).status_code==201
        summary=client.get(f"/studios/studio-a/summaries/daily?operating_date={day}",headers=owner).json(); assert summary["cash_day"]["expected_cash_clp"]==21000 and summary["totals"]["operating_result_clp"]==9500
        assert client.post("/studios/studio-a/movements",json=movement,headers={**professional,"Idempotency-Key":"no-role"}).status_code==403
        assert client.get(f"/studios/studio-a/summaries/daily?operating_date={day}",headers=professional).status_code==403
        assert client.get(f"/studios/studio-a/summaries/daily?operating_date={day}",headers=other).status_code==403
