import hashlib,json
from datetime import datetime
from decimal import Decimal,ROUND_HALF_UP
from uuid import uuid4
from zoneinfo import ZoneInfo
from .database import connection
from .cash import ensure_day_open
from .agenda import appointment_for_service
SANTIAGO=ZoneInfo("America/Santiago")
class IdempotencyConflict(ValueError): pass
def calculate_distribution(list_price_clp,discount_clp,commission_percentage):
    if list_price_clp<0 or discount_clp<0: raise ValueError("Los importes CLP no pueden ser negativos")
    if discount_clp>list_price_clp: raise ValueError("El descuento no puede superar el precio de lista")
    if commission_percentage<0 or commission_percentage>100: raise ValueError("El porcentaje debe estar entre 0 y 100")
    final=list_price_clp-discount_clp; commission=int((Decimal(final)*commission_percentage/Decimal("100")).quantize(Decimal("1"),rounding=ROUND_HALF_UP)); return final,commission,final-commission
def _fingerprint(payload):
    data={k:(v.isoformat() if hasattr(v,"isoformat") else str(v)) for k,v in payload.items()}; return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def create_performed_service(studio_id,payload,actor_id,idempotency_key):
    fingerprint=_fingerprint(payload); conn=connection()
    try:
        conn.execute("BEGIN IMMEDIATE"); prior=conn.execute("SELECT * FROM performed_services WHERE studio_id=? AND idempotency_key=?",(studio_id,idempotency_key)).fetchone()
        if prior:
            if prior["request_fingerprint"]==fingerprint: conn.commit(); return dict(prior)
            raise IdempotencyConflict("La clave de idempotencia ya fue usada con otro payload")
        operating_date=payload["operating_date"].isoformat(); ensure_day_open(conn,studio_id,operating_date); appointment_id=payload.get("appointment_id");
        if appointment_id: appointment_for_service(conn,studio_id,appointment_id)
        percentage=Decimal(str(payload["commission_percentage"])); final,commission,share=calculate_distribution(payload["list_price_clp"],payload["discount_clp"],percentage); now=datetime.now(SANTIAGO).isoformat(); record={"id":str(uuid4()),"studio_id":studio_id,"appointment_id":appointment_id,"professional_id":payload.get("professional_id"),"service_id":payload.get("service_id"),"professional_name":payload["professional_name"],"service_name":payload["service_name"],"list_price_clp":payload["list_price_clp"],"discount_clp":payload["discount_clp"],"commission_percentage":str(percentage),"materials_provider":payload["materials_provider"],"operating_date":operating_date,"final_price_clp":final,"commission_clp":commission,"studio_share_clp":share,"status":"CONFIRMADO","created_at":now,"actor_id":actor_id,"idempotency_key":idempotency_key,"request_fingerprint":fingerprint}
        conn.execute("""INSERT INTO performed_services(id,studio_id,appointment_id,professional_id,service_id,professional_name,service_name,list_price_clp,discount_clp,commission_percentage,materials_provider,operating_date,final_price_clp,commission_clp,studio_share_clp,status,created_at,actor_id,idempotency_key,request_fingerprint) VALUES(:id,:studio_id,:appointment_id,:professional_id,:service_id,:professional_name,:service_name,:list_price_clp,:discount_clp,:commission_percentage,:materials_provider,:operating_date,:final_price_clp,:commission_clp,:studio_share_clp,:status,:created_at,:actor_id,:idempotency_key,:request_fingerprint)""",record)
        conn.execute("INSERT INTO audit_events(id,studio_id,actor_id,action,entity_type,entity_id,idempotency_key,created_at) VALUES(?,?,?,?,?,?,?,?)",(str(uuid4()),studio_id,actor_id,"CREATE_PERFORMED_SERVICE","performed_service",record["id"],idempotency_key,now)); conn.commit(); return record
    except Exception: conn.rollback(); raise
    finally: conn.close()
def list_performed_services(studio_id,professional_id=None):
    conn=connection()
    try:
        query="SELECT * FROM performed_services WHERE studio_id=?"; params=[studio_id]
        if professional_id is not None: query+=" AND professional_id=?"; params.append(professional_id)
        services=[dict(row) for row in conn.execute(query+" ORDER BY operating_date DESC,created_at DESC",params).fetchall()]
        for service in services:
            service["payments"]=[dict(row) for row in conn.execute("SELECT * FROM payments WHERE studio_id=? AND performed_service_id=? AND status='ACTIVO' ORDER BY received_at,id",(studio_id,service["id"])).fetchall()]
        return services
    finally: conn.close()
