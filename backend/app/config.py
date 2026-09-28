import os
import logging
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
ENVIRONMENT=os.getenv("ENVIRONMENT","development")
DATABASE_URL=os.getenv("DATABASE_URL","estetica.db")
DEVELOPMENT_STUDIO_ID=os.getenv("DEVELOPMENT_STUDIO_ID","development-studio")
JWT_ALGORITHM="HS256"
JWT_SECRET=os.getenv("JWT_SECRET","development-only-change-me")
JWT_ISSUER=os.getenv("JWT_ISSUER","estetica-api")
FRONTEND_ORIGINS=tuple(x.strip() for x in os.getenv("FRONTEND_ORIGINS","http://127.0.0.1:5173,http://localhost:5173").split(",") if x.strip())
_default_backup_dir=Path(os.getenv("TEMP", ".")) / "estetica-private-backups"
BACKUP_DIR=Path(os.getenv("BACKUP_DIR",str(_default_backup_dir))).expanduser()
BACKUP_RETENTION_DAYS=int(os.getenv("BACKUP_RETENTION_DAYS","30"))
LOG_LEVEL=os.getenv("LOG_LEVEL","INFO").upper()
DEBUG=os.getenv("DEBUG","false").lower() in {"1","true","yes"}
def configure_logging():
    level=getattr(logging,LOG_LEVEL,logging.INFO)
    logging.basicConfig(level=level,format="%(asctime)s %(levelname)s %(name)s %(message)s")
    # Application code must log outcomes only, never request payloads or credentials.
    logging.getLogger("uvicorn.access").setLevel(level)
def validate_config():
    if ENVIRONMENT!="development" and JWT_SECRET in {"development-only-change-me", "replace-with-a-long-random-secret", ""}: raise RuntimeError("JWT_SECRET debe configurarse fuera de desarrollo")
    if BACKUP_RETENTION_DAYS < 1: raise RuntimeError("BACKUP_RETENTION_DAYS debe ser al menos 1")
    if ENVIRONMENT!="development" and not os.getenv("BACKUP_DIR"): raise RuntimeError("BACKUP_DIR privado y persistente debe configurarse fuera de desarrollo")
    if ENVIRONMENT!="development" and DEBUG: raise RuntimeError("DEBUG debe permanecer desactivado fuera de desarrollo")
    project_root=Path(__file__).resolve().parents[2]
    try: BACKUP_DIR.resolve().relative_to(project_root)
    except ValueError: pass
    else: raise RuntimeError("BACKUP_DIR no puede estar dentro del árbol de la aplicación o del frontend")
