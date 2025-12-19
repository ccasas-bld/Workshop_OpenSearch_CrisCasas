# OpenSearch Lab (Local) — Docker Compose + Dashboard + Faceted Search (Controls)

Este repositorio/documento contiene los pasos mínimos para levantar **OpenSearch** en local, cargar datos (sample + manual), y visualizar la información en **OpenSearch Dashboards** con **búsqueda facetada** usando **Controls**.

---

## 0) Requisitos

- Docker Engine instalado
- Docker Compose v2 (`docker compose`)
- Puertos libres:
  - `9200` (OpenSearch API)
  - `5601` (OpenSearch Dashboards)

---

## 1) Preparación del sistema (Linux)

OpenSearch requiere un valor mínimo de `vm.max_map_count`:

```bash
sudo sysctl -w vm.max_map_count=262144
```

```bash
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
sudo sysctl -p
```

## 2) Levantar OpenSearch con Docker Compose

Crear carpeta de trabajo:

```bash
mkdir -p ~/opensearch-lab
cd ~/opensearch-lab
```

Descargar docker-compose.yml recomendado:

```bash
curl -O https://raw.githubusercontent.com/opensearch-project/documentation-website/2.14/assets/examples/docker-compose.yml
```

!Nota: puede aparecer el warning version is obsolete en Compose v2. No bloquea ejecución.

Crear archivo .env con la contraseña inicial del admin:

```bash
echo "OPENSEARCH_INITIAL_ADMIN_PASSWORD=<TU_PASSWORD_FUERTE_AQUI>" > .env
```
Levantar contenedores:

```bash
docker compose up -d
docker compose ps
```
Ver logs:

```bash
docker compose logs -f opensearch-node1
docker compose logs -f opensearch-dashboards
```
#3) Verificación de servicios

Verificar OpenSearch API (HTTPS):

```bash
curl -k -u admin:<TU_PASSWORD_FUERTE_AQUI> https://localhost:9200
```
Abrir OpenSearch Dashboards (UI):

URL: http://localhost:5601
Usuario: admin
Password: el definido en .env

## 4) Cargar datasets
### 4.1 Dataset de ejemplo (Sample data)

En OpenSearch Dashboards:

Home → Add sample data

Cargar “Sample web logs”

Validar en Discover

### 4.2 Dataset manual (requisito 2.c) — índice eventos_lab

En Dashboards → Management → Dev Tools.

Crear índice con mapping (sin * en el nombre del índice):

```http
PUT eventos_lab
{
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "ubicacion":  { "type": "keyword" },
      "tipo_evento":{ "type": "keyword" },
      "severidad":  { "type": "integer" },
      "mensaje":    { "type": "text" },
      "usuario":    { "type": "keyword" },
      "ip":         { "type": "ip" }
    }
  }
}
```

Si aparece resource_already_exists_exception, el índice ya existe: no recrear. Continuar con la carga de datos.

Cargar documentos con _bulk:

```http
POST _bulk
{ "index": { "_index": "eventos_lab" } }
{ "@timestamp":"2025-12-19T08:00:00-05:00", "ubicacion":"Bogotá", "tipo_evento":"login", "severidad":2, "mensaje":"Login OK usuario A", "usuario":"user_001", "ip":"192.168.1.10" }
{ "index": { "_index": "eventos_lab" } }
{ "@timestamp":"2025-12-19T08:10:00-05:00", "ubicacion":"Bogotá", "tipo_evento":"error_app", "severidad":4, "mensaje":"Timeout servicio X", "usuario":"user_002", "ip":"192.168.1.11" }
{ "index": { "_index": "eventos_lab" } }
{ "@timestamp":"2025-12-19T09:00:00-05:00", "ubicacion":"Medellín", "tipo_evento":"login", "severidad":1, "mensaje":"Login OK usuario B", "usuario":"user_003", "ip":"192.168.1.12" }
{ "index": { "_index": "eventos_lab" } }
{ "@timestamp":"2025-12-19T09:20:00-05:00", "ubicacion":"Cali", "tipo_evento":"fraude", "severidad":5, "mensaje":"Acceso sospechoso", "usuario":"user_004", "ip":"192.168.1.13" }
```
Validar conteo:

```http
GET eventos_lab/_count
```
Validar documentos:

```http
GET eventos_lab/_search
{
  "size": 10,
  "sort": [{ "@timestamp": "desc" }]
}

```

5) Crear Data View / Index Pattern (eventos_lab*)

Crear un patrón para explorar el índice en Discover y para usarlo en visualizaciones:

Pattern: eventos_lab*

Time field: @timestamp

Según versión, esta opción puede aparecer como Index Patterns o permitir crearlo directamente desde Discover.


6) Visualizaciones + Dashboard (mínimo 3)

Usar el Data View eventos_lab* para crear visualizaciones.

6.1 Barras — Ubicación vs Severidad (apilado o agrupado)

Configuración recomendada:

Tipo: Bar

Y (métrica): Count

X (bucket): Terms(ubicacion)

Split series: Terms(severidad)

Modo: Stacked o Grouped

Qué representa: cantidad de eventos por ciudad y su distribución por severidad (1–5).

6.2 Línea — Eventos en el tiempo por ubicación

Configuración recomendada:

Tipo: Line

Y: Count

X: Date histogram(@timestamp)

Split series: Terms(ubicacion)

Qué representa: tendencia/picos de volumen de eventos a lo largo del tiempo, separado por ubicación.

6.3 Torta/Donut — Distribución por tipo_evento

Configuración recomendada:

Tipo: Pie o Donut

Métrica: Count

Slices: Terms(tipo_evento) (Size 5–10)

Qué representa: proporción de eventos por tipo (login, api_call, error_app, fraude, etc.).

6.4 (Opcional) KPIs — Total eventos y severidad promedio

Configuración recomendada (visualización tipo “Metric”):

Metric 1: Count

Metric 2: Average(severidad)

Qué representa: volumen total y severidad promedio bajo filtros y rango temporal actuales.

6.5 Crear Dashboard

Pasos:

Dashboard → Create / Edit

Add panels → agregar las 3 visualizaciones (y KPIs si aplica)

Save dashboard

Si no aparecen datos en Discover/visualizaciones, revisar el Time picker (rango temporal) y que el Data View sea el correcto.

7) Faceted Search (Controls)

La búsqueda facetada se implementa como filtros dinámicos en UI usando Controls.

Crear Controls en el dashboard (Dashboard → Edit → Controls):

Options list: ubicacion (multi-select)

Options list: tipo_evento (multi-select)

Range slider: severidad (1–5)

Usar también el Time picker como faceta temporal

Aplicar filtros con Apply changes.

Probar búsquedas combinando facetas (ejemplos):

Caso 1:

ubicacion = Bogotá

tipo_evento = api_call

severidad = 2–4

Caso 2:

ubicacion = Barranquilla, Cali

tipo_evento = fraude

severidad = 4–5

Caso 3:

Cambiar time picker: Last 7 days → Last 24 hours

Mantener filtros activos

Resultado esperado: todas las visualizaciones y métricas cambian según la combinación de filtros.

8) Inconvenientes comunes y soluciones

Warning version is obsolete:

Causa: Compose v2 ignora version:

Impacto: no bloquea

Solución: opcionalmente eliminar version: del YAML

Error permission denied en docker.sock:

Solución (recomendado): agregar usuario al grupo docker


```bash
sudo usermod -aG docker $USER
newgrp docker
```

