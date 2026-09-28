"""Private, consistent SQLite backups. There is intentionally no HTTP restore endpoint."""
import json, os, sqlite3, tempfile
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo
from . import database
from .config import BACKUP_DIR, BACKUP_RETENTION_DAYS

def _atomic_json(path, value):
    fd,tmp=tempfile.mkstemp(prefix=".backup-",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as file: json.dump(value,file,ensure_ascii=False)
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def create_backup(backup_dir=BACKUP_DIR, retention_days=BACKUP_RETENTION_DAYS):
    """Use SQLite's backup API, test integrity, then atomically publish the private file."""
    target_dir=Path(backup_dir); target_dir.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    destination=target_dir/f"stetiapp-{stamp}.sqlite3"
    fd,tmp=tempfile.mkstemp(prefix=".stetiapp-",suffix=".sqlite3",dir=target_dir); os.close(fd)
    try:
        source=database.connection(); destination_conn=sqlite3.connect(tmp)
        try: source.backup(destination_conn); destination_conn.commit()
        finally: destination_conn.close(); source.close()
        check_conn=sqlite3.connect(tmp)
        try: check=check_conn.execute("PRAGMA integrity_check").fetchone()[0]
        finally: check_conn.close()
        if check!="ok": raise RuntimeError("La copia SQLite no superó integrity_check")
        os.replace(tmp,destination)
        metadata={"created_at":datetime.now(timezone.utc).isoformat(),"filename":destination.name,"size_bytes":destination.stat().st_size,"integrity":"ok"}
        _atomic_json(destination.with_suffix(".json"),metadata)
        cutoff=datetime.now(timezone.utc).timestamp()-retention_days*86400
        for item in target_dir.glob("stetiapp-*"):
            if item.stat().st_mtime < cutoff: item.unlink()
        return metadata
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def verify_restore_isolated(backup_path):
    """Never replaces the active DB: restore only into a short-lived temp directory."""
    with tempfile.TemporaryDirectory(prefix="stetiapp-restore-") as temp:
        restored=Path(temp)/"restored.sqlite3"
        source=sqlite3.connect(backup_path); destination=sqlite3.connect(restored)
        try: source.backup(destination); destination.commit()
        finally: destination.close(); source.close()
        conn=sqlite3.connect(restored)
        try:
            check=conn.execute("PRAGMA integrity_check").fetchone()[0]
            if check!="ok": raise RuntimeError("La restauración de prueba no superó integrity_check")
            return {"integrity":check,"performed_services":conn.execute("SELECT COUNT(*) FROM performed_services").fetchone()[0]}
        finally: conn.close()

def maybe_create_daily_backup():
    day=datetime.now(ZoneInfo("America/Santiago")).strftime("%Y%m%d")
    if any(Path(BACKUP_DIR).glob(f"stetiapp-{day}T*.sqlite3")): return None
    return create_backup()
