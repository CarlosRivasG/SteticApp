from datetime import date
from fastapi import Depends,FastAPI,Header,HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from .auth import get_current_user,require_studio_membership,require_owner_admin
from .config import DEBUG,FRONTEND_ORIGINS,configure_logging,validate_config
from .database import init_db
from .performed_services import IdempotencyConflict,create_performed_service,list_performed_services
from .payments import PaymentConflict,PaymentValidationError,create_payment,list_payments
from .cash import CashConflict,DayClosed,close_day,create_movement,daily_summary,reopen_day,update_cash_day,weekly_summary
from .agenda import create_appointment,create_client,list_appointments,list_clients,set_appointment_status,update_appointment,update_client
from .backups import maybe_create_daily_backup
from .exports import build_studio_export
from .schemas import AppointmentCreate,AppointmentStatusUpdate,AppointmentUpdate,CashDayUpdate,ClientCreate,ClientUpdate,CloseDayCreate,MovementCreate,PaymentCreate,PerformedServiceCreate,ReopenDayCreate
app=FastAPI(title="Estética API",version="0.3.0",debug=DEBUG)
app.add_middleware(CORSMiddleware,allow_origins=list(FRONTEND_ORIGINS),allow_credentials=False,allow_methods=["GET","POST","PUT"],allow_headers=["Content-Type","Idempotency-Key","Authorization"])
@app.on_event("startup")
async def startup(): configure_logging(); validate_config(); init_db(); maybe_create_daily_backup()
@app.get("/health")
async def health(): return {"status":"ok"}
@app.get("/studios/{studio_id}/exports/csv")
async def export_studio(studio_id:str,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    content=build_studio_export(studio_id)
    return Response(content=content,media_type="application/zip",headers={"Content-Disposition":'attachment; filename="stetiapp-export.zip"'})
@app.get("/studios/{studio_id}/clients")
async def clients(studio_id:str,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id); return {"items":list_clients(studio_id)}
@app.post("/studios/{studio_id}/clients",status_code=201)
async def create_client_route(studio_id:str,request:ClientCreate,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id); return create_client(studio_id,request.model_dump(),user.id)
@app.put("/studios/{studio_id}/clients/{client_id}")
async def update_client_route(studio_id:str,client_id:str,request:ClientUpdate,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return update_client(studio_id,client_id,request.model_dump(),user.id)
    except LookupError as error: raise HTTPException(status_code=404,detail=str(error))
@app.get("/studios/{studio_id}/appointments")
async def appointments(studio_id:str,user=Depends(get_current_user)):
    role=require_studio_membership(user,studio_id); return {"items":list_appointments(studio_id,user.id if role=="PROFESSIONAL" else None)}
@app.post("/studios/{studio_id}/appointments",status_code=201)
async def create_appointment_route(studio_id:str,request:AppointmentCreate,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return create_appointment(studio_id,request.model_dump(),user.id)
    except LookupError as error: raise HTTPException(status_code=404,detail=str(error))
@app.put("/studios/{studio_id}/appointments/{appointment_id}")
async def update_appointment_route(studio_id:str,appointment_id:str,request:AppointmentUpdate,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return update_appointment(studio_id,appointment_id,request.model_dump(),user.id)
    except LookupError as error: raise HTTPException(status_code=404,detail=str(error))
    except ValueError as error: raise HTTPException(status_code=409,detail=str(error))
@app.post("/studios/{studio_id}/appointments/{appointment_id}/status")
async def appointment_status_route(studio_id:str,appointment_id:str,request:AppointmentStatusUpdate,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return set_appointment_status(studio_id,appointment_id,request.model_dump(),user.id)
    except LookupError as error: raise HTTPException(status_code=404,detail=str(error))
    except ValueError as error: raise HTTPException(status_code=409,detail=str(error))
@app.get("/studios/{studio_id}/performed-services")
async def performed_services(studio_id:str,user=Depends(get_current_user)):
    role=require_studio_membership(user,studio_id); return {"items":list_performed_services(studio_id,user.id if role=="PROFESSIONAL" else None)}
@app.post("/studios/{studio_id}/performed-services",status_code=201)
async def confirm_performed_service(studio_id:str,request:PerformedServiceCreate,idempotency_key:str=Header(alias="Idempotency-Key",min_length=1,max_length=128),user=Depends(get_current_user)):
    require_studio_membership(user,studio_id)
    try: return create_performed_service(studio_id,request.model_dump(),user.id,idempotency_key)
    except IdempotencyConflict as error: raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(error))
    except DayClosed as error: raise HTTPException(status_code=409,detail=str(error))
@app.get("/studios/{studio_id}/performed-services/{service_id}/payments")
async def payments(studio_id:str,service_id:str,user=Depends(get_current_user)):
    role=require_studio_membership(user,studio_id)
    try: return {"items":list_payments(studio_id,service_id,user.id if role=="PROFESSIONAL" else None)}
    except LookupError as error: raise HTTPException(status_code=404,detail=str(error))
@app.post("/studios/{studio_id}/performed-services/{service_id}/payments",status_code=201)
async def register_payment(studio_id:str,service_id:str,request:PaymentCreate,idempotency_key:str=Header(alias="Idempotency-Key",min_length=1,max_length=128),user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return create_payment(studio_id,service_id,request.model_dump(),user.id,idempotency_key)
    except LookupError as error: raise HTTPException(status_code=404,detail=str(error))
    except PaymentConflict as error: raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail=str(error))
    except PaymentValidationError as error: raise HTTPException(status_code=422,detail=str(error))
    except DayClosed as error: raise HTTPException(status_code=409,detail=str(error))
@app.get("/studios/{studio_id}/summaries/daily")
async def daily(studio_id:str,operating_date:date,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id); return daily_summary(studio_id,operating_date.isoformat())
@app.get("/studios/{studio_id}/summaries/weekly")
async def weekly(studio_id:str,week_start:date,user=Depends(get_current_user)):
    require_owner_admin(user,studio_id); return weekly_summary(studio_id,week_start.isoformat())
@app.post("/studios/{studio_id}/movements",status_code=201)
async def movement(studio_id:str,request:MovementCreate,idempotency_key:str=Header(alias="Idempotency-Key",min_length=1,max_length=128),user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return create_movement(studio_id,request.model_dump(),user.id,idempotency_key)
    except CashConflict as error: raise HTTPException(status_code=409,detail=str(error))
    except DayClosed as error: raise HTTPException(status_code=409,detail=str(error))
@app.put("/studios/{studio_id}/cash-days/{operating_date}")
async def cash_day(studio_id:str,operating_date:date,request:CashDayUpdate,idempotency_key:str=Header(alias="Idempotency-Key",min_length=1,max_length=128),user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return update_cash_day(studio_id,operating_date.isoformat(),request.model_dump(exclude_none=True),user.id,idempotency_key)
    except CashConflict as error: raise HTTPException(status_code=409,detail=str(error))
    except DayClosed as error: raise HTTPException(status_code=409,detail=str(error))
@app.post("/studios/{studio_id}/cash-days/{operating_date}/close")
async def close(studio_id:str,operating_date:date,request:CloseDayCreate,idempotency_key:str=Header(alias="Idempotency-Key",min_length=1,max_length=128),user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return close_day(studio_id,operating_date.isoformat(),request.model_dump(),user.id,idempotency_key)
    except CashConflict as error: raise HTTPException(status_code=409,detail=str(error))
    except DayClosed as error: raise HTTPException(status_code=409,detail=str(error))
@app.post("/studios/{studio_id}/cash-days/{operating_date}/reopen")
async def reopen(studio_id:str,operating_date:date,request:ReopenDayCreate,idempotency_key:str=Header(alias="Idempotency-Key",min_length=1,max_length=128),user=Depends(get_current_user)):
    require_owner_admin(user,studio_id)
    try: return reopen_day(studio_id,operating_date.isoformat(),request.model_dump(),user.id,idempotency_key)
    except CashConflict as error: raise HTTPException(status_code=409,detail=str(error))
    except DayClosed as error: raise HTTPException(status_code=409,detail=str(error))
