import os
import json
import requests
from bs4 import BeautifulSoup

# Configuración de Telegram (usaremos variables de entorno en GitHub Actions por seguridad)
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "9004414867:AAEEa_L1RJfX3cJ6FeZ4XCS9_MTgEuH_xXU")
CHAT_ID = os.environ.get("CHAT_ID", "9221580402")

# Palabras clave definidas por ti
KEYWORDS = [
    "ingeniería", "informática", "técnico en informática", 
    "analista de soporte técnico", "analista de bases de datos", 
    "analista de datos", "análisis de datos", "soporte tier ii", "soporte"
]

# Ubicaciones de interés
LOCATIONS = ["puerto montt", "puerto varas", "los lagos", "remoto"]

# Archivo de historial para comparar con el día anterior
HISTORY_FILE = "historial_empleos.json"

def cargar_historial():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def guardar_historial(historial):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(historial), f, ensure_ascii=False, indent=4)

def enviar_alerta_telegram(mensaje):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def buscar_empleos():
    print("Iniciando búsqueda de empleos...")
    historial = cargar_historial()
    nuevos_empleos = []

    # Aquí iremos añadiendo la lógica de scraping para cada una de las 6 páginas:
    # 1. ChileTrabajos
    # 2. Empleos Públicos
    # 3. Fiscalía
    # 4. BNE
    # 5. Computrabajo
    # 6. Get on Board

    # Ejemplo simulado de estructura de una oferta encontrada:
    # oferta = {"id": "chiletrabajos-12345", "titulo": "Analista de Soporte IT", "url": "https://..."}
    
    # if oferta["id"] not in historial:
    #     nuevos_empleos.append(oferta)
    #     historial.add(oferta["id"])

    # Enviar notificación si hay novedades
    if nuevos_empleos:
        mensaje = "🚨 *¡Nuevas ofertas de empleo encontradas!* 🚨\n\n"
        for emp in nuevos_empleos:
            mensaje += f"• *{emp['titulo']}*\n[Ver oferta]({emp['url']})\n\n"
        
        enviar_alerta_telegram(mensaje)
        guardar_historial(historial)
        print("¡Alertas enviadas con éxito!")
    else:
        print("No hay ofertas nuevas hoy.")

if __name__ == "__main__":
    buscar_empleos()