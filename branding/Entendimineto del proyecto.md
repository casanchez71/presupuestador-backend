
LO QUE ENTENDIO CLAUDE CODE de mi pedido:

El problema real
Un arquitecto hoy hace presupuestos así:

Recibe un plano de obra
Abre un mega Excel de 55 hojas (tipo Las Heras)
Manualmente descompone la obra en secciones (pisos, columnas, losas, etc.)
Para cada sección, asigna materiales, mano de obra, equipos
Busca precios en listas (que cambian cada mes)
Calcula costos directos, le suma indirectos (estructura, jefatura, logística)
Le pone márgenes de beneficio
Exporta el presupuesto para presentar al cliente
Esto tarda días o semanas. Es manual, propenso a errores, y cada vez que cambia un precio hay que recalcular todo.

Lo que vos querés
Un sistema donde el arquitecto haga esto:

Crea un presupuesto → dice "Edificio Las Heras, 4 pisos"
Sube el plano → la IA lo analiza y propone las secciones automáticamente (estructura, albañilería, instalaciones, etc.)
Valida el árbol → el arquitecto revisa, ajusta, confirma
Se cargan precios → importa lista de precios (Excel) o usa catálogo existente
El sistema calcula todo → materiales × cantidad, mano de obra, directo, indirecto, beneficio, neto
El arquitecto ajusta → cambia cantidades, corrige precios, el sistema recalcula solo
Exporta → PDF/Excel profesional listo para el cliente
Versiona → guarda snapshots, compara versiones, ve historial de cambios
Lo que lo hace único (la brecha que encontraste)
Togal.AI, Beam, Kreo, STACK — ninguno resuelve bien:

Indirectos ponderados (estructura 15%, jefatura 8%, logística 5%, herramientas 3%)
Gastos de estructura distribuidos
Trazabilidad completa (quién cambió qué, cuándo, por qué)
Adaptación argentina (formatos, unidades, listas de precios locales)
La visión futura
Agentes de IA que operen el sistema: un agente que lee planos, otro que busca precios, otro que optimiza costos. El sistema tiene que estar preparado para eso — API limpia, datos bien estructurados, acciones atómicas.

LO QUE HAY HOY
Componente	Estado	Calidad
API REST (17 endpoints)	✅ Funcionando	Profesional — modular, tipado, testeado
Import Excel Las Heras (55 hojas)	✅ Funcionando	Bueno — parsea catálogos + ítems + recursos
Modelo de datos (8 tablas)	✅ Creado	Bueno — soporta el desglose completo
Auth + Multi-tenant	✅ Funcionando	Profesional — Modelo C, dual Supabase
IA Vision (planos → ítems)	✅ Funcionando	Básico — extrae ítems pero no calcula cantidades con precisión
Cálculos automáticos	❌ No existe	Los totales no se calculan solos
Integración catálogo → precios	❌ No existe	Se importan catálogos pero no se usan para preciar
Export PDF	❌ No existe	Solo Excel básico
Frontend real	❌ No existe	Solo Swagger docs
Resumen: Los cimientos están bien, pero el edificio no está construido.

LO QUE PROPONGO
Filosofía: "Excel inteligente, no ERP pesado"
No vamos a construir un SAP. Vamos a construir lo que el arquitecto realmente usa: un Excel que piensa solo, conectado a IA, con precios actualizados y cálculos automáticos.

Las 3 capas del sistema
┌─────────────────────────────────────────────┐
│  CAPA 3: INTERFAZ                           │
│  React — lo que ve el arquitecto             │
│  Árbol jerárquico + tablas editables         │
│  + vista análisis + exports                  │
├─────────────────────────────────────────────┤
│  CAPA 2: INTELIGENCIA                       │
│  IA Vision (planos → secciones)              │
│  IA Pricing (catálogo → precios sugeridos)   │
│  IA Optimización (detecta inconsistencias)   │
│  → Futuro: Agentes autónomos                │
├─────────────────────────────────────────────┤
│  CAPA 1: MOTOR DE CÁLCULO                  │
│  Cálculos automáticos (cascada)              │
│  Catálogos de precios versionados            │
│  Indirectos ponderados configurables         │
│  Versionado + auditoría                      │
└─────────────────────────────────────────────┘

Orden de construcción (lo que importa primero)
FASE 1 — Motor de cálculo (sin esto nada funciona)

Cálculos automáticos en cascada: cantidad × precio → directo → + indirecto → + beneficio → neto
Integración catálogo: cuando asignás un recurso, el precio se busca del catálogo
Recálculo masivo: cambiás un precio en el catálogo → se actualiza todo
Copia de presupuestos
Export PDF profesional
FASE 2 — Frontend funcional (sin esto nadie lo puede usar)

Dashboard de presupuestos
Árbol jerárquico editable (la pantalla principal)
Tablas de costos editables en línea
Vista análisis (el resumen tipo 01_C&P)
Import Excel + Upload de planos
Export PDF/Excel
FASE 3 — IA avanzada (lo que lo hace diferente)

IA Vision mejorada: plano → secciones con cantidades estimadas
IA Pricing: sugiere precios del catálogo para cada recurso
IA Validación: "Este ítem tiene costo de mano de obra pero no materiales — ¿es correcto?"
IA Comparación: "Este presupuesto es 30% más caro que el anterior para obra similar"
FASE 4 — Agentes (el futuro)

Agente que monitorea precios de mercado
Agente que lee planos automáticamente al subirse
Agente que sugiere optimizaciones de costos
API preparada para que cualquier agente opere el sistema