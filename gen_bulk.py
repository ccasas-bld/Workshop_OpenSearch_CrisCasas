import json
import random
from datetime import datetime, timedelta, timezone

# -------- Config --------
OUT_FILE = "bulk_eventos_lab.ndjson"
INDEX_NAME = "eventos_lab"
N = 500  # cantidad de documentos a generar

ubicaciones = ["Bogotá", "Medellín", "Cali", "Barranquilla", "Bucaramanga"]
tipos_evento = ["login", "logout", "error_app", "fraude", "download", "api_call"]
mensajes = {
    "login": ["Login OK usuario", "Login fallido usuario", "MFA requerido usuario"],
    "logout": ["Logout OK usuario", "Sesión expirada usuario"],
    "error_app": ["Timeout servicio", "NullReference en módulo", "DB connection error"],
    "fraude": ["Acceso sospechoso", "Intento fuerza bruta", "Token inválido repetido"],
    "download": ["Descarga completada", "Descarga bloqueada por policy", "Archivo no encontrado"],
    "api_call": ["API 200 OK", "API 429 rate limit", "API 500 internal error"],
}

usuarios = [f"user_{i:03d}" for i in range(1, 101)]
ips = [f"192.168.1.{i}" for i in range(2, 255)]

# Base de tiempo: últimos 7 días
now = datetime.now(timezone(timedelta(hours=-5)))  # Colombia -05:00
start = now - timedelta(days=7)

def iso(dt: datetime) -> str:
    # ISO-8601 con offset (lo que mejor entiende OpenSearch en date)
    return dt.isoformat(timespec="seconds")

with open(OUT_FILE, "w", encoding="utf-8") as f:
    for _ in range(N):
        tipo = random.choice(tipos_evento)
        ubic = random.choice(ubicaciones)
        user = random.choice(usuarios)
        ip = random.choice(ips)

        # timestamp aleatorio en últimos 7 días
        dt = start + timedelta(seconds=random.randint(0, 7 * 24 * 3600))

        # severidad coherente por tipo
        if tipo in ("login", "logout"):
            sev = random.randint(1, 3)
        elif tipo in ("download", "api_call"):
            sev = random.randint(2, 4)
        elif tipo == "error_app":
            sev = random.randint(3, 5)
        else:  # fraude
            sev = random.randint(4, 5)

        msg = random.choice(mensajes[tipo]) + f" {user}"

        doc = {
            "@timestamp": iso(dt),
            "ubicacion": ubic,
            "tipo_evento": tipo,
            "severidad": sev,
            "mensaje": msg,
            "usuario": user,
            "ip": ip
        }

        # Línea acción + línea doc (NDJSON)
        f.write(json.dumps({"index": {"_index": INDEX_NAME}}) + "\n")
        f.write(json.dumps(doc, ensure_ascii=False) + "\n")

print(f"Generado: {OUT_FILE} con {N} documentos para índice '{INDEX_NAME}'.")
