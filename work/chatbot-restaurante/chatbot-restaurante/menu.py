import json, os

def cargar_menu(menu_path: str) -> dict:
    if not os.path.exists(menu_path):
        return {}
    with open(menu_path, "r", encoding="utf-8") as f:
        return json.load(f)

def menu_a_texto(menu: dict) -> str:
    if not menu:
        return "Menú no disponible."
    lineas = []
    for categoria, items in menu.items():
        lineas.append(f"\n*{categoria.upper()}*")
        for item in items:
            precio = f"${item['precio']:,}".replace(",", ".")
            desc = f" - {item['descripcion']}" if item.get('descripcion') else ""
            lineas.append(f"  • {item['nombre']} — {precio}{desc}")
    return "\n".join(lineas)
