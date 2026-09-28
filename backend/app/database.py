import sqlite3
from .config import DATABASE_URL, DEVELOPMENT_STUDIO_ID
def connection():
    conn=sqlite3.connect(DATABASE_URL); conn.row_factory=sqlite3.Row; conn.execute("PRAGMA foreign_keys = ON"); return conn
def _add_column_if_missing(conn, table, definition):
    if definition.split()[0] not in {r["name"] for r in conn.execute(f"PRAGMA table_info({table})")}: conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")
def _migrate_legacy_appointments(conn):
    columns={row["name"] for row in conn.execute("PRAGMA table_info(appointments)")}
    if "service_id" not in columns: return
    # The early prototype linked appointments to a now-unused service_catalog.
    # Rebuild while preserving the records and using its service_id as snapshot text.
    conn.execute("PRAGMA foreign_keys=OFF")
    conn.executescript("""
    CREATE TABLE appointments_current (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,client_id TEXT NOT NULL,professional_id TEXT NOT NULL,service_name TEXT NOT NULL,start_at TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('PROGRAMADA','CANCELADA','NO_ASISTIO','ATENDIDA')),created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor_id TEXT NOT NULL);
    INSERT INTO appointments_current(id,studio_id,client_id,professional_id,service_name,start_at,status,created_at,updated_at,actor_id)
    SELECT id,studio_id,client_id,professional_id,COALESCE(NULLIF(service_name,''),service_id),start_at,status,created_at,COALESCE(updated_at,created_at),COALESCE(actor_id,'') FROM appointments;
    DROP TABLE appointments;
    ALTER TABLE appointments_current RENAME TO appointments;
    """)
    conn.execute("PRAGMA foreign_keys=ON")
def init_db():
    conn=connection(); conn.executescript("""
    CREATE TABLE IF NOT EXISTS studios (id TEXT PRIMARY KEY,name TEXT NOT NULL,timezone TEXT NOT NULL DEFAULT 'America/Santiago');
    CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY,email TEXT NOT NULL UNIQUE,active INTEGER NOT NULL DEFAULT 1,created_at TEXT NOT NULL);
    CREATE TABLE IF NOT EXISTS studio_memberships (studio_id TEXT NOT NULL,user_id TEXT NOT NULL,role TEXT NOT NULL CHECK(role IN ('OWNER_ADMIN','PROFESSIONAL')),PRIMARY KEY(studio_id,user_id),FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(user_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS performed_services (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,appointment_id TEXT,professional_id TEXT,service_id TEXT,professional_name TEXT NOT NULL,service_name TEXT NOT NULL,list_price_clp INTEGER NOT NULL CHECK(list_price_clp >= 0),discount_clp INTEGER NOT NULL CHECK(discount_clp >= 0 AND discount_clp <= list_price_clp),commission_percentage TEXT NOT NULL,materials_provider TEXT NOT NULL CHECK(materials_provider IN ('LOCAL','PROFESSIONAL','MIXTO')),operating_date TEXT NOT NULL,final_price_clp INTEGER NOT NULL CHECK(final_price_clp >= 0),commission_clp INTEGER NOT NULL CHECK(commission_clp >= 0),studio_share_clp INTEGER NOT NULL CHECK(studio_share_clp >= 0),status TEXT NOT NULL CHECK(status='CONFIRMADO'),created_at TEXT NOT NULL,actor_id TEXT,idempotency_key TEXT,request_fingerprint TEXT,FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(actor_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS clients (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,name TEXT NOT NULL,contact TEXT,created_at TEXT NOT NULL,updated_at TEXT NOT NULL,FOREIGN KEY(studio_id) REFERENCES studios(id));
    CREATE TABLE IF NOT EXISTS appointments (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,client_id TEXT NOT NULL,professional_id TEXT NOT NULL,service_name TEXT NOT NULL,start_at TEXT NOT NULL,status TEXT NOT NULL CHECK(status IN ('PROGRAMADA','CANCELADA','NO_ASISTIO','ATENDIDA')),created_at TEXT NOT NULL,updated_at TEXT NOT NULL,actor_id TEXT NOT NULL,FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(client_id) REFERENCES clients(id),FOREIGN KEY(actor_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS audit_events (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,actor_id TEXT NOT NULL,action TEXT NOT NULL,entity_type TEXT NOT NULL,entity_id TEXT NOT NULL,idempotency_key TEXT,created_at TEXT NOT NULL,FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(actor_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS payments (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,performed_service_id TEXT NOT NULL,amount_clp INTEGER NOT NULL CHECK(amount_clp > 0),method TEXT NOT NULL CHECK(method IN ('EFECTIVO','TRANSFERENCIA','TARJETA','OTRO')),status TEXT NOT NULL CHECK(status='ACTIVO'),received_at TEXT NOT NULL,actor_id TEXT NOT NULL,idempotency_key TEXT NOT NULL,request_fingerprint TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(performed_service_id) REFERENCES performed_services(id),FOREIGN KEY(actor_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS financial_movements (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,operating_date TEXT NOT NULL,type TEXT NOT NULL CHECK(type IN ('OPERATING_EXPENSE','ADMIN_SALARY','OWNER_WITHDRAWAL')),amount_clp INTEGER NOT NULL CHECK(amount_clp > 0),method TEXT NOT NULL CHECK(method IN ('EFECTIVO','TRANSFERENCIA','TARJETA','OTRO')),paid INTEGER NOT NULL CHECK(paid IN (0,1)),note TEXT NOT NULL DEFAULT '',actor_id TEXT NOT NULL,idempotency_key TEXT NOT NULL,request_fingerprint TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(actor_id) REFERENCES users(id));
    CREATE TABLE IF NOT EXISTS cash_days (studio_id TEXT NOT NULL,operating_date TEXT NOT NULL,opening_cash_clp INTEGER NOT NULL DEFAULT 0 CHECK(opening_cash_clp >= 0),counted_cash_clp INTEGER,status TEXT NOT NULL DEFAULT 'OPEN' CHECK(status IN ('OPEN','CLOSED')),closed_at TEXT,PRIMARY KEY(studio_id,operating_date),FOREIGN KEY(studio_id) REFERENCES studios(id));
    CREATE TABLE IF NOT EXISTS cash_day_events (id TEXT PRIMARY KEY,studio_id TEXT NOT NULL,operating_date TEXT NOT NULL,action TEXT NOT NULL CHECK(action IN ('UPDATE_CASH','CLOSE_DAY','REOPEN_DAY')),opening_cash_clp INTEGER,counted_cash_clp INTEGER,expected_cash_clp INTEGER,difference_clp INTEGER,reason TEXT NOT NULL DEFAULT '',actor_id TEXT NOT NULL,idempotency_key TEXT NOT NULL,request_fingerprint TEXT NOT NULL,created_at TEXT NOT NULL,FOREIGN KEY(studio_id) REFERENCES studios(id),FOREIGN KEY(actor_id) REFERENCES users(id));
    """)
    # Compatibility with the earlier development schema, whose users table
    # did not yet contain the JWT identity fields.
    _add_column_if_missing(conn,"users","email TEXT")
    _add_column_if_missing(conn,"users","created_at TEXT")
    _add_column_if_missing(conn,"audit_events","idempotency_key TEXT")
    _add_column_if_missing(conn,"clients","contact TEXT")
    _add_column_if_missing(conn,"clients","updated_at TEXT")
    _add_column_if_missing(conn,"appointments","service_name TEXT NOT NULL DEFAULT ''")
    _add_column_if_missing(conn,"appointments","updated_at TEXT")
    _add_column_if_missing(conn,"appointments","actor_id TEXT")
    client_columns={row["name"] for row in conn.execute("PRAGMA table_info(clients)")}
    if "phone" in client_columns: conn.execute("UPDATE clients SET contact=phone WHERE contact IS NULL AND phone IS NOT NULL")
    _migrate_legacy_appointments(conn)
    for definition in ("appointment_id TEXT","actor_id TEXT","idempotency_key TEXT","request_fingerprint TEXT"): _add_column_if_missing(conn,"performed_services",definition)
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_performed_services_idempotency ON performed_services(studio_id,idempotency_key) WHERE idempotency_key IS NOT NULL")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_performed_services_studio_date ON performed_services(studio_id,operating_date,created_at)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_performed_services_appointment ON performed_services(studio_id,appointment_id) WHERE appointment_id IS NOT NULL")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_clients_studio_name ON clients(studio_id,name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_appointments_studio_start ON appointments(studio_id,start_at)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_payments_idempotency ON payments(studio_id,idempotency_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_payments_service ON payments(studio_id,performed_service_id,received_at)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_financial_movements_idempotency ON financial_movements(studio_id,idempotency_key)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_financial_movements_day ON financial_movements(studio_id,operating_date,created_at)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_cash_day_events_idempotency ON cash_day_events(studio_id,idempotency_key)")
    conn.execute("INSERT OR IGNORE INTO studios(id,name,timezone) VALUES(?,?,?)",(DEVELOPMENT_STUDIO_ID,"Estética desarrollo","America/Santiago")); conn.commit(); conn.close()
