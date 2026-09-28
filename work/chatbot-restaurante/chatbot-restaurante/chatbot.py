from openai import AsyncOpenAI
from config import GROQ_API_KEY
from menu import cargar_menu, menu_a_texto
from database import get_historial, guardar_mensaje

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY
)

SYSTEM_PROMPT = """Eres el asistente virtual de {nombre_restaurante}. Responde SIEMPRE en español.

Tu trabajo es atender clientes de forma amable, breve y natural por WhatsApp.

INFORMACIÓN DEL RESTAURANTE:
- Horario: {horario}
- Menú:
{menu_texto}

INSTRUCCIONES:
- Respuestas cortas y claras, como un chat real.
- Si piden el menú, muéstralo organizado por categoría.
- Puedes tomar pedidos: confirma cada item y da el total.
- Si preguntan algo que no sabes, ofrece contactar al local.
- Nunca inventes precios ni platos que no están en el menú.
- Usa emojis con moderación. Sé cálido pero profesional.
"""

async def responder(restaurante: dict, cliente_numero: str, mensaje_usuario: str) -> str:
    menu = cargar_menu(restaurante["menu_path"])
    menu_texto = menu_a_texto(menu)

    system = SYSTEM_PROMPT.format(
        nombre_restaurante=restaurante["nombre"],
        horario=restaurante["horario"],
        menu_texto=menu_texto
    )

    historial = get_historial(restaurante["id"], cliente_numero)
    guardar_mensaje(restaurante["id"], cliente_numero, "user", mensaje_usuario)

    messages = [{"role": "system", "content": system}]
    messages.extend(historial)
    messages.append({"role": "user", "content": mensaje_usuario})

    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        max_tokens=500,
        temperature=0.7
    )

    respuesta = response.choices[0].message.content
    guardar_mensaje(restaurante["id"], cliente_numero, "assistant", respuesta)
    return respuesta
