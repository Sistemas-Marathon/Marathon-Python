# Plan: Migración de Marathon-Python (Streamlit) a React + TSX / NestJS

Este documento es un plan de ejecución por fases, pensado para correr cada fase como
un prompt separado (en sesiones distintas) y no gastar todo el contexto de una vez.
Cada fase es independiente y termina en un estado funcional y verificable.

## Objetivo

Reemplazar el portal interno de Streamlit (`marathon-interno.streamlit.app`) por una
app propia en React + TypeScript (frontend) y NestJS (backend), corriendo primero en
localhost, con los mismos reportes, y con un login que falta hoy (la app de Streamlit
queda expuesta a cualquiera con el link, sin autenticación).

## Decisiones ya tomadas

- **Backend**: NestJS, conexión directa a la misma base SQL Server (`MARAPROD24` en
  `181.209.94.152:29434`) usando el paquete `mssql` de Node (driver Tedious), con las
  mismas credenciales que ya usa `pymssql` en Streamlit (via `.streamlit/secrets.toml`
  hoy; en Nest van en un `.env`, nunca commiteado).
- **Frontend**: React + TypeScript con Vite, React Router, TanStack Query para pedir
  datos a la API, TanStack Table para las tablas de resultados.
- **Las queries SQL ya están validadas** contra la base real en los módulos `.py`
  actuales de este repo — al portar cada reporte, copiar la query tal cual desde el
  archivo Python correspondiente (están probadas, no hay que re-derivarlas).
- **Corre en localhost por ahora**: nada de exponer puertos ni desplegar a un server
  hasta que se decida explícitamente avanzar con eso (es la última fase).

## Login: integración con RRHH-Marathon (resuelto)

"Login de rrhh-marathon" es el backend NestJS ya existente del proyecto **RRHH-Marathon**
(`/Users/sistemas/Desktop/Proyectos/RRHH-Marathon/backend`), que ya tiene usuarios,
roles y permisos de toda la empresa. **No se construye un sistema de login propio.**
De RRHH-Marathon no se toca ni se modifica absolutamente nada de su código — el
backend nuevo solo lo consume como cliente HTTP, exclusivamente para el login:

- Endpoint real: `POST /users/login` (sin prefijo global), body
  `{ "email": string, "password": string }`, devuelve
  `{ "access_token": string, "refresh_token": string }`.
- Hay también `GET /users/me` (con el `access_token` en `Authorization: Bearer ...`)
  para traer perfil, rol y permisos del usuario logueado.
- **URL confirmada**: `http://181.209.94.152:3001` (misma IP que la SQL Server, puerto
  3001). Se encontró en `PORTAL-MARATHON/.env.example` (`VITE_AUTH_API_BASE_URL`), el
  portal central ya existente que usan para loguear a otras apps internas (Mi Tienda,
  SCamaras) con este mismo backend. Va como `RRHH_MARATHON_API_URL` en el `.env`.
- **Referencia de implementación real**: `PORTAL-MARATHON/src/auth/authService.ts`
  (solo lectura, no tocar ese repo) ya tiene el cliente exacto de este login
  (`login`, `getCurrentUser` via `/users/me`, `refresh` via `/users/refresh`) — sirve
  como ejemplo de contrato de API ya probado en producción, replicar ese mismo
  contrato en el backend nuevo.
- Todos los demás módulos de RRHH-Marathon (`schedules`, `performance`,
  `sales-audit`, `transfer-litigation`, etc.) — aunque algunos se superponen en
  dominio con reportes de este plan (ver tabla de abajo) — **no se consumen ni se
  tocan**. Cada reporte de este proyecto se construye de cero, de punta a punta,
  siguiendo el inventario completo más abajo.

### Superposición de dominio detectada (solo como referencia, no cambia el alcance)

| Reporte de este plan | Módulo similar ya existente en RRHH-Marathon (no se usa) |
|---|---|
| Reporte Actividad en Masa | `performance/absence-metrics` (misma lógica MPLAGESALARIE+CHOIXCOD) |
| Llegadas Tardes y Justificaciones | `performance/lateness-metrics`, `schedules` |
| Transferencias TEM-TRE | `transfer-litigation` (enfocado en detectar litigios, no es un listado plano) |

El resto de los 19 reportes no tiene equivalente detectado en RRHH-Marathon.

## Inventario completo de reportes a portar (desde `app.py` actual)

**Supply Chain**
- Reposición Cruzada (`reposicion_cruzada.py`)
- Mínimos y Máximos (`min_max.py`)
- Lista artículos (`lista_art.py`)

**RRHH**
- Tickets por hora (`rrhh_tickets_por_hora.py`)
- Transferencias TEM-TRE (`rrhh_tem_tre.py`)
- Llegadas Tardes y Justificaciones (`rrhh_lleg_tardes.py`)
- Modificaciones de Horarios (`rrhh_modif_horarios.py`)
- Tickets por Comercial (`rrhh_tickets_por_comercial.py`)
- Desglose de Recibos (`rrhh_desglose_recibos.py`)
- Desglose de Recibos DAB (`rrhh_desglose_recibos_dab.py`)
- Liquidación de Comisiones (`rrhh_liquidacion_comision.py`)
- Reporte Martin (`rrhh_martin.py`)
- Reporte Actividad en Masa (`rrhh_actividad.py`)
- Recepción de Proveedor (`rrhh_recepcion_proveedor.py`)

**Marketing**
- Generador de Códigos de Barras (`marketing_codigos_barra.py`)

**Control cajas**
- Consulta por forma de pago (`cajas_formas_de_pago.py`)
- Consulta por descuentos empleados (`cajas_desc_empleado.py`)
- Consulta de clientes por venta (`cajas_ventas_cliente.py`)
- Consulta de ventas por banco (`cajas_ventas_banco.py`)

Total: 19 reportes + el generador de códigos de barra (este último es distinto: no es
consulta a DB con fecha, genera imágenes — se porta aparte, no sigue el patrón
genérico).

---

## Fase 0 — Scaffolding del proyecto

**Prompt sugerido**: "Arrancá la Fase 0 del plan en PLAN_MIGRACION_REACT_NEST.md:
scaffolding del monorepo."

- Crear carpeta nueva del proyecto (monorepo con `/frontend` y `/backend`).
- `backend/`: Nest CLI, módulo de conexión a SQL Server (`mssql`), un endpoint
  `GET /health` que haga una query trivial (`SELECT 1`) contra `MARAPROD24` para
  confirmar que la conexión funciona. Config via `.env` + `.gitignore`.
- `frontend/`: Vite + React + TypeScript, layout vacío, confirmar que levanta en
  `localhost:5173` (o el puerto que elija Vite) y puede pegarle al `/health` del
  backend sin error de CORS.
- Entregable: ambos corriendo en localhost, health-check end-to-end funcionando.
- **No** se toca ningún reporte real todavía.

## Fase 1 — Autenticación (proxy contra el login de RRHH-Marathon)

**Prompt sugerido**: "Arrancá la Fase 1 del plan: login proxy contra RRHH-Marathon."

- Requiere tener `RRHH_MARATHON_API_URL` confirmada (ver sección de arriba).
- Backend: módulo `auth` propio que **no guarda usuarios ni passwords** — es un
  proxy delgado:
  - `POST /auth/login` (de este backend nuevo) recibe `{ email, password }`, reenvía
    tal cual a `POST {RRHH_MARATHON_API_URL}/users/login`, y devuelve al frontend lo
    que responda ese endpoint (`access_token` / `refresh_token`) o el error de
    credenciales inválidas tal cual venga.
  - Ese `access_token` se usa como la sesión de este portal también: cada endpoint
    propio (los reportes) valida el token contra `GET {RRHH_MARATHON_API_URL}/users/me`
    (o decodificando el JWT si está firmado con una clave que podamos verificar —
    confirmar esto en la Fase 1 mirando cómo está armado `getJwtSecret()` en
    RRHH-Marathon, sin tocar ese repo, solo para saber si el JWT es verificable acá
    o si hay que validar siempre contra `/users/me`).
- Frontend: pantalla de login (mismo email/password que ya usan en la app de
  RRHH-Marathon), guardado del token, rutas protegidas.
- **No hay alta de usuarios en este proyecto** — los usuarios ya existen en
  RRHH-Marathon, acá solo se autentica contra ellos.
- Entregable: no se puede ver nada del portal sin loguearse, y el login funciona con
  las mismas credenciales que ya usa la gente en RRHH-Marathon.

## Fase 2 — Shell y navegación

**Prompt sugerido**: "Arrancá la Fase 2 del plan: layout y navegación."

- Sidebar con las 4 áreas (Supply Chain, RRHH, Marketing, Control cajas) y el listado
  de reportes de cada una (ver inventario arriba), replicando la estructura actual
  de `app.py`.
- Cada ítem navega a una ruta (`/rrhh/liquidacion-comisiones`, etc.) que por ahora
  puede mostrar solo un placeholder "en construcción".
- Entregable: navegación completa funcionando, protegida por el login de la Fase 1.

## Fase 3 — Primer reporte real de punta a punta (reporte molde)

**Prompt sugerido**: "Arrancá la Fase 3 del plan: portar Liquidación de Comisiones
completo como reporte molde."

- Elegido como primero por ser representativo (filtro de fechas, joins, columna
  calculada, export a Excel): **Liquidación de Comisiones**.
- Backend: endpoint `GET /rrhh/liquidacion-comisiones?fechaInicio=&fechaFin=`,
  reusando la query exacta de `rrhh_liquidacion_comision.py` (incluye el filtro de
  artículos vacíos, columnas NOMBRE_ARTICULO/CLASIFICACION, orden de columnas
  M/N/O ya definido).
- Backend: endpoint de export a Excel (generar el `.xlsx` en el server, que el
  frontend descargue), replicando `df.to_excel(...)` de Python con una librería
  Node equivalente (`exceljs`).
- Frontend: página con dos date pickers, botón "Consultar", tabla de resultados
  (TanStack Table), botón "Descargar Excel".
- Este reporte sirve como **plantilla**: un hook genérico (`useReportQuery`) y un
  componente genérico (`ReportTable` + `ReportPage`) reusables para los siguientes
  18 reportes, para no reescribir el mismo patrón cada vez.
- Entregable: Liquidación de Comisiones funcionando igual que en Streamlit,
  comparado dato a dato contra el actual.

## Fases 4 en adelante — Resto de los reportes, por lotes

Cada fase siguiente porta un lote chico (3-5 reportes) reusando el patrón de la
Fase 3, agrupados por área para mantener contexto acotado:

- **Fase 4**: resto de RRHH, lote 1 (Tickets por hora, Transferencias TEM-TRE,
  Llegadas Tardes y Justificaciones, Modificaciones de Horarios)
- **Fase 5**: resto de RRHH, lote 2 (Tickets por Comercial, Desglose de Recibos,
  Desglose de Recibos DAB)
- **Fase 6**: resto de RRHH, lote 3 (Reporte Martin, Reporte Actividad en Masa,
  Recepción de Proveedor)
- **Fase 7**: Supply Chain completo (Reposición Cruzada, Mínimos y Máximos, Lista
  artículos)
- **Fase 8**: Control cajas completo (las 4 consultas)
- **Fase 9**: Marketing — Generador de Códigos de Barras (distinto patrón, no es
  consulta a DB, se evalúa aparte cómo portarlo)

**Prompt sugerido para cada una**: "Arrancá la Fase N del plan: portar [lote de
reportes], usando el patrón de la Fase 3."

## Fase final — Despliegue al servidor real

**Prompt sugerido**: "Arrancá la Fase final del plan: deploy al servidor con pm2."

- Solo después de confirmar que todos los reportes migrados funcionan igual que en
  Streamlit.
- Clonar al servidor real (el mismo donde corren los demás proyectos con pm2), build
  de frontend y backend, proceso pm2 para el backend Nest, el frontend se sirve como
  estático (build) detrás de nginx o directo desde Nest.
- Reverse proxy + HTTPS siguiendo el mismo patrón que ya usan los otros proyectos del
  servidor.
- Dar de baja la app de Streamlit Cloud y el workflow de keep-alive
  (`.github/workflows/keep-alive.yml`) una vez confirmado el reemplazo.

---

## Notas para quien ejecute cada fase

- Cada fase asume que las anteriores ya están hechas y funcionando.
- Si en algún momento una query de un reporte no está 100% clara en el `.py`
  original, se valida igual que se hizo en Python: corriendo la query contra la
  base real antes de darla por buena (las credenciales están en
  `.streamlit/secrets.toml` de este repo).
- Mantener siempre el mismo criterio de columnas/orden/nombres que ya está validado
  en cada módulo Python — no "mejorar" ni reordenar nada sin que el usuario lo pida
  explícitamente, tal como pasó en este repo (varios reportes tuvieron ajustes finos
  de columnas pedidos a mano).
