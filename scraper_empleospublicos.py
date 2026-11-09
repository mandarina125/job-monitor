import requests

URL_API = "https://www.empleospublicos.cl/apiConvocatorias.ashx"
BASE_URL = "https://www.empleospublicos.cl"

FILTRO_TITULOS = [
    "informática", "informatica", "soporte", "redes", "sistemas",
    "analista", "datos", "infraestructura", "tecnología", "tecnologia",
    "computación", "computacion", "ti", "programador", "desarrollador"
]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.empleospublicos.cl/"
}

def extraer_empleos_publicos():
    print("Iniciando revisión en Empleos Públicos (Los Lagos)...")
    ofertas_encontradas = []

    # Parámetros validados: action=search y region=10 (Los Lagos)
    params = {
        "action": "search",
        "region": "10"
    }

    try:
        response = requests.get(URL_API, params=params, headers=headers, timeout=12)
        if response.status_code != 200:
            print(f"Error {response.status_code} al consultar Empleos Públicos.")
            return []

        resultado = response.json()
        lista_ofertas = resultado.get("data", [])
        total = resultado.get("total", 0)

        print(f"Total convocatorias activas en Los Lagos: {total}")

        for item in lista_ofertas:
            # Los campos estándar de Empleos Públicos suelen ser 'cargo' o 'nombre' o 'titulo'
            titulo = item.get("cargo") or item.get("nombre") or item.get("titulo") or ""
            institucion = item.get("institucion") or item.get("ministerio") or "Sector Público"
            
            # Identificador de la convocatoria para el enlace directo
            codigo = item.get("codConvocatoria") or item.get("id") or item.get("codigo") or ""
            
            if codigo:
                enlace = f"https://www.empleospublicos.cl/pub/convocatorias/convpostularavisoTrabajo.aspx?i={codigo}&c=0&j=0&tipo=aviso"
            else:
                enlace = "https://www.empleospublicos.cl"

            titulo_lower = titulo.lower()
            if any(k in titulo_lower for k in FILTRO_TITULOS):
                ofertas_encontradas.append({
                    "titulo": f"{titulo} ({institucion})",
                    "url": enlace,
                    "origen": "Empleos Públicos"
                })

    except Exception as e:
        print(f"Error al procesar Empleos Públicos: {e}")

    return ofertas_encontradas

if __name__ == "__main__":
    ofertas = extraer_empleos_publicos()
    print(f"\nTotal convocatorias TI encontradas: {len(ofertas)}")
    for o in ofertas:
        print(f"📌 {o['titulo']}")
        print(f"🔗 {o['url']}\n")