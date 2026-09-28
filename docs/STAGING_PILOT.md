# Staging privado para el piloto

## Estado de infraestructura

Este repositorio no contiene proveedor, hosting, Docker, infraestructura como código ni almacenamiento persistente configurado. Por eso **no está listo para piloto aún**: antes de invitar a una dueña se debe elegir un hosting privado que permita ejecutar FastAPI, conservar una carpeta de datos y una carpeta privada de respaldos entre reinicios.

No subas `backend/.env`, `frontend/dev-config.js`, bases SQLite, respaldos, tokens ni datos de clientas a Git.

## Preparación de staging

1. Crea un entorno separado de producción: una URL privada del frontend y otra de la API, ambas con HTTPS.
2. Crea dos directorios persistentes y privados, fuera del contenido público: uno para `DATABASE_URL` y otro para `BACKUP_DIR`.
3. Copia `backend/.env.example` a `backend/.env`. Sustituye los valores de ejemplo; genera un `JWT_SECRET` largo y aleatorio. No reutilices el secreto ni la base de producción.
4. Usa `ENVIRONMENT=staging`, `DEBUG=false` y `FRONTEND_ORIGINS` con **solo** el origen HTTPS real del frontend. No uses `*`.
5. Instala dependencias y ejecuta, desde `backend`:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

El proxy/hosting elegido debe exponer HTTPS y conservar los directorios privados, sin servirlos como archivos web.

## Esquema, logging y respaldo

`init_db()` aplica el esquema y migraciones compatibles al iniciar una base vacía. No hay una migración externa que ejecutar.

Programa diariamente, bajo la cuenta del servidor:

```powershell
python -m app.backup
```

El comando usa el backup consistente de SQLite, valida integridad y conserva la cantidad de días indicada por `BACKUP_RETENTION_DAYS`. El proceso debe registrar solo fecha, nombre de archivo, tamaño, estado y fallos; nunca tokens, contraseñas, teléfonos ni payloads de clientas.

## Validación de staging

1. Crea una dueña y token temporal con datos ficticios usando `python -m app.dev`.
2. Configura temporalmente `API_BASE_URL`, `FRONTEND_URL`, `STAGING_SMOKE_STUDIO_ID` y `STAGING_SMOKE_TOKEN` solo en la sesión de administración.
3. Ejecuta `python -m app.smoke`. Comprueba frontend, `/health`, SQLite y una consulta autenticada.
4. Ejecuta una jornada ficticia de la guía de piloto.
5. Ejecuta una restauración de prueba en una copia temporal, nunca sobre `DATABASE_URL` activo.

## Restauración de prueba

Detén la app. Copia un `.sqlite3` de respaldo a una ruta temporal privada, ejecuta `PRAGMA integrity_check`, establece `DATABASE_URL` a esa copia y arranca la API. Comprueba `/health` y una consulta autenticada. El respaldo original y la base activa no se modifican.

## Bloqueantes antes de iniciar

- Elegir y configurar hosting privado con HTTPS.
- Confirmar que ambos directorios sobreviven reinicios y no son servidos públicamente.
- Configurar el programador diario y verificar un respaldo/restauración reales.
- Usar solo datos ficticios hasta completar esos pasos.
