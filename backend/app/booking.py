from datetime import datetime, timedelta
from uuid import uuid4
from .database import connection

def available_slots(studio_id: str, service_id: str, date: str, professional_id: str | None = None):
    """Returns available 30-minute starts between 09:00 and 20:00 for the requested service."""
    conn = connection()
    service = conn.execute("SELECT duration_minutes FROM service_catalog WHERE id=? AND studio_id=? AND active=1", (service_id, studio_id)).fetchone()
    if not service:
        conn.close(); raise ValueError("Servicio no encontrado")
    professionals = [professional_id] if professional_id else [r[0] for r in conn.execute("SELECT id FROM professionals WHERE studio_id=? AND active=1", (studio_id,)).fetchall()]
    slots = []
    for pid in professionals:
        cursor = datetime.fromisoformat(f"{date}T09:00:00")
        closing = datetime.fromisoformat(f"{date}T20:00:00")
        while cursor + timedelta(minutes=service['duration_minutes']) <= closing:
            end = cursor + timedelta(minutes=service['duration_minutes'])
            conflict = conn.execute("""SELECT 1 FROM appointments WHERE professional_id=? AND status='PROGRAMADA'
              AND start_at < ? AND end_at > ?""", (pid, end.isoformat(), cursor.isoformat())).fetchone()
            if not conflict: slots.append({"professional_id": pid, "start_at": cursor.isoformat(), "end_at": end.isoformat()})
            cursor += timedelta(minutes=30)
    conn.close()
    return slots

def create_appointment(studio_id: str, data: dict):
    conn = connection()
    service = conn.execute("SELECT * FROM service_catalog WHERE id=? AND studio_id=? AND active=1", (data['service_id'], studio_id)).fetchone()
    if not service: conn.close(); raise ValueError("Servicio no encontrado")
    client = conn.execute("SELECT * FROM clients WHERE studio_id=? AND phone IS ?", (studio_id, data.get('client_phone'))).fetchone()
    now = datetime.utcnow().isoformat()
    if not client:
        client_id = str(uuid4()); conn.execute("INSERT INTO clients(id,studio_id,name,phone,created_at) VALUES(?,?,?,?,?)", (client_id,studio_id,data['client_name'],data.get('client_phone'),now))
    else: client_id = client['id']
    start = datetime.fromisoformat(data['start_at'].replace('Z','+00:00')); end = start + timedelta(minutes=service['duration_minutes'])
    appointment_id = str(uuid4())
    conn.execute("""INSERT INTO appointments(id,studio_id,client_id,professional_id,service_id,start_at,end_at,status,source,created_at)
      VALUES(?,?,?,?,?,?,?,?,?,?)""", (appointment_id,studio_id,client_id,data.get('professional_id'),service['id'],start.isoformat(),end.isoformat(),'PROGRAMADA',data['source'],now))
    conn.commit(); conn.close()
    return {"id":appointment_id,"status":"PROGRAMADA","start_at":start.isoformat(),"end_at":end.isoformat(),"source":data['source']}
