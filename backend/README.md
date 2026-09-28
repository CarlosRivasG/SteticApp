# Backend Estética

API para convertir el MVP local en un sistema compartido. La aplicación es la fuente de verdad; WhatsApp y Google Calendar son canales sincronizados.

## Primer corte: atenciones confirmadas

El estudio de desarrollo `development-studio` se crea automáticamente al iniciar. La aplicación puede confirmar una atención mediante:

- `POST /studios/development-studio/performed-services`
- `GET /studios/development-studio/performed-services`

El servidor valida importes CLP, descuento, porcentaje y materiales; calcula y persiste el precio final, comisión y participación del local como snapshots inmutables. Los cobros parciales se registran por separado y no modifican la comisión devengada; caja permanece fuera de este corte.

Los cobros parciales se registran contra una atención confirmada mediante:

- `POST /studios/{studio_id}/performed-services/{service_id}/payments`
- `GET /studios/{studio_id}/performed-services/{service_id}/payments`

Cada cobro requiere autorización, `Idempotency-Key`, monto CLP positivo y medio de pago. La lista de atenciones también devuelve sus cobros válidos para calcular total recibido y saldo pendiente.

## Caja y movimientos

Solo una membresía `OWNER_ADMIN` puede registrar `OPERATING_EXPENSE`, `ADMIN_SALARY` o `OWNER_WITHDRAWAL`, actualizar el conteo de efectivo, cerrar o reabrir un día. Los endpoints usan `Idempotency-Key` y conservan un evento de auditoría:

- `POST /studios/{studio_id}/movements`
- `PUT /studios/{studio_id}/cash-days/{operating_date}`
- `POST /studios/{studio_id}/cash-days/{operating_date}/close`
- `POST /studios/{studio_id}/cash-days/{operating_date}/reopen`
- `GET /studios/{studio_id}/summaries/daily?operating_date=YYYY-MM-DD`
- `GET /studios/{studio_id}/summaries/weekly?week_start=YYYY-MM-DD`

El resumen entrega los registros fuente, el esperado por medio de pago y el resultado operativo simple. Transferencias y tarjetas son registros esperados del sistema, no conciliación bancaria.

## Ejecutar localmente

1. Cree un entorno virtual e instale `pip install -r requirements.txt`.
2. Copie `.env.example` como `.env` y complete secretos y credenciales.
3. Ejecute `uvicorn app.main:app --reload` desde esta carpeta.

La documentación local queda en `/docs`.

## Identidad de desarrollo

No existe registro público ni login todavía. Para crear un estudio, su dueña y un token de desarrollo, ejecuta:

```powershell
python -m app.dev --email duena@ejemplo.cl --studio "Mi estudio"
```

El comando muestra `STUDIO_ID` y un `TOKEN` temporal. Usa el token como `Authorization: Bearer TOKEN`; cada creación de atención exige además un encabezado único `Idempotency-Key`.

## Calidad

Desde esta carpeta, con el entorno virtual activo:

```powershell
python -m pytest
```

## Exportación y respaldos privados

Una administradora puede descargar `GET /studios/{studio_id}/exports/csv`. El resultado es un ZIP con CSV UTF-8: `studio`, `clients`, `appointments`, `performed_services`, `payments`, `financial_movements`, `cash_days`, `cash_day_events` y `audit_events`. Cada archivo conserva IDs y claves relacionales, fechas ISO 8601 e importes CLP enteros. No contiene usuarios, contraseñas, hashes, tokens, llaves de idempotencia ni fingerprints de solicitudes.

Los respaldos no son descargables por HTTP ni se restauran por una ruta pública. Configure un directorio privado y persistente, fuera del directorio servido por el frontend, antes de un piloto:

```powershell
$env:BACKUP_DIR='C:\Users\cm_ri\StetiAppBackups'
$env:BACKUP_RETENTION_DAYS='30'
python -m app.backup
```

Programe ese último comando diariamente con el programador del sistema bajo la cuenta que ejecuta el backend. El proceso usa `sqlite3.backup`, comprueba `PRAGMA integrity_check`, publica el archivo y su metadato JSON de manera atómica, y elimina copias que superen la retención. En desarrollo, si no se configura `BACKUP_DIR`, se usa una carpeta temporal privada; **no es durable y no habilita un piloto**. En producción, `BACKUP_DIR` es obligatorio.

Para restaurar, detenga la aplicación y trabaje con una copia del respaldo en un entorno aislado. Ejecute `PRAGMA integrity_check`, configure `DATABASE_URL` hacia esa copia y arranque la aplicación para comprobar `/health` y una consulta autenticada. Nunca sobrescriba la base activa; pruebe primero con una copia temporal. No hay endpoint público de restauración.

## Desarrollo con frontend

El backend acepta únicamente el frontend servido por HTTP en `http://127.0.0.1:5173` o `http://localhost:5173`. Desde la raíz del proyecto, levántelo aparte con `cd ..\frontend` y `npx serve . -l 5173`; no use `file://`.

Desde la raíz del proyecto, compruebe el frontend con:

```powershell
node --check frontend/app.js
```

## Staging privado y piloto

Consulta [../docs/STAGING_PILOT.md](../docs/STAGING_PILOT.md) antes de desplegar: contiene variables por entorno, requisitos de almacenamiento persistente, prueba de humo y restauración aislada. La guía para la dueña está en [../docs/PILOT_GUIDE_OWNER.md](../docs/PILOT_GUIDE_OWNER.md) y el seguimiento del piloto en [../docs/PILOT_TRACKER.md](../docs/PILOT_TRACKER.md).

## Integraciones

WhatsApp y Google Calendar permanecen fuera del router activo hasta implementar validación de firma y credenciales por entorno. La agenda y el resto de la demo no forman parte de esta foundation.
