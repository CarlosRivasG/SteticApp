# Reglas de negocio financieras

Estas reglas se derivan de PRD/SRS v0.1 del 25 de septiembre de 2026.

| ID | Regla |
|---|---|
| RB-01 | Cada entidad pertenece a un estudio; lecturas y escrituras validan autorización y propiedad en servidor. |
| RB-02 | CLP se guarda como entero no negativo. |
| RB-03 | Comisión = redondear(precio final × porcentaje / 100) al peso, 0,5 hacia arriba. Participación del local = precio final − comisión. |
| RB-04 | Materiales (`LOCAL`, `PROFESIONAL`, `MIXTO`) es una etiqueta; no cambia automáticamente porcentaje ni costo. |
| RB-05 | La comisión se devenga al confirmar la atención, incluso con cobro pendiente. |
| RB-06 | Varios cobros son válidos mientras su suma no supere el precio final. |
| RB-07 | Anular exige motivo, permiso y reverso/anulación trazable de cobros vinculados. |
| RB-08 | Ajustar atención confirmada o día cerrado requiere motivo, auditoría y reapertura explícita del período. |
| RB-09 | Retiro de dueña reduce caja, no resultado operativo. Gasto efectivamente pagado reduce ambos; gasto pendiente reduce resultado, no caja aún. |
| RB-10 | Operación en `America/Santiago`; semana lunes–domingo. |
