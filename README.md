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


