---
name: security-review
description: Review security and financial-integrity risks in features that touch access, studio data, APIs, databases, integrations, secrets, uploads, or money. Reports findings only; never implements fixes automatically.
---

# Security review

Use this skill before closing a feature that changes authentication, authorization, multi-tenant data, endpoints, databases, external integrations, secrets, file uploads, or financial records.

This is a review-only workflow. Inspect the relevant diff, source code, schema, configuration, tests, and documentation. Do not edit application code or configuration unless the user separately asks for an implementation.

## Review checklist

### 1. Multi-tenant isolation

- Verify every query and mutation filters by `studio_id`.
- Never trust `studio_id`, role, or permissions supplied by the browser; verify authority on the server.
- Check for horizontal access between studios through identifiers, list endpoints, joins, exports, or error responses.

### 2. API

- Validate payloads with Pydantic, including size limits, types, ranges, and unexpected fields.
- Ensure errors do not expose traces, SQL, secrets, or internal identifiers unnecessarily.
- Require idempotency controls for financial operations and verify duplicate requests cannot create duplicate financial records.

### 3. Database

- Use parameterized queries exclusively.
- Require transactions for composed operations that must succeed or fail together.
- Do not delete financial history.
- Require audit events for relevant corrections or reversals.

### 4. Secrets and integrations

- Do not expose keys, tokens, credentials, or private URLs in frontend code, Git, or logs.
- Use environment variables for secrets.
- Verify webhook signatures before processing external webhook payloads.

### 5. Browser

- Restrict CORS by environment and allowed origins.
- Do not keep tokens or unnecessary sensitive financial data in `localStorage`.
- Prevent XSS when rendering client-provided names, notes, or other content.

### 6. Dependencies and deployment

- Identify vulnerable or unpinned dependencies where the project has a supported audit mechanism.
- Verify production does not enable debug behavior.
- Check that the minimum secure configuration is documented.

## Reporting format

Classify every finding as one of:

- **BLOQUEANTE**: unauthorized access, secret exposure, integrity loss, or another risk that makes the feature unsafe to ship.
- **IMPORTANTE**: material risk that needs a tracked correction before broad rollout.
- **MEJORA**: defense-in-depth or maintainability improvement that does not block the stated scope.

For every finding, state:

1. **Riesgo**
2. **Evidencia**
3. **Archivos afectados**
4. **Corrección mínima**

End with an explicit decision: `APROBADO`, `APROBADO CON PENDIENTES`, or `NO APROBADO`. A feature with any open **BLOQUEANTE** finding must be `NO APROBADO`.
