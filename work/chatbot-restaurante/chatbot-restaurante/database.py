import sqlite3
from config import DATABASE_URL

def get_conn():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS restaurantes (
            id TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            whatsapp_number TEXT,
            menu_path TEXT,
            horario TEXT,
            activo INTEGER DEFAULT 1,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS conversaciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurante_id TEXT NOT NULL,
            cliente_numero TEXT NOT NULL,
            rol TEXT NOT NULL,
            mensaje TEXT NOT NULL,
            creado_en TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurante_id) REFERENCES restaurantes(id)
        );
    """)
    conn.commit()
    existe = conn.execute("SELECT id FROM restaurantes WHERE id='demo'").fetchone()
    if not existe:
        conn.execute("""
            INSERT INTO restaurantes (id, nombre, whatsapp_number, menu_path, horario)
            VALUES ('demo', 'Restaurante Demo', '+56912345678',
                    'menus/restaurante_demo.json', 'Lunes a Domingo 12:00-23:00')
        """)
        conn.commit()
    conn.close()

def get_restaurante_by_number(numero: str):
    conn = get_conn()
    r = conn.execute(
        "SELECT * FROM restaurantes WHERE whatsapp_number=? AND activo=1", (numero,)
    ).fetchone()
    conn.close()
    return dict(r) if r else None

def get_historial(restaurante_id: str, cliente_numero: str, limite: int = 10):
    conn = get_conn()
    rows = conn.execute("""
        SELECT rol, mensaje FROM conversaciones
        WHERE restaurante_id=? AND cliente_numero=?
        ORDER BY id DESC LIMIT ?
    """, (restaurante_id, cliente_numero, limite)).fetchall()
    conn.close()
    return [{"role": r["rol"], "content": r["mensaje"]} for r in reversed(rows)]

def guardar_mensaje(restaurante_id: str, cliente_numero: str, rol: str, mensaje: str):
    conn = get_conn()
    conn.execute("""
        INSERT INTO conversaciones (restaurante_id, cliente_numero, rol, mensaje)
        VALUES (?, ?, ?, ?)
    """, (restaurante_id, cliente_numero, rol, mensaje))
    conn.commit()
    conn.close()
