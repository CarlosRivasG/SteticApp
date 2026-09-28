from datetime import datetime
from uuid import uuid4
from zoneinfo import ZoneInfo
from .database import connection

SANTIAGO=ZoneInfo("America/Santiago")

def _now(): return datetime.now(SANTIAGO).isoformat()
def _start(value): return (value.replace(tzinfo=SANTIAGO) if value.tzinfo is None else value.astimezone(SANTIAGO)).isoformat()
def _audit(conn,studio,actor,action,entity,now): conn.execute("INSERT INTO audit_events(id,studio_id,actor_id,action,entity_type,entity_id,created_at) VALUES(?,?,?,?,?,?,?)",(str(uuid4()),studio,actor,action,"appointment",entity,now))

def list_clients(studio_id):
    conn=connection()
    try: return [dict(row) for row in conn.execute("SELECT * FROM clients WHERE studio_id=? ORDER BY name,id",(studio_id,))]
    finally: conn.close()
def create_client(studio_id,payload,actor):
    conn=connection(); now=_now(); record={"id":str(uuid4()),"studio_id":studio_id,"name":payload["name"].strip(),"contact":payload.get("contact") or None,"created_at":now,"updated_at":now}
    try: conn.execute("INSERT INTO clients(id,studio_id,name,contact,created_at,updated_at) VALUES(:id,:studio_id,:name,:contact,:created_at,:updated_at)",record); _audit(conn,studio_id,actor,"CREATE_CLIENT",record["id"],now); conn.commit(); return record
    finally: conn.close()
def update_client(studio_id,client_id,payload,actor):
    conn=connection(); now=_now()
    try:
        row=conn.execute("SELECT id FROM clients WHERE id=? AND studio_id=?",(client_id,studio_id)).fetchone()
        if not row: raise LookupError("Clienta no encontrada")
        conn.execute("UPDATE clients SET name=?,contact=?,updated_at=? WHERE id=? AND studio_id=?",(payload["name"].strip(),payload.get("contact") or None,now,client_id,studio_id)); _audit(conn,studio_id,actor,"UPDATE_CLIENT",client_id,now); conn.commit(); return dict(conn.execute("SELECT * FROM clients WHERE id=?",(client_id,)).fetchone())
    finally: conn.close()
def list_appointments(studio_id,professional_id=None):
    conn=connection()
    try:
        query="SELECT a.*,c.name client_name,c.contact client_contact FROM appointments a JOIN clients c ON c.id=a.client_id AND c.studio_id=a.studio_id WHERE a.studio_id=?"; params=[studio_id]
        if professional_id is not None: query+=" AND a.professional_id=?"; params.append(professional_id)
        return [dict(row) for row in conn.execute(query+" ORDER BY a.start_at,a.id",params)]
    finally: conn.close()
def _assert_client(conn,studio,client):
    if not conn.execute("SELECT id FROM clients WHERE id=? AND studio_id=?",(client,studio)).fetchone(): raise LookupError("Clienta no encontrada")
def create_appointment(studio,payload,actor):
    conn=connection(); now=_now(); start=_start(payload["start_at"])
    try:
        _assert_client(conn,studio,payload["client_id"]); record={"id":str(uuid4()),"studio_id":studio,"client_id":payload["client_id"],"professional_id":payload["professional_id"],"service_name":payload["service_name"].strip(),"start_at":start,"status":"PROGRAMADA","created_at":now,"updated_at":now,"actor_id":actor}
        # Older local databases required service_id, end_at and source. Keep them
        # populated while the current model uses the service name snapshot.
        columns={row["name"] for row in conn.execute("PRAGMA table_info(appointments)")}
        record.update({"service_id":record["service_name"],"end_at":start,"source":"MANUAL"})
        fields=[field for field in record if field in columns]
        conn.execute(f"INSERT INTO appointments({','.join(fields)}) VALUES({','.join(':'+field for field in fields)})",{field:record[field] for field in fields}); _audit(conn,studio,actor,"CREATE_APPOINTMENT",record["id"],now); conn.commit(); return record
    finally: conn.close()
def update_appointment(studio,appointment_id,payload,actor):
    conn=connection(); now=_now()
    try:
        row=conn.execute("SELECT status FROM appointments WHERE id=? AND studio_id=?",(appointment_id,studio)).fetchone()
        if not row: raise LookupError("Cita no encontrada")
        if row["status"]!="PROGRAMADA": raise ValueError("Solo se puede reprogramar una cita programada")
        _assert_client(conn,studio,payload["client_id"]); conn.execute("UPDATE appointments SET client_id=?,professional_id=?,service_name=?,start_at=?,updated_at=? WHERE id=? AND studio_id=?",(payload["client_id"],payload["professional_id"],payload["service_name"].strip(),_start(payload["start_at"]),now,appointment_id,studio)); _audit(conn,studio,actor,"UPDATE_APPOINTMENT",appointment_id,now); conn.commit(); return dict(conn.execute("SELECT * FROM appointments WHERE id=?",(appointment_id,)).fetchone())
    finally: conn.close()
def set_appointment_status(studio,appointment_id,payload,actor):
    conn=connection(); now=_now()
    try:
        row=conn.execute("SELECT status FROM appointments WHERE id=? AND studio_id=?",(appointment_id,studio)).fetchone()
        if not row: raise LookupError("Cita no encontrada")
        if row["status"]!="PROGRAMADA": raise ValueError("La cita ya no está programada")
        conn.execute("UPDATE appointments SET status=?,updated_at=? WHERE id=? AND studio_id=?",(payload["status"],now,appointment_id,studio)); _audit(conn,studio,actor,payload["status"],appointment_id,now); conn.commit(); return dict(conn.execute("SELECT * FROM appointments WHERE id=?",(appointment_id,)).fetchone())
    finally: conn.close()
def appointment_for_service(conn,studio,appointment_id):
    row=conn.execute("SELECT id FROM appointments WHERE id=? AND studio_id=? AND status='ATENDIDA'",(appointment_id,studio)).fetchone()
    if not row: raise ValueError("La cita debe estar atendida y pertenecer al estudio")
    if conn.execute("SELECT id FROM performed_services WHERE studio_id=? AND appointment_id=?",(studio,appointment_id)).fetchone(): raise ValueError("La cita ya tiene una atención asociada")
