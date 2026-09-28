from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.responses import PlainTextResponse
import asyncio
from config import VERIFY_TOKEN
from database import init_db, get_restaurante_by_number
from chatbot import responder
from whatsapp import enviar_mensaje

app = FastAPI(title="Chatbot Restaurante")

@app.on_event("startup")
async def startup():
    init_db()

@app.get("/webhook")
async def verificar_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Token inválido")

@app.post("/webhook")
async def recibir_mensaje(request: Request):
    data = await request.json()
    try:
        entry = data["entry"][0]
        change = entry["changes"][0]["value"]
        if "messages" not in change:
            return {"status": "no_message"}
        mensaje = change["messages"][0]
        if mensaje.get("type") != "text":
            return {"status": "tipo_no_soportado"}
        numero_wa = change["metadata"]["display_phone_number"]
        numero_cliente = mensaje["from"]
        texto = mensaje["text"]["body"]
        numero_wa_fmt = f"+{numero_wa}" if not numero_wa.startswith("+") else numero_wa
        restaurante = get_restaurante_by_number(numero_wa_fmt)
        if not restaurante:
            return {"status": "restaurante_no_encontrado"}
        asyncio.create_task(procesar_y_responder(restaurante, numero_cliente, texto))
    except (KeyError, IndexError) as e:
        print(f"Error: {e}")
    return {"status": "ok"}

async def procesar_y_responder(restaurante, numero_cliente, texto):
    try:
        respuesta = await responder(restaurante, numero_cliente, texto)
        await enviar_mensaje(numero_cliente, respuesta)
    except Exception as e:
        print(f"Error: {e}")

@app.get("/")
async def health():
    return {"status": "running"}
