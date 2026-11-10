import os
import json
import html
import requests

# 1. Importación modular de los 4 extractores
from scraper_chiletrabajos import extraer_ofertas as extraer_chiletrabajos
from scraper_computrabajo import extraer_computrabajo
from scraper_fiscalia import extraer_fiscalia
from scraper_empleospublicos import extraer_empleos_publicos
from scraper_getonboard import extraer_getonboard

# Leer directamente de las variables de entorno sin dejar textos planos
TELEGRAM_TOKEN = os.getenv("9004414867:AAEEa_L1RJfX3cJ6FeZ4XCS9_MTgEuH_xXU")
CHAT_ID = os.getenv("9221580402")

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
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
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
    
    historial = cargar_historial()
    todas_las_ofertas = []

    # Portal 1: ChileTrabajos
    try:
        ofertas_ct = extraer_chiletrabajos()
        for o in ofertas_ct:
            o["origen"] = "ChileTrabajos"
        todas_las_ofertas.extend(ofertas_ct)
    except Exception as e:
        print(f"❌ Error en ChileTrabajos: {e}")

    # Portal 2: CompuTrabajo
    try:
        ofertas_comp = extraer_computrabajo()
        todas_las_ofertas.extend(ofertas_comp)
    except Exception as e:
        print(f"❌ Error en CompuTrabajo: {e}")

    # Portal 3: Fiscalía de Chile
    try:
        ofertas_fisc = extraer_fiscalia()
        todas_las_ofertas.extend(ofertas_fisc)
    except Exception as e:
        print(f"❌ Error en Fiscalía: {e}")

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
            titulo_limpio = html.escape(o.get('titulo', 'Sin título'))
            origen = o.get('origen', 'Web')
            mensaje += f"• [{origen}] <b>{titulo_limpio}</b>\n"
            mensaje += f"🔗 <a href='{o['url']}'>Ver oferta</a>\n\n"
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