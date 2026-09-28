---
name: implement-feature
description: Entrega una feature completa del SaaS de estética desde una spec verificable.
---

# Implementar una feature

## Entrada necesaria

La tarea debe indicar el resultado de negocio y apuntar a una spec en `docs/features/` o contener criterios de aceptación observables.

## Procedimiento

1. Lee `AGENTS.md`, `docs/PRODUCT.md`, `docs/BUSINESS_RULES.md` y la spec de la feature.
2. Inspecciona los patrones existentes, contratos, esquema y pruebas antes de cambiar nada.
3. Escribe un plan breve: alcance, archivos, migración si aplica, riesgos y criterios de aceptación.
4. Implementa el corte más pequeño que entregue valor de punta a punta. Reutiliza componentes y lógica existentes.
5. Cuando cambies flujo financiero, confirma en servidor, conserva snapshots, usa transacciones/idempotencia y registra auditoría según corresponda.
6. Añade pruebas de reglas, errores y bordes relevantes. Ejecuta lint, typecheck, pruebas y build definidos por el repo.
7. Verifica manualmente la experiencia móvil afectada.

## Delegación

Delegar solo exploración, UI independiente o diseño de casos de prueba. El agente principal es el único que integra contratos, migraciones y resultados.

## Salida

Informa: resumen, archivos modificados, verificaciones ejecutadas, criterios cumplidos y decisiones pendientes. No declares terminada una feature si falta una verificación exigida.
