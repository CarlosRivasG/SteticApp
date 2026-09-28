# AGENTS.md — Estética: sistema de trabajo con agentes

## Producto y prioridad

Esta aplicación ayuda a dueñas y administradoras de estudios de uñas y belleza pequeños (0–5 profesionales) a registrar servicios realmente realizados, cobros, comisiones, salidas de dinero y cierres diarios auditables.

No es un sistema genérico de reservas ni contabilidad tributaria. La prioridad es que la dueña pueda explicar qué se atendió, cuánto se cobró, cuánto corresponde a cada profesional, qué salió de caja y por qué existe una diferencia.

La referencia funcional y visual existente es `index.html`. Consérvala como referencia de flujo; no asumas que el almacenamiento local de la demo es una arquitectura de producción.

## Fuentes de verdad

Antes de implementar una feature, lee únicamente los documentos relevantes:

1. `docs/PRODUCT.md` — alcance y resultado esperado.
2. `docs/BUSINESS_RULES.md` — reglas financieras inviolables.
3. `docs/UI_SPEC.md` — experiencia y lenguaje visual.
4. `docs/features/<feature>.md` — contrato de la feature, si existe.

Si una solicitud contradice una regla, detente y explica el conflicto. No inventes reglas financieras ni cambies una regla de producto sin actualizar su documento fuente.

## Modo de trabajo

Para cambios pequeños y aislados, trabaja con un único agente.

Para una feature que atraviese datos, lógica y UI:

1. El agente principal inspecciona el repositorio y la spec.
2. Redacta un plan breve con archivos, riesgos y criterios de aceptación.
3. Solo delega tareas independientes y no solapadas (por ejemplo: investigación de esquema, UI aislada, o casos de prueba).
4. El agente principal integra los cambios, ejecuta las verificaciones y revisa los criterios de aceptación.

Nunca paralelices modificaciones sobre los mismos archivos, migraciones, contratos de API o lógica de cálculo.

## Reglas financieras y de integridad

- Todo dato pertenece a un único estudio. La autorización y el aislamiento se validan en el servidor; nunca se confía en un rol entregado por el navegador.
- Los importes CLP son enteros no negativos. La comisión se calcula sobre el precio final posterior a descuento y se redondea al peso más cercano (0,5 hacia arriba).
- Al confirmar una atención se congelan precio final, profesional, porcentaje de comisión y responsable de materiales. Cambios de configuración posteriores no reescriben el pasado.
- Comisión devengada no es comisión pagada. Un pago de comisión debe ser un movimiento explícito, nunca un gasto genérico.
- Cobros parciales no pueden superar el precio final; ventas, cobros y comisiones se agregan por separado.
- Retiro de dueña reduce caja esperada, pero no el resultado operativo. Gasto operativo y sueldo administrativo se muestran separados.
- Las modificaciones de registros confirmados o de un día cerrado requieren motivo y un evento de auditoría. No borres historia financiera.
- Fecha operativa y reportes usan `America/Santiago`; las semanas van de lunes a domingo.
- Las confirmaciones y ajustes deben ser idempotentes y atómicos cuando afecten más de un registro.

## UX

- La usuaria principal no es técnica: prioriza claridad, confirmación visible y prevención de errores sobre densidad de opciones.
- Diseño premium beauty-tech: marfil cálido, rosa suave, rosewood, champagne y ciruela profunda. Evitar rosa Barbie, interfaces administrativas genéricas, saturación visual y 3D/WebGL en operación.
- Debe funcionar bien en móvil y escritorio. Reutiliza componentes y patrones existentes antes de crear otros.
- Cada métrica financiera debe permitir llegar al detalle que la compone.

## Calidad y entrega

Una tarea no está terminada porque compila. Antes de finalizar:

1. Comprueba los criterios de aceptación de la feature.
2. Ejecuta los comandos definidos por el repositorio para lint, typecheck, pruebas y build.
3. Añade o actualiza pruebas de reglas y transacciones cuando se modifique dinero, permisos, cierres o auditoría.
4. Realiza verificación manual móvil de los flujos afectados.
5. Resume: qué cambió, pruebas ejecutadas, decisiones o riesgos pendientes.

Antes de cerrar cualquier feature de autenticación, multi-tenant, integración externa o datos financieros, ejecuta `.agents/skills/security-review/SKILL.md`. No cierres la feature si esa revisión mantiene un hallazgo **BLOQUEANTE** abierto.

No introduzcas dependencias, refactors amplios, cambios de esquema destructivos ni cambios visuales fuera de alcance sin justificarlo en el plan.
