import os
from dotenv import load_dotenv
import json
import html
import requests

# Cargar variables locales desde el archivo .env
load_dotenv()

# 1. Importación modular de los extractores
from scraper_chiletrabajos import extraer_ofertas as extraer_chiletrabajos
from scraper_computrabajo import extraer_computrabajo
from scraper_fiscalia import extraer_fiscalia
from scraper_empleospublicos import extraer_empleos_publicos
from scraper_getonboard import extraer_getonboard

# Leer variables usando el NOMBRE de la variable de entorno
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CONFIG_FILE = "config.json"

def cargar_configuracion():
    """Carga los parámetros de búsqueda o aplica valores por defecto si no existe."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "filtros": {
            "palabras_busqueda": ["soporte", "informatica", "datos"],
            "palabras_titulo": ["soporte", "informatica", "tecnico", "analista"]
        },
        "ubicaciones": {
            "region_chiletrabajos": "10",
            "slug_computrabajo": "los-lagos"
        }
    }

# Archivo de persistencia histórica
HISTORY_FILE = "historial_empleos.json"

def cargar_historial():
    """Carga los enlaces de ofertas ya notificadas para evitar duplicados."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception as e:
            print(f"Aviso al leer historial: {e}. Se iniciará con memoria limpia.")
    return set()

def guardar_historial(historial):
    """Guarda el historial actualizado en el archivo JSON."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(historial), f, ensure_ascii=False, indent=4)

def enviar_alerta_telegram(mensaje):
    """Envía el reporte consolidado a Telegram usando formato HTML."""
    # Validar que los tokens existan primero
    if not TELEGRAM_TOKEN or not CHAT_ID:
        print("Error: TELEGRAM_TOKEN o CHAT_ID no están configurados en el entorno.")
        return False
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN.strip()}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID.strip(),
        "text": mensaje,
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }
    
    try:
        res = requests.post(url, json=payload, timeout=12)
        if res.status_code == 200:
            return True
        else:
            print(f"Error de Telegram ({res.status_code}): {res.text}")
            return False
    except Exception as e:
        print(f"Error de red con Telegram: {e}")
        return False

def ejecutar_rastreo_diario():
    print("=" * 55)
    print("🚀 INICIANDO RASTREO CONSOLIDADO DE EMPLEOS TI")
    print("=" * 55 + "\n")
    
    config = cargar_configuracion()
    palabras_busqueda = config["filtros"]["palabras_busqueda"]
    palabras_titulo = config["filtros"]["palabras_titulo"]
    region_ct = config["ubicaciones"]["region_chiletrabajos"]
    region_comp = config["ubicaciones"]["slug_computrabajo"]

    historial = cargar_historial()
    todas_las_ofertas = []

    # 1. ChileTrabajos
    try:
        ofertas_ct = extraer_chiletrabajos(
            palabras_busqueda=palabras_busqueda,
            palabras_filtro=palabras_titulo,
            region=region_ct
        )
        todas_las_ofertas.extend(ofertas_ct)
    except Exception as e:
        print(f"❌ Error en ChileTrabajos: {e}")

    # 2. CompuTrabajo
    try:
        ofertas_comp = extraer_computrabajo(
            palabras_busqueda=palabras_busqueda,
            palabras_filtro=palabras_titulo,
            slug_region=region_comp
        )
        todas_las_ofertas.extend(ofertas_comp)
    except Exception as e:
        print(f"❌ Error en CompuTrabajo: {e}")

    # Portales 3, 4 y 5 continúan normalmente...
    # [Fiscalía, Empleos Públicos y Get on Board]

    # Portal 4: Empleos Públicos
    try:
        ofertas_ep = extraer_empleos_publicos()
        todas_las_ofertas.extend(ofertas_ep)
    except Exception as e:
        print(f"❌ Error en Empleos Públicos: {e}")

    # 5. Ejecutar Get on Board
    try:
        ofertas_gob = extraer_getonboard()
        todas_las_ofertas.extend(ofertas_gob)
    except Exception as e:
        print(f"❌ Error en Get on Board: {e}")

    # Filtrar solo ofertas que no se hayan visto antes
    nuevas = [o for o in todas_las_ofertas if o["url"] not in historial]

    print("\n" + "-" * 55)
    print(f"📊 RESUMEN DE RASTREO:")
    print(f"• Total ofertas capturadas hoy: {len(todas_las_ofertas)}")
    print(f"• Novedades reales no notificadas: {len(nuevas)}")
    print("-" * 55 + "\n")

    if nuevas:
        mensaje = "💼 <b>Nuevas vacantes de TI detectadas</b> 🔔\n\n"
        for o in nuevas:
            # Blindamos absolutamente todos los campos contra cualquier etiqueta mal formada
            titulo_limpio = html.escape(o.get('titulo', 'Sin título'))
            origen_limpio = html.escape(o.get('origen', 'Web'))
            url_limpia = html.escape(o.get('url', '#'), quote=True)
            
            # Usamos estructura limpia sin mezclar etiquetas crudas
            mensaje += f"• [{origen_limpio}] <b>{titulo_limpio}</b>\n"
            mensaje += f"🔗 <a href='{url_limpia}'>Ver oferta</a>\n\n"
            historial.add(o["url"])

        # Control del límite de 4096 caracteres por mensaje en Telegram
        exito = True
        if len(mensaje) > 4000:
            partes = [mensaje[i:i+4000] for i in range(0, len(mensaje), 4000)]
            for p in partes:
                if not enviar_alerta_telegram(p):
                    exito = False
        else:
            exito = enviar_alerta_telegram(mensaje)

        if exito:
            guardar_historial(historial)
            print("✅ Notificación enviada con éxito a Telegram y memoria actualizada.")
        else:
            print("⚠️ No se pudo enviar el mensaje a Telegram; el historial no fue modificado.")
    else:
        print("☕ Todo al día: no hay convocatorias nuevas en ninguno de los 4 portales.")

if __name__ == "__main__":
    ejecutar_rastreo_diario()