import hashlib,json
from datetime import date,datetime,timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo
from .database import connection

SANTIAGO=ZoneInfo("America/Santiago")
METHODS=("EFECTIVO","TRANSFERENCIA","TARJETA","OTRO")

class CashConflict(ValueError): pass
class DayClosed(ValueError): pass

def _fingerprint(payload):
    data={key:(value.isoformat() if hasattr(value,"isoformat") else value) for key,value in payload.items()}
    return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest()

def _day_row(conn,studio_id,operating_date):
    return conn.execute("SELECT * FROM cash_days WHERE studio_id=? AND operating_date=?",(studio_id,operating_date)).fetchone()

def ensure_day_open(conn,studio_id,operating_date):
    row=_day_row(conn,studio_id,operating_date)
    if row and row["status"]=="CLOSED": raise DayClosed("El día está cerrado; reábrelo con un motivo antes de modificarlo")

def _event(conn,studio_id,key,fingerprint):
    prior=conn.execute("SELECT * FROM cash_day_events WHERE studio_id=? AND idempotency_key=?",(studio_id,key)).fetchone()
    if not prior: return None
    if prior["request_fingerprint"]!=fingerprint: raise CashConflict("La clave de idempotencia ya fue usada con otro payload")
    return prior

def _insert_audit(conn,studio_id,actor_id,action,entity_id,key,now):
    conn.execute("INSERT INTO audit_events(id,studio_id,actor_id,action,entity_type,entity_id,idempotency_key,created_at) VALUES(?,?,?,?,?,?,?,?)",(str(uuid4()),studio_id,actor_id,action,"cash_day",entity_id,key,now))

def _expected_by_method(conn,studio_id,operating_date,opening=0):
    expected={method:0 for method in METHODS}; expected["EFECTIVO"]=opening
    for row in conn.execute("SELECT method,COALESCE(SUM(amount_clp),0) amount FROM payments WHERE studio_id=? AND status='ACTIVO' AND substr(received_at,1,10)=? GROUP BY method",(studio_id,operating_date)):
        expected[row["method"]]+=row["amount"]
    for row in conn.execute("SELECT method,COALESCE(SUM(amount_clp),0) amount FROM financial_movements WHERE studio_id=? AND operating_date=? AND paid=1 GROUP BY method",(studio_id,operating_date)):
        expected[row["method"]]-=row["amount"]
    return expected

def create_movement(studio_id,payload,actor_id,idempotency_key):
    fingerprint=_fingerprint(payload); conn=connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        prior=conn.execute("SELECT * FROM financial_movements WHERE studio_id=? AND idempotency_key=?",(studio_id,idempotency_key)).fetchone()
        if prior:
            if prior["request_fingerprint"]==fingerprint: conn.commit(); return dict(prior)
            raise CashConflict("La clave de idempotencia ya fue usada con otro payload")
        operating_date=payload["operating_date"].isoformat(); ensure_day_open(conn,studio_id,operating_date)
        now=datetime.now(SANTIAGO).isoformat(); record={"id":str(uuid4()),"studio_id":studio_id,"operating_date":operating_date,"type":payload["type"],"amount_clp":payload["amount_clp"],"method":payload["method"],"paid":int(payload["paid"]),"note":payload["note"].strip(),"actor_id":actor_id,"idempotency_key":idempotency_key,"request_fingerprint":fingerprint,"created_at":now}
        conn.execute("INSERT INTO financial_movements(id,studio_id,operating_date,type,amount_clp,method,paid,note,actor_id,idempotency_key,request_fingerprint,created_at) VALUES(:id,:studio_id,:operating_date,:type,:amount_clp,:method,:paid,:note,:actor_id,:idempotency_key,:request_fingerprint,:created_at)",record)
        _insert_audit(conn,studio_id,actor_id,"CREATE_MOVEMENT",record["id"],idempotency_key,now); conn.commit(); return record
    except Exception: conn.rollback(); raise
    finally: conn.close()

def update_cash_day(studio_id,operating_date,payload,actor_id,idempotency_key):
    fingerprint=_fingerprint({"action":"UPDATE_CASH","operating_date":operating_date,**payload}); conn=connection()
    try:
        conn.execute("BEGIN IMMEDIATE"); prior=_event(conn,studio_id,idempotency_key,fingerprint)
        if prior: conn.commit(); return daily_summary(studio_id,operating_date)
        ensure_day_open(conn,studio_id,operating_date); row=_day_row(conn,studio_id,operating_date)
        opening=payload.get("opening_cash_clp",row["opening_cash_clp"] if row else 0); counted=payload.get("counted_cash_clp",row["counted_cash_clp"] if row else None)
        conn.execute("INSERT INTO cash_days(studio_id,operating_date,opening_cash_clp,counted_cash_clp) VALUES(?,?,?,?) ON CONFLICT(studio_id,operating_date) DO UPDATE SET opening_cash_clp=excluded.opening_cash_clp,counted_cash_clp=excluded.counted_cash_clp",(studio_id,operating_date,opening,counted))
        now=datetime.now(SANTIAGO).isoformat(); expected=_expected_by_method(conn,studio_id,operating_date,opening)["EFECTIVO"]
        event_id=str(uuid4()); conn.execute("INSERT INTO cash_day_events(id,studio_id,operating_date,action,opening_cash_clp,counted_cash_clp,expected_cash_clp,difference_clp,reason,actor_id,idempotency_key,request_fingerprint,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(event_id,studio_id,operating_date,"UPDATE_CASH",opening,counted,expected,None if counted is None else counted-expected,"",actor_id,idempotency_key,fingerprint,now)); _insert_audit(conn,studio_id,actor_id,"UPDATE_CASH",event_id,idempotency_key,now); conn.commit()
    except Exception: conn.rollback(); raise
    finally: conn.close()
    return daily_summary(studio_id,operating_date)

def close_day(studio_id,operating_date,payload,actor_id,idempotency_key):
    fingerprint=_fingerprint({"action":"CLOSE_DAY","operating_date":operating_date,**payload}); conn=connection()
    try:
        conn.execute("BEGIN IMMEDIATE"); prior=_event(conn,studio_id,idempotency_key,fingerprint)
        if prior: conn.commit(); return daily_summary(studio_id,operating_date)
        ensure_day_open(conn,studio_id,operating_date); row=_day_row(conn,studio_id,operating_date); opening=row["opening_cash_clp"] if row else 0; expected=_expected_by_method(conn,studio_id,operating_date,opening)["EFECTIVO"]; now=datetime.now(SANTIAGO).isoformat()
        conn.execute("INSERT INTO cash_days(studio_id,operating_date,opening_cash_clp,counted_cash_clp,status,closed_at) VALUES(?,?,?,?,?,?) ON CONFLICT(studio_id,operating_date) DO UPDATE SET counted_cash_clp=excluded.counted_cash_clp,status='CLOSED',closed_at=excluded.closed_at",(studio_id,operating_date,opening,payload["counted_cash_clp"],"CLOSED",now))
        event_id=str(uuid4()); conn.execute("INSERT INTO cash_day_events(id,studio_id,operating_date,action,opening_cash_clp,counted_cash_clp,expected_cash_clp,difference_clp,reason,actor_id,idempotency_key,request_fingerprint,created_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)",(event_id,studio_id,operating_date,"CLOSE_DAY",opening,payload["counted_cash_clp"],expected,payload["counted_cash_clp"]-expected,payload["reason"].strip(),actor_id,idempotency_key,fingerprint,now)); _insert_audit(conn,studio_id,actor_id,"CLOSE_DAY",event_id,idempotency_key,now); conn.commit()
    except Exception: conn.rollback(); raise
    finally: conn.close()
    return daily_summary(studio_id,operating_date)

def reopen_day(studio_id,operating_date,payload,actor_id,idempotency_key):
    fingerprint=_fingerprint({"action":"REOPEN_DAY","operating_date":operating_date,**payload}); conn=connection()
    try:
        conn.execute("BEGIN IMMEDIATE"); prior=_event(conn,studio_id,idempotency_key,fingerprint)
        if prior: conn.commit(); return daily_summary(studio_id,operating_date)
        row=_day_row(conn,studio_id,operating_date)
        if not row or row["status"]!="CLOSED": raise DayClosed("El día no está cerrado")
        now=datetime.now(SANTIAGO).isoformat(); conn.execute("UPDATE cash_days SET status='OPEN',closed_at=NULL WHERE studio_id=? AND operating_date=?",(studio_id,operating_date))
        event_id=str(uuid4()); conn.execute("INSERT INTO cash_day_events(id,studio_id,operating_date,action,reason,actor_id,idempotency_key,request_fingerprint,created_at) VALUES(?,?,?,?,?,?,?,?,?)",(event_id,studio_id,operating_date,"REOPEN_DAY",payload["reason"].strip(),actor_id,idempotency_key,fingerprint,now)); _insert_audit(conn,studio_id,actor_id,"REOPEN_DAY",event_id,idempotency_key,now); conn.commit()
    except Exception: conn.rollback(); raise
    finally: conn.close()
    return daily_summary(studio_id,operating_date)

def daily_summary(studio_id,operating_date):
    conn=connection()
    try:
        day=_day_row(conn,studio_id,operating_date); opening=day["opening_cash_clp"] if day else 0
        services=[dict(row) for row in conn.execute("SELECT * FROM performed_services WHERE studio_id=? AND operating_date=? AND status='CONFIRMADO' ORDER BY created_at,id",(studio_id,operating_date))]
        payments=[dict(row) for row in conn.execute("SELECT * FROM payments WHERE studio_id=? AND status='ACTIVO' AND substr(received_at,1,10)=? ORDER BY received_at,id",(studio_id,operating_date))]
        movements=[dict(row) for row in conn.execute("SELECT * FROM financial_movements WHERE studio_id=? AND operating_date=? ORDER BY created_at,id",(studio_id,operating_date))]
        expected=_expected_by_method(conn,studio_id,operating_date,opening); studio_share=sum(row["studio_share_clp"] for row in services); operating=sum(row["amount_clp"] for row in movements if row["type"] in ("OPERATING_EXPENSE","ADMIN_SALARY")); withdrawals=sum(row["amount_clp"] for row in movements if row["type"]=="OWNER_WITHDRAWAL"); service_ids=[row["id"] for row in services]; paid_for_services=0 if not service_ids else conn.execute(f"SELECT COALESCE(SUM(amount_clp),0) total FROM payments WHERE studio_id=? AND status='ACTIVO' AND performed_service_id IN ({','.join('?' for _ in service_ids)})",[studio_id,*service_ids]).fetchone()["total"]
        counted=day["counted_cash_clp"] if day else None; events=[dict(row) for row in conn.execute("SELECT * FROM cash_day_events WHERE studio_id=? AND operating_date=? ORDER BY created_at,id",(studio_id,operating_date))]
        return {"operating_date":operating_date,"cash_day":{"opening_cash_clp":opening,"counted_cash_clp":counted,"status":day["status"] if day else "OPEN","closed_at":day["closed_at"] if day else None,"expected_by_method":expected,"expected_cash_clp":expected["EFECTIVO"],"difference_clp":None if counted is None else counted-expected["EFECTIVO"]},"totals":{"sales_clp":sum(row["final_price_clp"] for row in services),"commissions_clp":sum(row["commission_clp"] for row in services),"studio_share_clp":studio_share,"payments_received_clp":sum(row["amount_clp"] for row in payments),"pending_clp":sum(row["final_price_clp"] for row in services)-paid_for_services,"operating_expenses_clp":operating,"owner_withdrawals_clp":withdrawals,"operating_result_clp":studio_share-operating},"services":services,"payments":payments,"movements":movements,"closure_history":events}
    finally: conn.close()

def weekly_summary(studio_id,start_date):
    start=date.fromisoformat(start_date); days=[daily_summary(studio_id,(start+timedelta(days=index)).isoformat()) for index in range(7)]
    keys=("sales_clp","commissions_clp","studio_share_clp","payments_received_clp","pending_clp","operating_expenses_clp","owner_withdrawals_clp","operating_result_clp")
    return {"week_start":start.isoformat(),"week_end":(start+timedelta(days=6)).isoformat(),"totals":{key:sum(day["totals"][key] for day in days) for key in keys},"days":days}
