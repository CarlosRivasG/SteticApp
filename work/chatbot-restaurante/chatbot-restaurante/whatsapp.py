import httpx
from config import META_ACCESS_TOKEN, META_PHONE_NUMBER_ID

API_URL = f"https://graph.facebook.com/v19.0/{META_PHONE_NUMBER_ID}/messages"

async def enviar_mensaje(numero_destino: str, texto: str):
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": numero_destino,
        "type": "text",
        "text": {"body": texto}
    }
    async with httpx.AsyncClient() as http:
        r = await http.post(API_URL, json=payload, headers=headers)
        r.raise_for_status()
        return r.json()
