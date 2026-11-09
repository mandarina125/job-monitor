import requests

BASE_API_URL = "https://www.getonbrd.com/api/v0/categories"

# Categorías oficiales verificadas en la API de Get on Board
CATEGORIAS = [
    "data-science-analytics",
    "sysadmin-devops-qa",
    "cybersecurity"
]

# Roles afines a soporte, análisis de datos, BI y TI inicial/intermedio
PALABRAS_CLAVE = [
    "data", "datos", "analista", "analytics", "bi", "sql", "power bi",
    "soporte", "support", "helpdesk", "ti", "it", "seguridad", 
    "junior", "trainee", "infraestructura"
]

# Exclusiones para roles directivos o de alta jerarquía
EXCLUSIONES = [
    "lead", "head", "manager", "architect", "arquitecto", "principal", "director"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

def extraer_getonboard():
    print("Iniciando revisión en Get on Board (Remoto / TI)...")
    ofertas_encontradas = []

    for cat in CATEGORIAS:
        url = f"{BASE_API_URL}/{cat}/jobs"
        try:
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                print(f"Aviso: Get on Board respondió {response.status_code} para '{cat}'.")
                continue

            datos = response.json()
            lista_jobs = datos.get("data", [])

            for item in lista_jobs:
                attributes = item.get("attributes", {})
                titulo = attributes.get("title", "")
                slug = attributes.get("slug", "")
                modalidad = attributes.get("remote_modality", "")
                
                enlace = f"https://www.getonbrd.com/jobs/{slug}" if slug else ""
                es_remoto = attributes.get("remote", False) or modalidad in ["fully_remote", "remote_local"]

                titulo_lower = titulo.lower()

                # Debe contener al menos una palabra clave afín y ninguna de exclusión
                cumple_perfil = any(k in titulo_lower for k in PALABRAS_CLAVE)
                no_es_gerencial = not any(e in titulo_lower for e in EXCLUSIONES)

                if es_remoto and cumple_perfil and no_es_gerencial and enlace:
                    if not any(o["url"] == enlace for o in ofertas_encontradas):
                        empresa = attributes.get("company", {}).get("data", {}).get("attributes", {}).get("name", "Empresa TI")
                        ofertas_encontradas.append({
                            "titulo": f"{titulo} ({empresa} - Remoto)",
                            "url": enlace,
                            "origen": "Get on Board"
                        })
                        
        except Exception as e:
            print(f"Error consultando '{cat}' en Get on Board: {e}")

    return ofertas_encontradas

if __name__ == "__main__":
    ofertas = extraer_getonboard()
    print(f"\n--- Ofertas filtradas para perfil TI ({len(ofertas)}) ---")
    for o in ofertas[:10]:  # Muestra las primeras 10 para probar
        print(f"📌 {o['titulo']}")
        print(f"🔗 {o['url']}\n")