import json
import requests

URL_FISCALIA = "https://fiscaliadechile.trabajando.cl/offers/ajax_search"

# Filtros estrictos para tecnología e informática
FILTRO_TITULOS = [
    "informática", "informatica", "soporte", "redes", "sistemas",
    "analista", "datos", "infraestructura", "tecnología", "tecnologia",
    "técnico en informática", "tecnico en informatica", "desarrollador"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://fiscaliadechile.trabajando.cl/"
}

# 237 corresponde a la Región de Los Lagos en Fiscalía
payload = {
    "filters": json.dumps({"fiscaliaRegional": "237"})
}

def extraer_fiscalia():
    print("Iniciando revisión en Fiscalía de Chile (Los Lagos)...")
    ofertas_encontradas = []

    try:
        response = requests.post(URL_FISCALIA, data=payload, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"Error {response.status_code} al consultar Fiscalía.")
            return []

        datos = response.json()
        items = datos if isinstance(datos, list) else datos.get("offers", [])

        for item in items:
            # Validamos que no esté oculta y sea de la región de Los Lagos (237)
            region = str(item.get("fiscaliaRegional", ""))
            hidden = item.get("hidden", 0)
            
            if hidden == 1 or (region and region != "237"):
                continue

            titulo = item.get("jobTitle") or item.get("cargo") or ""
            oferta_id = item.get("id")
            
            enlace = f"https://fiscaliadechile.trabajando.cl/ofertas/{oferta_id}" if oferta_id else "https://fiscaliadechile.trabajando.cl/#offerList"

            titulo_lower = titulo.lower()
            if any(k in titulo_lower for k in FILTRO_TITULOS):
                ofertas_encontradas.append({
                    "titulo": titulo,
                    "url": enlace,
                    "origen": "Fiscalía Los Lagos"
                })

    except Exception as e:
        print(f"Error al procesar Fiscalía: {e}")

    return ofertas_encontradas

if __name__ == "__main__":
    ofertas = extraer_fiscalia()
    print(f"Total ofertas TI encontradas en Fiscalía: {len(ofertas)}")
    for o in ofertas:
        print(f"📌 {o['titulo']}")
        print(f"🔗 {o['url']}\n")