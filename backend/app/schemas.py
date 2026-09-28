from datetime import date,datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel,ConfigDict,Field,field_validator,model_validator
class ApiModel(BaseModel): model_config=ConfigDict(extra="forbid")
class PerformedServiceCreate(ApiModel):
    appointment_id:str|None=Field(default=None,max_length=100)
    professional_id:str|None=Field(default=None,max_length=100); service_id:str|None=Field(default=None,max_length=100)
    professional_name:str=Field(min_length=1,max_length=100); service_name:str=Field(min_length=1,max_length=100)
    list_price_clp:int=Field(strict=True,ge=0); discount_clp:int=Field(strict=True,ge=0)
    commission_percentage:Decimal=Field(ge=Decimal("0"),le=Decimal("100"),max_digits=5,decimal_places=2)
    materials_provider:Literal["LOCAL","PROFESSIONAL","MIXTO"]; operating_date:date
    @field_validator("professional_name","service_name")
    @classmethod
    def names(cls,value):
        if not value.strip(): raise ValueError("No puede estar vacío")
        return value.strip()
    @field_validator("discount_clp")
    @classmethod
    def discount(cls,value,info):
        if (price:=info.data.get("list_price_clp")) is not None and value>price: raise ValueError("El descuento no puede superar el precio de lista")
        return value
class PaymentCreate(ApiModel):
    amount_clp:int=Field(strict=True,gt=0)
    method:Literal["EFECTIVO","TRANSFERENCIA","TARJETA","OTRO"]
class MovementCreate(ApiModel):
    type:Literal["OPERATING_EXPENSE","ADMIN_SALARY","OWNER_WITHDRAWAL"]
    amount_clp:int=Field(strict=True,gt=0)
    method:Literal["EFECTIVO","TRANSFERENCIA","TARJETA","OTRO"]
    paid:bool
    note:str=Field(default="",max_length=240)
    operating_date:date
    @model_validator(mode="after")
    def withdrawal_is_paid(self):
        if self.type=="OWNER_WITHDRAWAL" and not self.paid: raise ValueError("Un retiro de dueña debe registrarse como pagado")
        return self
class CashDayUpdate(ApiModel):
    opening_cash_clp:int|None=Field(default=None,strict=True,ge=0)
    counted_cash_clp:int|None=Field(default=None,strict=True,ge=0)
    @model_validator(mode="after")
    def has_change(self):
        if self.opening_cash_clp is None and self.counted_cash_clp is None: raise ValueError("Indica saldo inicial o efectivo contado")
        return self
class CloseDayCreate(ApiModel):
    counted_cash_clp:int=Field(strict=True,ge=0)
    reason:str=Field(default="",max_length=240)
class ReopenDayCreate(ApiModel):
    reason:str=Field(min_length=1,max_length=240)
class ClientCreate(ApiModel):
    name:str=Field(min_length=1,max_length=100)
    contact:str|None=Field(default=None,max_length=100)
class ClientUpdate(ClientCreate): pass
class AppointmentCreate(ApiModel):
    client_id:str=Field(min_length=1,max_length=100)
    professional_id:str=Field(min_length=1,max_length=100)
    service_name:str=Field(min_length=1,max_length=100)
    start_at:datetime
class AppointmentUpdate(AppointmentCreate): pass
class AppointmentStatusUpdate(ApiModel):
    status:Literal["CANCELADA","NO_ASISTIO","ATENDIDA"]
