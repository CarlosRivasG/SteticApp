"""Private studio exports. Authentication is enforced by the route, scoping here is defense in depth."""
from csv import DictWriter
from datetime import datetime, timezone
from io import BytesIO, StringIO
from zipfile import ZIP_DEFLATED, ZipFile
from .database import connection

EXPORTS=(
    ("studio.csv", "SELECT id,name,timezone FROM studios WHERE id=?", ("id","name","timezone")),
    ("clients.csv", "SELECT id,studio_id,name,contact,created_at,updated_at FROM clients WHERE studio_id=? ORDER BY created_at,id", ("id","studio_id","name","contact","created_at","updated_at")),
    ("appointments.csv", "SELECT id,studio_id,client_id,professional_id,service_name,start_at,status,created_at,updated_at,actor_id FROM appointments WHERE studio_id=? ORDER BY start_at,id", ("id","studio_id","client_id","professional_id","service_name","start_at","status","created_at","updated_at","actor_id")),
    ("performed_services.csv", "SELECT id,studio_id,appointment_id,professional_id,service_id,professional_name,service_name,list_price_clp,discount_clp,commission_percentage,materials_provider,operating_date,final_price_clp,commission_clp,studio_share_clp,status,created_at,actor_id FROM performed_services WHERE studio_id=? ORDER BY operating_date,created_at,id", ("id","studio_id","appointment_id","professional_id","service_id","professional_name","service_name","list_price_clp","discount_clp","commission_percentage","materials_provider","operating_date","final_price_clp","commission_clp","studio_share_clp","status","created_at","actor_id")),
    ("payments.csv", "SELECT id,studio_id,performed_service_id,amount_clp,method,status,received_at,actor_id,created_at FROM payments WHERE studio_id=? ORDER BY received_at,created_at,id", ("id","studio_id","performed_service_id","amount_clp","method","status","received_at","actor_id","created_at")),
    ("financial_movements.csv", "SELECT id,studio_id,operating_date,type,amount_clp,method,paid,note,actor_id,created_at FROM financial_movements WHERE studio_id=? ORDER BY operating_date,created_at,id", ("id","studio_id","operating_date","type","amount_clp","method","paid","note","actor_id","created_at")),
    ("cash_days.csv", "SELECT studio_id,operating_date,opening_cash_clp,counted_cash_clp,status,closed_at FROM cash_days WHERE studio_id=? ORDER BY operating_date", ("studio_id","operating_date","opening_cash_clp","counted_cash_clp","status","closed_at")),
    ("cash_day_events.csv", "SELECT id,studio_id,operating_date,action,opening_cash_clp,counted_cash_clp,expected_cash_clp,difference_clp,reason,actor_id,created_at FROM cash_day_events WHERE studio_id=? ORDER BY operating_date,created_at,id", ("id","studio_id","operating_date","action","opening_cash_clp","counted_cash_clp","expected_cash_clp","difference_clp","reason","actor_id","created_at")),
    ("audit_events.csv", "SELECT id,studio_id,actor_id,action,entity_type,entity_id,created_at FROM audit_events WHERE studio_id=? ORDER BY created_at,id", ("id","studio_id","actor_id","action","entity_type","entity_id","created_at")),
)

def _csv(rows, explicit_columns=None):
    columns=list(explicit_columns or (rows[0].keys() if rows else []))
    text=StringIO(newline="")
    writer=DictWriter(text,fieldnames=columns,extrasaction="ignore",lineterminator="\r\n")
    writer.writeheader(); writer.writerows(rows)
    return text.getvalue().encode("utf-8")

def build_studio_export(studio_id):
    """Return a UTF-8 ZIP without auth credentials, hashes, idempotency data or request fingerprints."""
    conn=connection()
    try:
        result=BytesIO()
        with ZipFile(result,"w",ZIP_DEFLATED) as archive:
            for filename,query,columns in EXPORTS:
                archive.writestr(filename,_csv([dict(row) for row in conn.execute(query,(studio_id,))],columns))
            archive.writestr("README.txt",("Exportación StetiApp\n"+f"Estudio: {studio_id}\nGenerada: {datetime.now(timezone.utc).isoformat()}\n"+"CSV UTF-8 con cabeceras. Fechas ISO 8601; importes CLP como enteros.\n").encode("utf-8"))
        return result.getvalue()
    finally: conn.close()
