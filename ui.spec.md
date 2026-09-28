\# Beauty Salon OS — UI/UX Redesign Specification



\## 0. Mission



Redesign the existing beauty salon management application into a premium,

visual and extremely easy-to-use beauty-tech operational system.



DO NOT rewrite the application's business logic unnecessarily.



The existing application already implements core domain functionality.

This task is primarily:



\- information architecture

\- UI architecture

\- UX improvement

\- visual redesign

\- responsive behavior

\- data visualization

\- interaction design

\- motion



Preserve existing calculations and workflows unless this specification

explicitly changes their presentation.



\---



\# 1. Product principles



\## 1.1 Calm over complexity



The owner should never feel like she is using accounting software.



Complex financial concepts must be translated into visual language.



Example:



Instead of exposing raw accounting concepts first:



Ventas: $25,000

Commission: $12,500

Studio: $12,500



Present:



$25.000

├── Maira     $12.500

└── Tu salón  $12.500



Advanced details remain available when needed.



\---



\## 1.2 Progressive disclosure



Do not display every available field immediately.



Primary workflows must expose only required information.



Advanced configuration should appear under:

"Más opciones"



Example:



Register service primary fields:



1\. Service

2\. Professional

3\. Price/payment

4\. Confirm



Secondary fields:



\- discount

\- commission override

\- materials provider

\- notes



\---



\# 2. Navigation architecture



Replace current top navigation with persistent desktop sidebar.



Routes/sections:



Inicio

Agenda

Atenciones

Clientes

Profesionales

Servicios

Caja

Reportes



Bottom:



Configuración



Sidebar footer:



current user

role



Example:



Andrea

Administración



\---



\# 3. Dashboard / Inicio



This becomes the operational command center.



Header:



Buenos días, Andrea ✦



Subtitle:



Tu salón empieza tranquilo hoy.



Right side:



\[current date]

\[notifications]

\[+ Registrar atención]



\---



\# 4. Primary KPI row



Four cards.



\## Ventas de hoy



Primary number.



Example:

$347.500



Secondary comparison:

↑ 12,4 % vs. viernes pasado



\## Comisiones devengadas



$173.750



\## Participación del local



$173.750



\## Atenciones



8

de 14 programadas



Cards must NOT have identical visual importance.



"Ventas de hoy" is primary.



\---



\# 5. Salon Day Timeline



This is the visual centerpiece.



Title:



Tu día en el salón



Subtitle:



8 citas hoy · 3 profesionales · próxima cita en 1 h 12 min



Create horizontal timeline.



X axis:

working hours.



Y axis:

professionals.



Example:



&#x20;       09  10  11  12  13  14  15  16



María       \[Camila]       \[Lucía]    \[Daniela]

Maira           \[Sofía]       \[Valentina]

Petra       \[Ana]                \[Paula]



Appointment cards must show:



client

service



Optional:

status



Statuses:



scheduled

arrived

in\_progress

completed

cancelled



Include vertical current-time indicator.



Interactions:



click appointment -> details

drag appointment -> reschedule (future enhancement)

click empty slot -> create appointment



Motion:

150–250ms.



Never sacrifice schedule readability for animation.



\---



\# 6. Money visualization



Create card:



¿A dónde fue el dinero?



Use donut visualization.



Segments:



Local

Profesionales

Gastos



Center:



total sales



Hover/tap segment:

show exact amount + percentage.



This visualization must use real application data.



Never hardcode production values.



\---



\# 7. Weekly revenue



Card:



Resumen semanal



Line/area chart.



X:

days.



Y:

sales.



Tooltip:



date

sales

appointments



Current day visually identifiable.



\---



\# 8. Team performance



Card:



Rendimiento del equipo



Each professional:



avatar

name

revenue

appointments

visual progress indicator



Do NOT frame this aggressively as employee competition.



Goal:

operational visibility.



\---



\# 9. Services performance



Card:



Servicios más vendidos



Rows:



service

number of bookings

revenue

visual bar



Sort by revenue or bookings.



Provide selector if useful.



\---



\# 10. Upcoming appointments



Card:



Próximas citas



Show maximum 3–5 items.



Each:



time

client

service

professional



CTA:



Ver agenda →



\---



\# 11. Action center



Card:



Pendientes de hoy



Examples:



Cobrar 2 atenciones

Confirmar llegada de Valentina

Registrar salida de insumos



Every item should be actionable.



The dashboard should help the owner answer:



"What should I do next?"



\---



\# 12. Cash card



Card:



Caja del día



Status badge:



Día abierto

or

Día cerrado



Metrics:



Efectivo esperado

Efectivo contado

Diferencia

Resultado operativo



Primary CTA:



Cerrar día



Do not expose the complete cash movement table on Dashboard.



Detailed information belongs in Caja.



\---



\# 13. Register service UX



Current business logic must remain.



Redesign flow into steps.



\## Step 1 — Servicio



Show service cards/buttons.



Manicura

Pedicura

Cejas

etc.



\## Step 2 — Profesional



Show available professionals.



Avatar + name.



\## Step 3 — Cobro



Show:



service

price



Visual split:



Professional commission

Studio share



Payment method.



Primary CTA:



Confirmar y cobrar $XX.XXX



Advanced:



Más opciones



Contains:



discount

commission %

materials provider

notes if implemented



\---



\# 14. Closing Day Experience



Closing the day should feel intentional.



Trigger:

Cerrar día



Open focused overlay/modal.



Step 1:



summary



Atenciones

Ventas

Comisiones

Gastos

Resultado



Step 2:



Efectivo esperado



Ask:



¿Cuánto tienes realmente?



numeric input.



Step 3:



Calculate difference.



If zero:



✓ Caja cuadrada



If discrepancy:



show amount clearly.



Allow note/reason.



Step 4:



confirmation.



Display:



Día cerrado



Small elegant success animation.



No confetti explosion.



Motion should feel premium.



\---



\# 15. Reports



Reports page prioritizes visualization before tables.



Sections:



Sales trend

Revenue distribution

Top services

Professional performance

Expenses

Commission status



Detailed tables appear below charts.



Charts answer:

"What happened?"



Tables answer:

"What exactly produced that number?"



\---



\# 16. Clients



Introduce Clients section.



Client profile:



name

contact

last visit

total visits

lifetime spend

usual professional

usual service

next appointment



Include:



Beauty Timeline



Chronological history:



appointment

service

professional

amount

notes



Future capability:



client retention indicator.



Possible states:



Active

Due soon

At risk

Inactive



Do not implement automated classification unless supporting data exists.



\---



\# 17. Visual system



\## Colors



\--background: #FBF8F5

\--surface: #FFFFFF

\--rose-soft: #EED8D8

\--rose: #D8AAAA

\--rosewood: #8E535B

\--champagne: #D8BE91

\--plum: #30242B



Semantic colors must exist separately:



success

warning

danger

info



Do not use rose for every semantic state.



\---



\# 18. Typography



Two-font hierarchy.



Display / editorial:

serif.



Use for:



page titles

large financial figures

selected editorial moments



UI:

modern sans-serif.



Use for:



navigation

buttons

forms

tables

labels

charts



Readability always wins.



\---



\# 19. Spacing



Use consistent spacing scale.



4

8

12

16

24

32

48

64



Avoid arbitrary spacing values unless necessary.



\---



\# 20. Cards



Default:



16–20px radius

subtle border

very subtle shadow

white / warm-white surface



Cards should NOT all look identical.



Use hierarchy through:



size

position

typography

background

content density



not excessive color.



\---



\# 21. Motion language



Motion has semantic meaning.



FLOW

Appointments move.



SPLIT

Money divides.



RESOLVE

Completed tasks disappear/resolve.



ATTENTION

Important pending items softly pulse/highlight.



CONFIRM

Successful operations settle into place.



Durations:



micro: 120–180ms

standard: 180–280ms

large transitions: 300–500ms



Respect prefers-reduced-motion.



\---



\# 22. Charts



Charts must be:



minimal

readable

interactive

responsive



Avoid:



3D charts

unnecessary grid lines

rainbow colors

excessive legends



Prefer:



line

area

bar

donut



Tooltips should show exact values.



CLP formatting:



$347.500



not:



$347,500



Use Chilean number formatting.



\---



\# 23. Responsive strategy



Desktop:

full sidebar + dashboard grid.



Tablet:

collapsible sidebar.



Mobile:

bottom navigation or compact drawer.



Mobile dashboard prioritization:



1\. today's sales

2\. next appointment

3\. pending actions

4\. timeline

5\. cash status

6\. analytics



Do not simply shrink desktop layout.



\---



\# 24. Accessibility



Minimum WCAG AA contrast where possible.



Keyboard navigation.



Visible focus states.



Buttons must have accessible labels.



Charts require textual summaries.



Never communicate status exclusively through color.



Respect reduced motion.



\---



\# 25. Technical constraints



Inspect existing project before changing architecture.



Reuse current:



business rules

data persistence

entities

calculations

event logic



Do not replace working logic merely to accommodate UI.



Create reusable UI primitives.



Suggested architecture:



components/

&#x20; layout/

&#x20; dashboard/

&#x20; appointments/

&#x20; services/

&#x20; finance/

&#x20; clients/

&#x20; professionals/

&#x20; charts/

&#x20; ui/



Avoid giant page components.



\---



\# 26. Data visualization library



If the project does not already contain a chart library,

prefer a lightweight React-compatible charting solution appropriate

to the existing stack.



Do not add multiple visualization libraries.



\---



\# 27. 3D policy



DO NOT put heavy WebGL/Three.js scenes inside operational dashboard screens.



Operational UI performance has priority.



3D can later be used for:



marketing site

onboarding

empty states

brand moments

interactive salon visualization



The dashboard should achieve premium quality primarily through:



layout

typography

motion

microinteractions

visualization

hierarchy.



\---



\# 28. Existing functionality that must survive



Preserve:



service registration

professional assignment

price

discount

commission calculation

studio participation

materials ownership



Preserve:



payments

payment methods



Preserve:



operating expenses

administrative salaries

owner withdrawals

commission payouts



Preserve:



cash opening balance

cash counting

expected cash

cash difference



Preserve:



day closing

audit history



Preserve:



appointments

date

time

client

contact

service

professional



Preserve:



weekly reporting

professional reporting



Preserve:



professional configuration

commission percentage



Preserve:



service catalog

reference price



Preserve:



backup

restore

demo reset



\---



\# 29. Implementation order



DO NOT attempt the entire redesign simultaneously.



PHASE 1

Design tokens + typography + app shell + sidebar.



PHASE 2

Dashboard layout and KPI cards.



PHASE 3

Day timeline.



PHASE 4

Charts and financial visualization.



PHASE 5

Register-service workflow.



PHASE 6

Cash / close-day experience.



PHASE 7

Agenda.



PHASE 8

Reports.



PHASE 9

Professionals and services.



PHASE 10

Clients if domain support exists.



PHASE 11

Responsive + accessibility + motion polish.



After every phase:



run application

check console

test existing workflows

verify persistence

verify calculations

check responsive layout



Do not continue if existing business logic is broken.



\---



\# 30. Definition of Done



The redesign is complete when:



\- all previous core functionality still works

\- dashboard can be understood in under 5 seconds

\- common operations require fewer interactions

\- financial information is visually understandable

\- UI feels consistent across pages

\- desktop/tablet/mobile are usable

\- charts use real state

\- animations do not block interaction

\- accessibility basics are implemented

\- no console errors

\- no broken existing calculations

\- no hardcoded demo values leaking into real application state

\- visual result closely follows the supplied reference image



The reference image defines VISUAL DIRECTION.



This specification defines PRODUCT BEHAVIOR.



When they conflict:



1\. preserve business correctness

2\. preserve usability

3\. follow this specification

4\. follow reference aesthetics



Do not sacrifice functionality merely to reproduce the screenshot.

