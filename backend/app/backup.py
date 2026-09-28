"""Run from a private scheduler: python -m app.backup"""
from .backups import create_backup
from .config import validate_config
from .database import init_db

def main():
    validate_config(); init_db()
    result=create_backup()
    print(f"Backup creado: {result['filename']} ({result['size_bytes']} bytes, integrity={result['integrity']})")
if __name__=="__main__": main()
