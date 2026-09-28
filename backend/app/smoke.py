"""Private staging smoke check. Run only with a short-lived test token in environment variables."""
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

def _get(url, headers=None):
    try:
        with urlopen(Request(url,headers=headers or {}),timeout=10) as response:
            if not 200 <= response.status < 300: raise RuntimeError(f"Respuesta HTTP inesperada: {response.status}")
            return response.read()
    except HTTPError as error: raise RuntimeError(f"Respuesta HTTP inesperada: {error.code}") from error
    except URLError as error: raise RuntimeError("No fue posible conectar con staging") from error

def main():
    api=os.environ["API_BASE_URL"].rstrip("/")
    frontend=os.environ["FRONTEND_URL"].rstrip("/")
    studio=os.environ["STAGING_SMOKE_STUDIO_ID"]
    token=os.environ["STAGING_SMOKE_TOKEN"]
    page=_get(frontend+"/")
    if b"est" not in page.lower(): raise RuntimeError("El frontend no devolvió el documento esperado")
    _get(api+"/health")
    _get(api+f"/studios/{studio}/performed-services",{"Authorization":f"Bearer {token}"})
    print("Smoke OK: frontend, API, SQLite y autenticación respondieron correctamente.")
if __name__=="__main__": main()
