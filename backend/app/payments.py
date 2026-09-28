import hashlib,json
from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo
from .database import connection
from .cash import ensure_day_open
SANTIAGO=ZoneInfo("America/Santiago")
class PaymentConflict(ValueError): pass
class PaymentValidationError(ValueError): pass
def _fingerprint(payload): return hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def list_payments(studio_id,service_id,professional_id=None):
    conn=connection()
    try:
        query="SELECT id FROM performed_services WHERE id=? AND studio_id=? AND status='CONFIRMADO'"; params=[service_id,studio_id]
        if professional_id is not None: query+=" AND professional_id=?"; params.append(professional_id)
        service=conn.execute(query,params).fetchone()
        if not service: raise LookupError("Atención no encontrada")
        return [dict(row) for row in conn.execute("SELECT * FROM payments WHERE studio_id=? AND performed_service_id=? AND status='ACTIVO' ORDER BY received_at,id",(studio_id,service_id)).fetchall()]
    finally: conn.close()
def create_payment(studio_id,service_id,payload,actor_id,idempotency_key):
    fingerprint=_fingerprint({"performed_service_id":service_id,**payload}); conn=connection()
    try:
        conn.execute("BEGIN IMMEDIATE"); prior=conn.execute("SELECT * FROM payments WHERE studio_id=? AND idempotency_key=?",(studio_id,idempotency_key)).fetchone()
        if prior:
            if prior["request_fingerprint"]==fingerprint: conn.commit(); return dict(prior)
            raise PaymentConflict("La clave de idempotencia ya fue usada con otro payload")
        operating_date=datetime.now(SANTIAGO).date().isoformat(); ensure_day_open(conn,studio_id,operating_date)
        service=conn.execute("SELECT final_price_clp FROM performed_services WHERE id=? AND studio_id=? AND status='CONFIRMADO'",(service_id,studio_id)).fetchone()
        if not service: raise LookupError("Atención no encontrada")
        paid=conn.execute("SELECT COALESCE(SUM(amount_clp),0) AS total FROM payments WHERE studio_id=? AND performed_service_id=? AND status='ACTIVO'",(studio_id,service_id)).fetchone()["total"]
        if paid+payload["amount_clp"]>service["final_price_clp"]: raise PaymentValidationError("El cobro excede el saldo pendiente")
        now=datetime.now(SANTIAGO).isoformat(); record={"id":str(uuid4()),"studio_id":studio_id,"performed_service_id":service_id,"amount_clp":payload["amount_clp"],"method":payload["method"],"status":"ACTIVO","received_at":now,"actor_id":actor_id,"idempotency_key":idempotency_key,"request_fingerprint":fingerprint,"created_at":now}
        conn.execute("""INSERT INTO payments(id,studio_id,performed_service_id,amount_clp,method,status,received_at,actor_id,idempotency_key,request_fingerprint,created_at) VALUES(:id,:studio_id,:performed_service_id,:amount_clp,:method,:status,:received_at,:actor_id,:idempotency_key,:request_fingerprint,:created_at)""",record)
        conn.execute("INSERT INTO audit_events(id,studio_id,actor_id,action,entity_type,entity_id,idempotency_key,created_at) VALUES(?,?,?,?,?,?,?,?)",(str(uuid4()),studio_id,actor_id,"CREATE_PAYMENT","payment",record["id"],idempotency_key,now)); conn.commit(); return record
    except Exception: conn.rollback(); raise
    finally: conn.close()
