# Instalación en el proyecto `2026-09-25`

Este paquete cambia el flujo sin meter una burocracia de seis agentes permanentes.

## Copia inicial

Desde la raíz del proyecto, copiar:

- `AGENTS.md`
- `docs/`
- `.agents/skills/`

Conservar el PRD/SRS y diseño técnico completos ya existentes dentro de `docs/` como referencia adicional. No reemplazar los archivos reales del proyecto sin comparar su contenido.

## Flujo diario

1. Carlos define o ajusta una regla/feature con `feature-spec`.
2. Codex principal usa `implement-feature` para inspeccionar, planificar, implementar y verificar.
3. Si toca dinero, permisos, cierre o auditoría, corre también `financial-review` antes de cerrar la tarea.
4. Se usan subagentes solo para partes independientes; el principal integra y ejecuta las pruebas.

## Primer prompt para Codex

> Lee `AGENTS.md` y resume la arquitectura actual, comandos de calidad, estado de las features E1-01 a E1-05 y cualquier contradicción con `docs/`. No modifiques código. Después propón el corte más pequeño para confirmar una atención y mostrar su reparto.

Con esa auditoría ya se puede trabajar por features completas, no por prompts improvisados.
