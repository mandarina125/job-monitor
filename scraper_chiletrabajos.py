import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.chiletrabajos.cl"
PALABRAS_BUSQUEDA = ["soporte", "informatica", "datos"]
FILTRO_TITULOS = [
    "ingeniería", "ingenieria", "informática", "informatica", 
    "técnico", "tecnico", "soporte", "analista", "tier", "base de datos", "datos"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
}

def extraer_ofertas():
    print("Iniciando revisión en ChileTrabajos (Los Lagos)...")
    ofertas_encontradas = []

    for palabra in PALABRAS_BUSQUEDA:
        url = f"{BASE_URL}/encuentra-un-empleo?carrera=&region=10&palabras-claves={palabra}"
        try:
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200:
                continue

            soup = BeautifulSoup(res.text, "html.parser")
            items = soup.find_all("div", class_="job-item")

            for item in items:
                tag_a = item.find("h2")
                link_elem = tag_a.find("a") if tag_a else item.find("a")

                if not link_elem:
                    continue

                titulo = link_elem.get_text(strip=True)
                enlace = urljoin(BASE_URL, link_elem.get("href", ""))

                titulo_lower = titulo.lower()
                if any(k in titulo_lower for k in FILTRO_TITULOS):
                    if not any(o["url"] == enlace for o in ofertas_encontradas):
                        ofertas_encontradas.append({
                            "titulo": titulo,
                            "url": enlace,
                            "origen": "ChileTrabajos"
                        })
        except Exception as e:
            print(f"Error consultando '{palabra}' en ChileTrabajos: {e}")

    return ofertas_encontradas

if __name__ == "__main__":
    # Prueba individual si ejecutas solo este archivo
    resultados = extraer_ofertas()
    print(f"Total encontradas en ChileTrabajos: {len(resultados)}")