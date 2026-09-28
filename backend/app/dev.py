import argparse
from datetime import datetime,timezone
from uuid import uuid4
from .auth import issue_development_token
from .database import connection,init_db
def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--email",required=True); parser.add_argument("--studio",default="Estética desarrollo"); args=parser.parse_args(); init_db(); conn=connection()
    studio=conn.execute("SELECT id FROM studios WHERE name=?",(args.studio,)).fetchone(); studio_id=studio["id"] if studio else str(uuid4())
    if not studio: conn.execute("INSERT INTO studios(id,name,timezone) VALUES(?,?,?)",(studio_id,args.studio,"America/Santiago"))
    user=conn.execute("SELECT id FROM users WHERE email=?",(args.email,)).fetchone(); user_id=user["id"] if user else str(uuid4())
    if not user:
        columns={row["name"] for row in conn.execute("PRAGMA table_info(users)")}; fields=["id","email","created_at"]; values=[user_id,args.email,datetime.now(timezone.utc).isoformat()]
        for name,value in (("studio_id",studio_id),("name",args.email),("role","OWNER_ADMIN"),("active",1)):
            if name in columns: fields.append(name); values.append(value)
        conn.execute(f"INSERT INTO users({','.join(fields)}) VALUES({','.join('?' for _ in fields)})",values)
    conn.execute("INSERT OR IGNORE INTO studio_memberships(studio_id,user_id,role) VALUES(?,?,?)",(studio_id,user_id,"OWNER_ADMIN")); conn.commit(); conn.close(); print(f"STUDIO_ID={studio_id}"); print(f"TOKEN={issue_development_token(user_id)}")
if __name__=="__main__": main()
