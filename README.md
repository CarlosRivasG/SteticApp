# Estética MVP — primer corte

Prototipo web responsive para validar el núcleo del flujo del PRD:

1. Configurar profesionales y catálogo.
2. Registrar una atención efectivamente realizada.
3. Aplicar precio, descuento, porcentaje y responsable de materiales.
4. Calcular y congelar la comisión y participación del local al confirmar.
5. Registrar cobros parciales por efectivo, transferencia, tarjeta u otro medio y ver el saldo pendiente.
6. Registrar gastos operativos, sueldos administrativos y retiros de dueña por separado; calcular caja esperada en efectivo y diferencia de conteo.
7. Cerrar el día para bloquear cambios y reabrirlo solo con un motivo, conservando el historial de cierre.
8. Crear citas manuales con clienta, profesional, servicio estimado y horario; una cita no afecta las cifras financieras.
9. Convertir una cita programada en atención real, usando la reserva como punto de partida y permitiendo corregir sus datos antes de confirmar.
10. Consultar el resumen de la semana por profesional y exportar servicios, cobros y movimientos en CSV.
11. Anular una atención sin cobros solo con un motivo; la anulación conserva historial y no altera mediante borrado los registros originales.
12. Registrar pagos de comisión como movimientos separados y vinculados a la profesional, sin tratarlos como gasto operativo.
13. Descargar un respaldo JSON y restaurarlo explícitamente en otro navegador o dispositivo.
14. Revertir el último cobro activo con motivo, conservando el historial y recalculando el saldo pendiente antes de anular una atención.

## Experiencia visual

La interfaz sigue el sistema visual de salón premium definido en `ui.spec.md`: sidebar persistente, dashboard de operación diaria, agenda visual, distribución de dinero, rendimiento del equipo, pendientes, caja resumida y diseño móvil con navegación inferior. Las atenciones, cobros, caja y agenda ya integrados usan FastAPI y SQLite como fuente de verdad. Partes no migradas de la demo conservan estado local temporal y no deben considerarse respaldo ni persistencia de producción.

## Ejecutar localmente

No abra `frontend/index.html` mediante `file://`. Abra dos terminales desde la raíz del proyecto (`anan`).

Terminal 1 — backend FastAPI:

```powershell
cd .\backend
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Terminal 2 — frontend HTTP:

```powershell
cd .\frontend
npx serve . -l 5173
```

Abra la URL mostrada por `serve`, usando `http://127.0.0.1:5173`. El frontend usa una única configuración local en `app.js`: API `http://127.0.0.1:8000` y estudio `development-studio`. Si el backend no está iniciado, mostrará un mensaje de conexión y no guardará nuevas atenciones localmente.

Para conectar el frontend protegido en desarrollo, copia `frontend/dev-config.example.js` como `frontend/dev-config.js`, pega el `TOKEN` temporal que imprime `python -m app.dev` y sirve nuevamente el frontend. `frontend/dev-config.js` está ignorado por Git y no debe crearse en producción.

Verificación de sintaxis del frontend:

```powershell
node --check frontend/app.js
```

Pruebas de backend, desde `backend`:

```powershell
python -m pytest
```

## Regla de cálculo

Todos los importes se guardan como enteros CLP. La comisión utiliza el redondeo requerido en la especificación:

`floor((precio_final × porcentaje_en_puntos_base + 5000) / 10000)`

## Piloto privado

Antes de usar la aplicación con un estudio real, revisa [docs/STAGING_PILOT.md](docs/STAGING_PILOT.md). El repositorio no configura un proveedor ni almacenamiento persistente: hasta que se configure un staging privado con HTTPS, SQLite persistente y respaldos privados diarios, el piloto permanece bloqueado. La operación de práctica se explica en [docs/PILOT_GUIDE_OWNER.md](docs/PILOT_GUIDE_OWNER.md).
