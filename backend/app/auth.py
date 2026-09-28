from dataclasses import dataclass
from datetime import datetime,timedelta,timezone
from uuid import uuid4
import jwt
from fastapi import Depends,HTTPException,status
from fastapi.security import HTTPAuthorizationCredentials,HTTPBearer
from .config import JWT_ALGORITHM,JWT_ISSUER,JWT_SECRET
from .database import connection
bearer_scheme=HTTPBearer()
@dataclass(frozen=True)
class AuthenticatedUser: id:str; email:str
def get_current_user(credentials:HTTPAuthorizationCredentials=Depends(bearer_scheme)):
    try:
        payload=jwt.decode(credentials.credentials,JWT_SECRET,algorithms=[JWT_ALGORITHM],issuer=JWT_ISSUER); user_id=payload.get("sub")
        if not isinstance(user_id,str) or not user_id: raise jwt.InvalidTokenError()
    except jwt.PyJWTError: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Token inválido")
    conn=connection(); row=conn.execute("SELECT id,email FROM users WHERE id=? AND active=1",(user_id,)).fetchone(); conn.close()
    if not row: raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Usuario no autorizado")
    return AuthenticatedUser(row["id"],row["email"])
def require_studio_membership(user,studio_id):
    conn=connection(); row=conn.execute("SELECT role FROM studio_memberships WHERE user_id=? AND studio_id=?",(user.id,studio_id)).fetchone(); conn.close()
    if not row: raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="No tienes acceso a este estudio")
    return row["role"]
def require_owner_admin(user,studio_id):
    role=require_studio_membership(user,studio_id)
    if role!="OWNER_ADMIN": raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Solo una administradora puede realizar esta operación")
    return role
def issue_development_token(user_id):
    now=datetime.now(timezone.utc); return jwt.encode({"sub":user_id,"iss":JWT_ISSUER,"iat":now,"exp":now+timedelta(hours=8),"jti":str(uuid4())},JWT_SECRET,algorithm=JWT_ALGORITHM)
