---
name: financial-review
description: Revisa una feature o PR que afecte dinero, comisiones, cobros, caja, cierres, permisos o auditoría.
---

# Revisión financiera

## Alcance

Usa esta revisión obligatoriamente para servicios confirmados, precios/descuentos, comisiones, cobros, movimientos, cierres, reportes, permisos por estudio y migraciones financieras.

## Checklist

- ¿La entidad está aislada por estudio y autorizada en servidor?
- ¿Los importes son enteros CLP y las validaciones viven también fuera del cliente?
- ¿Se conserva el snapshot de precio, porcentaje, profesional y materiales al confirmar?
- ¿Cobros parciales no superan el precio y no duplican ventas/comisiones?
- ¿Comisión devengada y pago de comisión están separados?
- ¿Retiros, gastos y sueldos se agregan correctamente en caja y resultado operativo?
- ¿Operaciones compuestas son atómicas e idempotentes?
- ¿Cambios/anulaciones/cierres producen motivo y auditoría, sin borrar historia?
- ¿Reportes operan en `America/Santiago` y son trazables a sus registros?
- ¿Existen pruebas para el camino feliz, límites, autorización, doble envío y día cerrado?

## Salida

Clasifica hallazgos en: bloqueante, importante o mejora. Para cada bloqueo indica regla afectada, evidencia y corrección mínima. No apruebes una feature financiera con un bloqueo abierto.
