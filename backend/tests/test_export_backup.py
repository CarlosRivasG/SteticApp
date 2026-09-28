import csv
from io import BytesIO, TextIOWrapper
from zipfile import ZipFile
from fastapi.testclient import TestClient
from app import database
from app.auth import issue_development_token
from app.backups import create_backup,verify_restore_isolated
from app.main import app

def seed(conn,user,studio,role="OWNER_ADMIN"):
    conn.execute("INSERT OR IGNORE INTO studios(id,name,timezone) VALUES(?,?,?)",(studio,studio,"America/Santiago"))
    conn.execute("INSERT INTO users(id,email,created_at) VALUES(?,?,?)",(user,f"{user}@test.local","2026-01-01T00:00:00+00:00"))
    conn.execute("INSERT INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",(studio,user,role)); conn.commit()

def test_export_is_scoped_authorized_and_backup_restores(monkeypatch,tmp_path):
    monkeypatch.setattr(database,"DATABASE_URL",str(tmp_path/"export.sqlite3"))
    with TestClient(app) as client:
        conn=database.connection(); seed(conn,"owner-a","studio-a"); seed(conn,"professional","studio-a","PROFESSIONAL"); seed(conn,"owner-b","studio-b")
        conn.execute("INSERT INTO clients(id,studio_id,name,contact,created_at,updated_at) VALUES(?,?,?,?,?,?)",("client-a","studio-a","Ana","9","2026-01-01T00:00:00+00:00","2026-01-01T00:00:00+00:00"))
        conn.execute("INSERT INTO clients(id,studio_id,name,contact,created_at,updated_at) VALUES(?,?,?,?,?,?)",("client-b","studio-b","Berta","8","2026-01-01T00:00:00+00:00","2026-01-01T00:00:00+00:00")); conn.commit(); conn.close()
        owner={"Authorization":f"Bearer {issue_development_token('owner-a')}"}; pro={"Authorization":f"Bearer {issue_development_token('professional')}"}; other={"Authorization":f"Bearer {issue_development_token('owner-b')}"}
        response=client.get("/studios/studio-a/exports/csv",headers=owner); assert response.status_code==200 and response.headers["content-type"].startswith("application/zip")
        assert client.get("/studios/studio-a/exports/csv",headers=pro).status_code==403
        assert client.get("/studios/studio-a/exports/csv",headers=other).status_code==403
        with ZipFile(BytesIO(response.content)) as archive:
            assert "performed_services.csv" in archive.namelist() and "users.csv" not in archive.namelist()
            rows=list(csv.DictReader(TextIOWrapper(archive.open("clients.csv"),encoding="utf-8")))
            assert [row["id"] for row in rows]==["client-a"]
    backup=create_backup(tmp_path/"private",30); restored=verify_restore_isolated(tmp_path/"private"/backup["filename"])
    assert backup["integrity"]=="ok" and backup["size_bytes"]>0 and restored["integrity"]=="ok"
