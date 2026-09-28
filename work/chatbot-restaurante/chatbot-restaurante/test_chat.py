import asyncio
from database import init_db, get_restaurante_by_number
from chatbot import responder

async def main():
    init_db()
    restaurante = get_restaurante_by_number('+56912345678')
    print(f"\n{'='*45}")
    print(f"  Chatbot: {restaurante['nombre']}")
    print(f"  Horario: {restaurante['horario']}")
    print(f"{'='*45}")
    print("  Escribe 'salir' para terminar\n")

    cliente = "+56900000001"

    while True:
        try:
            msg = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nHasta luego.")
            break
        if not msg:
            continue
        if msg.lower() == "salir":
            print("Hasta luego.")
            break
        print("Bot: ", end="", flush=True)
        respuesta = await responder(restaurante, cliente, msg)
        print(respuesta + "\n")

asyncio.run(main())
