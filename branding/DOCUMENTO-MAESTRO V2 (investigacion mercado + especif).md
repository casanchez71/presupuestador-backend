# DOCUMENTO MAESTRO DEL PROYECTO
**Presupuestador Inteligente 80/20 –Arquitectos**

**Versión:** 4.0 (Unificada)  
**Fecha:** 3 de abril de 2026  
**Autores:** Carlos Alberto Sanchez Soria + Grok (xAI) + Claude Code / Codex  
**Estado:** Vigente – Base oficial de decisiones para ejecución y consultoría  
**Repositorio:** https://github.com/casanchez71/presupuestador-backend

## 1. Historia y evolución real (corregida)
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
**Problema:**  
- El modulo Presupuestador vive hoy en el mismo proyecto Supabase de EOS.  
- Esto acelero salida, pero mezcla dominio core (CRM/Bot/EOS) con dominio especifico de presupuestacion.

**Opciones consideradas:**  
- **A:** mantener todo compartido.  
- **B:** separar totalmente auth + data en proyecto nuevo.  
- **C (elegida):** **Auth compartida + Data separada por fases**.

## 6. Decision oficial vigente (Modelo C)
Se define formalmente:  
- Mantener **login unico** y seguridad central en EOS.  
- Separar progresivamente la **data del Presupuestador** en proyecto Supabase dedicado.  
- Ejecutar migracion en 2 fases para evitar downtime.

**Principios:**  
- Separar datos sin romper experiencia de usuario.  
- Evitar doble login.  
- Evitar contaminar el core EOS con tablas hiper-especificas.  
- Mantener rollback por variables de entorno.

## 7. Pedido oficial a Claude Code (incluido en historia de decisiones)
**Mandato:**  
- Implementar y ejecutar el plan **Auth compartida + Data separada**.  
- Codex audita cada cambio.

**Plan operativo exigido:**  
1. Crear proyecto `presupuestador-data` en Supabase.  
2. Correr migraciones del modulo en ese proyecto.  
3. Backend con doble cliente Supabase:  
   - `AUTH_SUPABASE_URL/KEY` para JWT + `memberships`  
   - `DATA_SUPABASE_URL/KEY` para tablas del presupuestador  
4. Mantener `SUPABASE_URL/KEY` como fallback temporal.  
5. Deploy controlado en Render con nuevas env vars.  
6. Validacion funcional end-to-end.  
7. Rollback por env vars si algo falla.

**Criterios de aceptacion:**  
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

## 10. Informe de Investigación – Software de Presupuestación Inteligente para Construcción – Análisis Mundial 2026

**Objetivo del informe**  
Proporcionar a la persona que está diseñando la consultoría un análisis claro, objetivo y actualizado de las mejores herramientas del mundo que resuelven el mismo problema que queremos resolver para Terrac: generar presupuestos profesionales de obra de forma rápida, con lectura inteligente de planos, importación de Excel, árbol jerárquico, indirectos ponderados y mínima intervención humana.

### 10.1 Panorama mundial actual (2026)
El mercado de software de estimating y takeoff para construcción está en plena explosión de IA. Las herramientas más avanzadas ya combinan:

* Visión artificial (lectura automática de planos PDF/imágenes)  
* Extracción inteligente de cantidades  
* Árboles jerárquicos automáticos  
* Integración con listas de precios  
* Versionado y trazabilidad

### 10.2 Software First-Class (los más relevantes)

| Posición | Software                        | Tipo principal              | Fortalezas principales (80/20)                                      | Debilidades importantes                              | Precio aproximado (2026)      | ¿Cubre el 80% de las necesidades de Terrac? |
|----------|---------------------------------|-----------------------------|---------------------------------------------------------------------|------------------------------------------------------|-------------------------------|---------------------------------------------|
| 1        | Togal.AI                        | AI Takeoff + Estimating     | Lectura de planos extremadamente precisa, genera ítems y cantidades en minutos, árbol automático, integración con Excel | Caro, menos fuerte en indirectos ponderados y costos de estructura | Muy alto (enterprise)        | Sí, el más cercano                          |
| 2        | Beam AI                         | AI Construction Takeoff     | Excelente en planos complejos, sugerencias inteligentes, export Excel limpio, muy rápido | Todavía débil en costos indirectos y versionado completo | Alto                         | Muy alto                                    |
| 3        | Kreo                            | AI Takeoff + BIM            | Muy bueno en planos CAD/PDF, medición automática, integración con presupuestos | Interfaz más técnica, menos "simple" que Togal      | Medio-Alto                   | Alto                                        |
| 4        | STACK                           | Takeoff + Estimating        | Muy sólido en takeoff + presupuesto, buen manejo de precios y subcontratos | Menos IA que los anteriores                          | Medio                        | Medio-Alto                                  |
| 5        | Handoff.AI                      | AI Estimating Assistant     | Muy bueno en conversación + IA, genera presupuestos desde descripción o planos | Aún inmaduro en proyectos grandes                    | Medio                        | Alto (para casos más simples)               |
| 6        | Autodesk Construction Cloud     | Plataforma completa         | Muy potente, integración BIM, lectura de planos, historial completo | Excesivamente complejo y caro para la mayoría        | Muy alto                     | Sí, pero sobredimensionado                  |

**Conclusión del cuadro:**  
Togal.AI y Beam AI son los que más se acercan a lo que queremos construir (80% de las necesidades con solo lectura de planos + generación automática de ítems).  
Ninguno de ellos resuelve perfectamente los indirectos ponderados + gastos de estructura + trazabilidad de versiones + integración con el flujo exacto de Terrac.  
Esa brecha es exactamente donde nuestro sistema puede ser superior y más específico.

### 10.3 Qué 20% de funciones cubren el 80% de las necesidades reales de una constructora como Terrac
Según el análisis de los documentos y la transcripción, las funciones que realmente generan el 80% del valor son:

| % de valor | Función                                              | Por qué es crítica para Terrac                                      | Software que mejor la resuelve |
|------------|------------------------------------------------------|---------------------------------------------------------------------|--------------------------------|
| 35%        | Lectura automática de planos + extracción de cantidades | Elimina la mayor pérdida de tiempo (lectura manual)                | Togal.AI / Beam AI             |
| 25%        | Generación automática de árbol jerárquico y códigos | Permite ver la obra piso por piso y estructurada                   | Togal.AI + Kreo                |
| 15%        | Importación y actualización de listas de precios     | Evita errores y mantiene trazabilidad                               | STACK + Togal                  |
| 10%        | Aplicación automática de indirectos ponderados       | Es uno de los dolores más grandes que mencionó Emilia              | Casi ninguno (nuestro fuerte)  |
| 10%        | Versionado y snapshots de presupuestos               | Evita que un cambio de precio rompa presupuestos anteriores        | Autodesk + nuestro enfoque     |
| 5%         | Export Excel/PDF profesional                         | Necesario para presentar al cliente                                 | Todos                          |

**Conclusión clave:**  
El 20% más valioso es: Lectura de planos + árbol automático + importación de precios + indirectos ponderados + versionado.  
Esto es exactamente lo que estamos construyendo.

### 10.4 Análisis minucioso de los documentos que me proporcionaste
Analicé en profundidad las dos transcripciones completas de las reuniones del 20 de marzo de 2026 con María Emilia Gerlero. Aquí los puntos más relevantes para el diseño del sistema:

**Del primer documento (reunión de 18 minutos):**  
* Importancia de centralizar el maestro de proveedores (razón social, contacto, medio de pedido, frecuencia, plazos, rubro).  
* Dolores explícitos: falta de control de stock, ausencia de trazabilidad, pedidos informales (“radio pasillo”).  
* Necesidad de checklist / perfil de entrada para relevar procesos.  
* Uso de Excel como primer paso aceptable, pero se busca reemplazarlo por sistema.  
* Importancia del módulo de procesos para centralizar mapas y conversaciones.

**Del segundo documento (reunión de 34 minutos):**  
* Se confirma la necesidad de maestro de materiales agrupado por rubro y subgrupo.  
* Campos obligatorios: unidad, precio con/sin IVA, fecha del precio, ubicación de la obra (para traslado).  
* Importancia de analizar traslado vs precio (ubicación del proveedor es clave).  
* Distinción clara entre materiales incluidos en el presupuesto y los que solo se cotizan (pagados por el cliente).  
* Catálogo de mano de obra (capataz, oficial, etc.) y equipos (propios o alquilados).  
* Asignación de gastos de estructura (alquiler, nafta, administración) por obra y por duración.  
* Flujo deseado: desarmar plano → extraer cantidades → trasladar a cómputo → calcular costos.  
* Deseo de lectura automática de planos (Python/OCR/IA) para generar preliminar que luego el jefe de obra valide.  
* Enfoque de módulos reutilizables según tipo de obra.  
* Principio de esencialismo (menos es más) y MVP.

Estos puntos fueron incorporados al Documento Maestro.

---

## 11. Especificación Funcional Recomendada  
**(Módulo a agregar al Documento Maestro)**

**Versión:** 1.0  
**Fecha:** 20 de marzo de 2026  
**Elaborado por:** Grok (xAI)

**Objetivo:** Definir de forma clara, completa y accionable todas las funcionalidades que debe tener el sistema para cumplir con los dolores y necesidades identificados en las reuniones y en el Documento Maestro.

**11.1 Principios de diseño del sistema**  
* Enfoque 80/20: el 20% de las funciones deben resolver el 80% de las necesidades reales.  
* El profesional solo valida y decide; la IA hace el trabajo pesado.  
* Máxima trazabilidad y versionado.  
* Multi-tenant por org_id (tabla memberships).  
* Diseño modular y extensible (para otros clientes en el futuro).  
* Interfaz simple, limpia y moderna (React 18 + Vite).

**11.2 Flujos principales del sistema**  
1. Flujo de creación de presupuesto  
   * Usuario crea nuevo presupuesto → define datos básicos.  
   * Sube planos → IA analiza y propone ítems y cantidades.  
   * Usuario valida/edita el árbol jerárquico.  
   * Importa o selecciona lista de precios.  
   * Sistema calcula costos directos + indirectos automáticamente.  
   * Usuario revisa vista análisis → exporta Excel/PDF o guarda versión.

2. Flujo de actualización de precios  
   * Usuario sube nuevo Excel de precios.  
   * Sistema crea snapshot y notifica en qué presupuestos afectaría.  
   * Usuario decide si actualiza presupuestos existentes o solo futuros.

3. Flujo de versionado  
   * En cualquier momento se puede guardar una versión completa (snapshot).  
   * Se puede comparar versiones o volver a una anterior.

**11.3 Pantallas principales (descripción detallada)**  
**Pantalla 1: Dashboard de Presupuestos**  
* Lista de todos los presupuestos del org_id.  
* Filtros: estado, fecha, cliente, valor total.  
* Botón grande: “+ Nuevo Presupuesto”.

**Pantalla 2: Creación / Edición de Presupuesto**  
* Datos básicos (nombre, cliente, ubicación, tipo de obra, duración).  
* Sección “Planos”: drag & drop de archivos (PDF, imágenes).  
* Botón “Analizar planos con IA”.

**Pantalla 3: Árbol Jerárquico (principal)**  
* Árbol colapsable (Obra → Piso 1 → Cimientos → Columnas → Losa → etc.).  
* Al seleccionar un nodo se abre tabla editable a la derecha.  
* Columnas: Código | Descripción | Unidad | Cantidad | Precio unit. | Subtotal | Indirecto | Total | Notas.  
* Botones: Agregar ítem, Eliminar, Sugerir con IA.

**Pantalla 4: Análisis de Planos con IA**  
* Vista split: izquierda = preview del plano, derecha = lista de ítems sugeridos por IA.  
* Cada sugerencia se puede aceptar, editar o rechazar.  
* Botón “Insertar todos los aceptados en el árbol”.

**Pantalla 5: Configuración de Precios e Indirectos**  
* Importación de Excel de precios.  
* Vista de precios actuales.  
* Configuración de indirectos (estructura %, jefatura %, logística %, etc.) con opción de aplicar por rubro o global.

**Pantalla 6: Vista Análisis**  
* Tabla resumen: Materiales | Mano de Obra | Equipos | Subcontratos | Indirectos | Beneficios | Total Neto.  
* Gráficos (torta y barras).  
* Botones de exportación (Excel y PDF).

**Pantalla 7: Historial de Versiones**  
* Lista de versiones guardadas con fecha, usuario y notas.  
* Botón “Ver versión” y “Restaurar versión”.

**11.4 Permisos y Roles (multi-tenant)**  
* Super Admin: acceso total a todo.  
* Admin de Organización: puede crear/editar presupuestos, configurar precios e indirectos.  
* Usuario Estándar: puede ver y editar presupuestos asignados, pero no configuración global.  
* Solo Lectura: solo visualización.  

Todos los permisos se controlan por org_id.

**11.5 Casos de uso principales**  
1. Caso de uso 1 – Crear presupuesto nuevo desde cero  
2. Caso de uso 2 – Importar Excel existente y convertirlo en presupuesto estructurado  
3. Caso de uso 3 – Analizar plano con IA y validar sugerencias  
4. Caso de uso 4 – Aplicar indirectos y ver análisis financiero  
5. Caso de uso 5 – Exportar presupuesto profesional (Excel + PDF)  
6. Caso de uso 6 – Guardar versión y comparar con anterior  
7. Caso de uso 7 – Actualizar lista de precios sin afectar presupuestos anteriores

**11.6 Requisitos no funcionales**  
* Tiempo de respuesta de IA en planos: máximo 15-30 segundos.  
* Soporte para planos de hasta 20 MB.  
* El sistema debe funcionar offline en modo básico (opcional futuro).  
* Auditoría completa de cambios (tabla audit_logs).  
* Snapshots inmutables de precios y presupuestos.

---

**Fin del Documento Maestro v4.0**  
Este documento es el punto de referencia único y completo para todos los agentes LLM, la consultoría y el desarrollo.

