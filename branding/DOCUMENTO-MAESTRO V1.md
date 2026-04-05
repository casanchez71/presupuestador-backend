# DOCUMENTO MAESTRO DEL PROYECTO
**Presupuestador Inteligente 80/20 - Arquitectos**

**Version:** 3.1  
**Fecha:** 3 de abril de 2026  
**Autores:** Carlos Alberto Sanchez Soria + Grok (inicio) + Claude Code/Codex (orquestacion y auditoria)  
**Estado:** Vigente - base de decisiones para ejecucion  
**Repositorio:** https://github.com/casanchez71/presupuestador-backend

## 1. Historia y evolucion real (corregida)

Este proyecto no arranca el 3 de abril de 2026.  
Los hitos reales registrados en repo/deploy arrancan el **18 de marzo de 2026**.

Origen funcional:
- Necesidad: automatizar presupuestacion de obra con base en Excel reales y lectura de planos.
- Restriccion: simplicidad 80/20, velocidad de salida, y compatibilidad con el ecosistema EOS/SOLE.

Evolucion de trabajo:
- Etapa inicial con Grok: definicion de alcance, tablas base, endpoints iniciales y estrategia de despliegue.
- Etapa de orquestacion: ramas, PRs, deploys, correcciones de JWT/RLS/build y alineacion de documentacion.
- Etapa actual: UI minima utilizable para pruebas, login simplificado y carga de Excel/plano desde la raiz.

## 2. Objetivo del sistema

Construir un modulo de presupuestacion de obra que:
- reduzca drásticamente tiempos de armado de presupuesto,
- mantenga trazabilidad de precios y versiones,
- permita lectura asistida de planos,
- y pueda integrarse dentro de SOLE sin romper seguridad multi-tenant.

## 3. Estado actual en produccion

### 3.1 Infraestructura actual
- Backend: FastAPI Python 3.11
- Deploy: Render (free tier)
- URL: https://presupuestador-backend-adm1.onrender.com
- DB actual: Supabase compartido con EOS (mismo proyecto)
- Auth: Supabase Auth con JWT (JWKS)

### 3.2 Repositorio
- GitHub: https://github.com/casanchez71/presupuestador-backend
- Branch principal: `main`

### 3.3 Modulo funcional hoy
- CRUD de presupuestos
- Arbol jerarquico de items
- Import Excel
- Analisis de plano por IA
- Aplicacion de indirectos
- Versionado/snapshots
- Export Excel
- UI minima en `/` con login, carga de presupuestos y flujo de prueba

## 4. Modelo de datos del modulo Presupuestador

Tablas propias del modulo:
- `price_snapshots`
- `audit_logs`
- `budgets`
- `budget_items` (incluye `indirecto` y `total_con_indirecto`)
- `budget_versions`
- `indirect_config`

Dependencias del core EOS:
- `auth.users`
- `organizations`
- `memberships`
- funcion `get_my_org_ids()`

Nota operativa:
- La aislacion tenant se hace por `org_id` + RLS.

## 5. Problema detectado y decision arquitectonica superadora

Problema:
- El modulo Presupuestador vive hoy en el mismo proyecto Supabase de EOS.
- Esto acelero salida, pero mezcla dominio core (CRM/Bot/EOS) con dominio especifico de presupuestacion.

Opciones consideradas:
- **A:** mantener todo compartido.
- **B:** separar totalmente auth + data en proyecto nuevo.
- **C (elegida):** **Auth compartida + Data separada por fases**.

## 6. Decision oficial vigente (Modelo C)

Se define formalmente:
- Mantener **login unico** y seguridad central en EOS.
- Separar progresivamente la **data del Presupuestador** en proyecto Supabase dedicado.
- Ejecutar migracion en 2 fases para evitar downtime.

Principios:
- Separar datos sin romper experiencia de usuario.
- Evitar doble login.
- Evitar contaminar el core EOS con tablas hiper-especificas.
- Mantener rollback por variables de entorno.

## 7. Pedido oficial a Claude Code (incluido en historia de decisiones)

Mandato:
- Implementar y ejecutar el plan **Auth compartida + Data separada**.
- Codex audita cada cambio.

Plan operativo exigido:
1. Crear proyecto `presupuestador-data` en Supabase.
2. Correr migraciones del modulo en ese proyecto.
3. Backend con doble cliente Supabase:
   - `AUTH_SUPABASE_URL/KEY` para JWT + `memberships`
   - `DATA_SUPABASE_URL/KEY` para tablas del presupuestador
4. Mantener `SUPABASE_URL/KEY` como fallback temporal.
5. Deploy controlado en Render con nuevas env vars.
6. Validacion funcional end-to-end.
7. Rollback por env vars si algo falla.

Criterios de aceptacion:
- Usuario SOLE usa el mismo login.
- Presupuestador lee/escribe en data separada.
- RLS y aislamiento por `org_id` intactos.
- Sin corte operativo en la migracion.

## 8. Reglas de implementacion y gobierno tecnico

- No fusionar cambios sin PR.
- No romper `main` para experimentos.
- Toda decision de infra debe quedar registrada en este documento y en PR.
- Si hay contradiccion entre documento y codigo, prevalece codigo + migraciones, y luego se actualiza el documento.

## 9. Pendientes reales priorizados

1. Cerrar migracion de data separada (Modelo C).
2. Mejorar calidad estructurada de sugerencias desde plano.
3. Flujo completo: plano + precios + estimacion de costos automatizada.
4. Export PDF.
5. Pruebas automatizadas y controles de regresion.

---

**Fin del Documento Maestro v3.1**

Este documento es rector de producto e infraestructura, y se mantiene alineado con codigo, migraciones y despliegues reales.
