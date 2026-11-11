import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://cl.computrabajo.com"
HISTORY_FILE = "historial_empleos_compu.json"

BASE_URL_COMPUTRABAJO = "https://cl.computrabajo.com"

# Búsqueda en Región de Los Lagos
URL_BUSQUEDA = f"{BASE_URL_COMPUTRABAJO}/empleos-en-los-lagos?q="

PALABRAS_BUSQUEDA = ["soporte", "informatica", "datos"]

FILTRO_TITULOS = [
    "ingeniería", "ingenieria", "informática", "informatica", 
    "técnico", "tecnico", "soporte", "analista", "tier", "base de datos", "datos", "soporte remoto"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "es-419,es;q=0.9"
}

def extraer_computrabajo(palabras_busqueda=None, palabras_filtro=None, slug_region="los-lagos"):
    print("Iniciando revisión en CompuTrabajo...")
    ofertas_encontradas = []

    palabras = palabras_busqueda or ["soporte", "informatica", "datos"]
    filtros = palabras_filtro or ["soporte", "informatica", "tecnico", "analista"]
    url_base_busqueda = f"{BASE_URL_COMPUTRABAJO}/empleos-en-{slug_region}?q="

    for palabra in palabras:
        url = f"{url_base_busqueda}{palabra}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            articulos = soup.find_all("article", class_="box_offer")

            for art in articulos:
                tag_a = art.find("a", class_="js-o-link")
                if not tag_a:
                    continue

                titulo = tag_a.get_text(strip=True)
                enlace = urljoin(BASE_URL_COMPUTRABAJO, tag_a.get("href", ""))

                empresa_tag = art.find("p", class_="fs16")
                empresa = empresa_tag.get_text(strip=True) if empresa_tag else "Confidencial"

                titulo_lower = titulo.lower()
                if any(k in titulo_lower for k in filtros):
                    if not any(o["url"] == enlace for o in ofertas_encontradas):
                        ofertas_encontradas.append({
                            "titulo": titulo,
                            "url": enlace,
                            "origen": "CompuTrabajo",
                            "empresa": empresa
                        })
        except Exception as e:
            print(f"Error consultando '{palabra}' en CompuTrabajo: {e}")

    return ofertas_encontradas