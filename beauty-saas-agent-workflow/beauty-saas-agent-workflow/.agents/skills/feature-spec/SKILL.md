---
name: feature-spec
description: Convierte un cambio de producto en una spec lista para que Codex implemente sin adivinar reglas.
---

# Especificar feature

Antes de programar, crea `docs/features/<nombre>.md` con:

1. Problema y usuaria afectada.
2. Alcance y exclusiones.
3. Flujo principal y estados vacíos/errores.
4. Reglas de negocio que reutiliza o modifica, con ID.
5. Datos, permisos, migraciones y auditoría requeridos.
6. Criterios de aceptación observables, incluyendo casos de borde.
7. Impacto visual y móvil.
8. Plan de liberación o migración de datos, si corresponde.

No conviertas una ambigüedad de negocio en una decisión técnica silenciosa. Señálala para decisión del Product Owner.
