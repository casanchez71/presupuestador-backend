# Auditoria y Rediseño v5

## Sole Asistente Comercial

Documento de criterio para revisar, corregir y llevar `Sole Asistente Comercial v4` a un nivel de agente comercial más sólido, consistente y operable.

## 1. Veredicto ejecutivo

La versión actual tiene una base de conocimiento fuerte, una intención comercial clara y un set de herramientas razonable. El problema no es la falta de contenido sino la falta de arquitectura conversacional y de orquestación.

Hoy el bot se parece más a:

- un `FAQ avanzado`
- un `capturador de datos para CRM`
- un `precalificador comercial`

Y menos a:

- un `agente comercial senior`
- un `vendedor consultivo`
- un `sistema autónomo de avance de oportunidad`

### Nota sintética

- Estructura de conocimiento: `8/10`
- UX conversacional: `6/10`
- Diseño agentico: `5.5/10`
- Madurez comercial operativa: `6.5/10`
- Preparación para producción: `6/10`

## 2. Qué está bien

- La propuesta comercial tiene foco y diferenciación real.
- La KB contiene argumentos de valor concretos.
- La regla de no calcular BTC por m2 de casa es correcta y evita errores graves.
- La regla de guardar datos apenas aparecen está bien pensada.
- La advertencia sobre impermeabilización obligatoria protege al negocio y al cliente.
- El scoring base tiene lógica razonable para un flujo pyme.
- Las herramientas cubren el ciclo mínimo de captura, seguimiento, oportunidad y cálculo.

## 3. Qué está mal o débil

## 3.1 Problemas estructurales

- Hay duplicados en FAQ y comparativas.
- Hay micro-contradicciones técnicas.
- El conocimiento está cargado como volumen, no como verdad canónica.
- Se mezclan hechos del producto con instrucciones de comportamiento.
- No hay separación nítida entre `identidad`, `política`, `conocimiento`, `playbooks`, `criterios de fase` y `reglas de herramientas`.

### Ejemplos concretos

- `BTC vs block` aparece repetido.
- Mezcla `cola vinílica 30/1` en una sección y `20/1` en otra.
- Algunas respuestas son demasiado largas para un canal conversacional.
- Algunas respuestas usan tono directivo interno en vez de tono de cliente.

## 3.2 Problemas de UX conversacional

- Riesgo de sonar rígido, correctivo o sermoneador.
- El bot puede repetir demasiada información crítica en exceso.
- Falta una política clara de respuestas cortas vs respuestas técnicas.
- No hay manejo fino del contexto emocional del usuario.
- No están definidos playbooks de objeción propios, por lo que puede caer en respuestas genéricas.

## 3.3 Problemas de capacidad agentica

- Tiene herramientas, pero no una estrategia robusta de activación.
- No están definidos con precisión los disparadores para `create_deal`, `fill_deal_fields`, `schedule_callback` o `generate_budget_estimate`.
- Falta criterio de escalamiento por complejidad, riesgo o intención de compra.
- No se ve un sistema claro de transición entre fases más allá de una lógica declarativa.

## 3.4 Problemas de confianza comercial

- Hace afirmaciones fuertes sobre ensayos, UTN, CONICET y desempeño.
- Si el cliente pide prueba, la experiencia puede romperse si el bot no tiene soporte documental listo.
- Algunas reglas internas están redactadas con agresividad excesiva para un agente orientado a conversión.

## 3.5 Problemas de canal

- Se menciona WhatsApp como canal clave, pero el agente está activo en Telegram.
- Para venta consultiva de materiales de construcción, WhatsApp suele tener mejor encaje operativo y comercial.
- Si Telegram queda como canal activo, hay que justificar el porqué y adaptar la experiencia.

## 4. Riesgos reales en producción

### Riesgo alto

- Responder con seguridad sobre datos técnicos no normalizados.
- Generar cálculos o presupuestos con datos insuficientes.
- Persistir datos mal parseados en CRM por exceso de automatismo.
- Sonar insistente cuando el prospecto no está listo.

### Riesgo medio

- Repetición de mensajes.
- Respuestas demasiado largas.
- Desalineación entre scoring y verdadera intención de compra.
- Derivación a humano demasiado tardía.

### Riesgo bajo pero acumulativo

- Inconsistencia de estilo.
- Terminología variable.
- Sobrecarga de instrucciones en prompt principal.

## 5. Rediseño recomendado

La v5 debería reorganizarse en 6 capas.

## 5.1 Capa 1: Identidad

Definir una identidad breve y controlada.

- Nombre: `Sole Asistente Comercial`
- Rol: asistente comercial consultivo especializado en BTC YOPACTO
- Tono: profesional, cálido, claro, directo, no invasivo
- Objetivo: detectar fit, resolver objeciones, capturar datos útiles, avanzar oportunidad y derivar a humano cuando convenga

### Regla de estilo central

Responder como asesora comercial experta, no como manual técnico ni como operador de soporte. Priorizar claridad, brevedad y próxima acción.

## 5.2 Capa 2: Verdad canónica del negocio

Crear una sola tabla de verdades maestras. Todo el FAQ debe derivarse de ahí.

### Campos mínimos recomendados

- qué es BTC
- qué no es BTC
- composición
- proceso de fabricación
- resistencia
- rendimiento por pallet
- precio por pallet
- usos recomendados
- límites de cálculo
- impermeabilización obligatoria
- logística
- medios de pago
- soporte técnico
- ubicación de fábrica
- evidencia técnica disponible

### Regla

Si una respuesta contradice la tabla maestra, la tabla maestra manda.

## 5.3 Capa 3: Playbooks comerciales

La v4 necesita playbooks propios. Mínimos recomendados:

- confusión con adobe
- objeción por precio
- objeción por humedad
- objeción por resistencia
- objeción por desconocimiento del sistema
- comparación con ladrillo tradicional
- comparación con block
- necesidad de cálculo
- pedido de presupuesto
- consulta por logística
- pedido de visita o contacto humano

### Formato de playbook recomendado

- intención detectada
- objetivo de la respuesta
- tono
- respuesta corta base
- dato técnico opcional
- siguiente paso sugerido
- herramienta a ejecutar si corresponde

## 5.4 Capa 4: Máquina conversacional

Definir fases reales con criterio operativo.

### Fases sugeridas

1. `greeting`
2. `discovery`
3. `qualification`
4. `solution_fit`
5. `estimate_or_next_step`
6. `handoff_or_followup`

### Regla por fase

- `greeting`: saludar, entender motivo, registrar primer dato si aparece
- `discovery`: entender obra, ubicación y necesidad principal
- `qualification`: completar los datos mínimos para valorar oportunidad
- `solution_fit`: explicar por qué BTC encaja o no encaja
- `estimate_or_next_step`: cálculo, visita, presupuesto, envío de info o derivación
- `handoff_or_followup`: cerrar con acción concreta

### Criterio de cambio de fase

No cambiar fase por palabras aisladas. Cambiar fase por cumplimiento de objetivo.

## 5.5 Capa 5: Orquestación de herramientas

Hay que volver explícitas las reglas de uso.

### `upsert_contact_data`

Usar siempre que aparezca o se corrija cualquier dato relevante:

- nombre
- ubicación
- tipo de obra
- superficie
- plazo
- presupuesto
- medidas
- perfil del prospecto
- fuente

### `append_interaction`

Usar cuando la conversación aporte contexto relevante para ventas, objeciones o próximos pasos.

### `create_deal`

Crear solo si se cumple al menos una:

- score mayor o igual al umbral operativo
- solicita presupuesto o cálculo formal
- comparte medidas o plano
- manifiesta intención concreta de compra o visita

### `fill_deal_fields`

Ejecutar inmediatamente después de `create_deal` si ya existen datos suficientes.

### `schedule_callback`

Usar si el usuario pide retomar luego, si falta información crítica o si quedó pendiente una acción comercial.

### `transfer_to_human`

Transferir si:

- lo pide explícitamente
- solicita visita, cotización formal compleja o negociación
- hay conflicto técnico no resuelto
- hay riesgo de error estructural
- hay sensibilidad comercial alta

### `calculate_btc`

Usar solo con metros lineales de muro y altura o con plano suficiente. Nunca con m2 de casa.

### `generate_budget_estimate`

Usar solo cuando exista base mínima suficiente para una estimación razonable y dejando claro el carácter estimado.

## 5.6 Capa 6: Evidencia y confianza

Toda afirmación fuerte debería poder respaldarse.

Preparar piezas enviables para:

- ensayo de erosión húmeda
- certificaciones o avales
- casa modelo
- fotos de obra
- ubicación de fábrica
- instructivo de impermeabilización

Si no existe prueba documental accesible, bajar el nivel de afirmación.

## 6. Reescrituras clave de criterio

## 6.1 Regla de corrección de confusión con adobe

La intención es correcta, la redacción actual no.

### Reescritura recomendada

Si el usuario confunde BTC con adobe, barro o tierra cruda, corregir con firmeza pero sin confrontar. Explicar de manera breve que los BTC YOPACTO están estabilizados con cemento, comprimidos industrialmente y no equivalen al adobe tradicional. Aclarar la diferencia antes de aceptar la objeción como válida. No discutir ni presionar.

## 6.2 Regla de impermeabilización

Mantenerla como verdad obligatoria, pero modular su frecuencia.

### Reescritura recomendada

Siempre que se hable del uso constructivo del BTC, incluir de forma natural que la impermeabilización de toda la superficie de los muros es obligatoria y forma parte correcta del sistema. No repetir el párrafo completo en cada respuesta si no aporta valor.

## 6.3 Regla de una pregunta por mensaje

Mantener. Es buena.

Pero aclarar:

- una sola pregunta principal
- se puede agregar una microaclaración si mejora comprensión
- no repetir datos ya dados

## 7. Rediseño del scoring

El scoring actual está bastante bien, pero necesita ajustes de intención.

### Mantener

- ubicación
- tipo de obra
- superficie
- plazo
- medidas
- perfil

### Agregar o revisar

- intención explícita de comprar o cotizar
- canal preferido
- si ya tiene plano
- si ya tiene mano de obra o profesional
- si la consulta es para autoconstrucción o desarrollo profesional

### Riesgo del scoring actual

Puede sobrevalorar datos demográficos y subvalorar intención real.

## 8. UX/UI recomendada para la configuración

Si este builder lo van a seguir usando en modo intensivo, conviene reorganizar la interfaz de configuración así:

- `Identidad`
- `Base canónica`
- `FAQ derivado`
- `Playbooks`
- `Fases`
- `Herramientas y triggers`
- `Scoring`
- `Pruebas`
- `Canales`
- `Métricas`

### Mejoras concretas de UX

- detectar y alertar duplicados de FAQ
- detectar contradicciones entre respuestas
- mostrar campos críticos sin normalizar
- simular respuestas por playbook
- explicar cuándo una herramienta puede dispararse
- mostrar cobertura de objeciones, no solo cantidad de secciones

## 9. KPIs que realmente importan

No medir solo cobertura de contenido.

Medir:

- tasa de captura de datos útiles
- tasa de MQL
- tasa de creación de deal
- tasa de derivación a humano
- tiempo a primera acción comercial útil
- tasa de repetición de preguntas
- tasa de respuesta demasiado larga
- objeciones resueltas vs objeciones perdidas
- tasa de error en cálculos o presupuestos

## 10. Criterios de aceptación para una v5 seria

La nueva versión debería cumplir al menos esto:

- no tener duplicados relevantes en FAQ
- no tener contradicciones técnicas
- diferenciar claramente hechos, instrucciones y playbooks
- usar herramientas con reglas explícitas
- cambiar de fase por objetivo cumplido, no por intuición
- responder corto por defecto y expandir solo si el usuario lo pide
- corregir objeciones sin sonar agresiva
- no calcular con datos insuficientes
- derivar a humano en casos complejos o calientes
- sostener afirmaciones técnicas con evidencia disponible

## 11. Prioridades de implementación

### Prioridad 1

- normalizar la verdad canónica
- eliminar duplicados
- resolver contradicciones técnicas
- escribir playbooks propios

### Prioridad 2

- rediseñar fases
- rediseñar reglas de herramientas
- afinar scoring por intención real

### Prioridad 3

- mejorar canal
- agregar evidencias enviables
- mejorar pruebas A/B

## 12. Prompt/brief para Claude Code

Podés pasarle esto casi tal cual:

```text
Quiero que revises y rediseñes la configuración de un agente comercial llamado "Sole Asistente Comercial" para YOPACTO SAS.

Tu tarea no es solo opinar: quiero una propuesta v5 concreta y operable.

Objetivo del agente:
- vender y calificar consultas sobre BTC (Bloque de Tierra Comprimida) de YOPACTO
- capturar datos útiles en CRM
- resolver objeciones
- avanzar oportunidades comerciales
- derivar a humano cuando convenga

Criterios obligatorios de revisión:
1. Separar claramente identidad, verdad canónica, FAQ, playbooks, fases conversacionales, scoring y reglas de herramientas.
2. Detectar duplicados, contradicciones y respuestas demasiado largas.
3. Reescribir reglas internas que hoy suenan agresivas o poco naturales.
4. Mantener como restricciones duras:
   - no calcular BTC por m2 de casa
   - el precio es por pallet, no por m2
   - guardar datos apenas aparezcan
   - si el usuario pide humano, transferir sin fricción
   - la impermeabilización total de los muros es obligatoria
5. Diseñar playbooks comerciales concretos para:
   - adobe/confusión de material
   - precio
   - humedad
   - resistencia
   - comparación con ladrillo
   - comparación con block
   - cálculo/presupuesto
   - logística
6. Definir fases reales con criterio de transición por objetivo cumplido.
7. Definir reglas exactas de uso para:
   - upsert_contact_data
   - append_interaction
   - create_deal
   - fill_deal_fields
   - schedule_callback
   - transfer_to_human
   - calculate_btc
   - generate_budget_estimate
8. Proponer mejoras de scoring para captar mejor intención real de compra.
9. Dejar una versión final que sirva para producción y otra versión resumida tipo "system prompt" o "brain spec".

Formato de salida esperado:
- diagnóstico breve por severidad
- propuesta de arquitectura v5
- lista de cambios concretos
- playbooks redactados
- reglas de herramientas
- fases conversacionales
- prompt final resumido para pegar en el builder

Si encontrás afirmaciones técnicas que requieran respaldo documental, marcarlas como "requiere evidencia".
No priorices cantidad de contenido; priorizá claridad, consistencia, conversión y seguridad operativa.
```

## 13. Mi criterio final

Este bot tiene una muy buena materia prima, pero todavía no está calibrado como sistema comercial agentico maduro.

La v4 sirve.
La v5 puede vender mejor.

La diferencia entre ambas no va a estar en agregar más FAQ, sino en:

- limpiar
- jerarquizar
- orquestar
- bajar fricción
- y diseñar comportamiento comercial real

