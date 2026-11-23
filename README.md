# 🚀 Job Monitor Bot — IT & Data Careers (Los Lagos & Remote)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-CI%2FCD-2088FF?style=for-the-badge&logo=github-actions&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram_Bot_API-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)

Sistema automatizado de vigilancia y alerta temprana para ofertas laborales en tecnología (Soporte Técnico, Infraestructura, Redes, Análisis de Datos, BI y Ciberseguridad). El bot rastrea múltiples fuentes públicas y privadas, descarta duplicados y despacha reportes limpios a través de la API de Telegram.

---

## 📌 Arquitectura del Sistema

```text
       [ Cron Job (GitHub Actions) ]
                     │ (08:00 AM Lun-Vie)
                     ▼
          ┌─────────────────────┐
          │      config.json    │ ──► [ Parámetros de búsqueda y filtros ]
          └──────────┬──────────┘
                     │
          ┌──────────▼──────────┐
          │       main.py       │ ──► [ Orquestador Modular ]
          └──────────┬──────────┘
                     │
    ┌────────────────┼────────────────┬────────────────┬────────────────┐
    ▼                ▼                ▼                ▼                ▼
[ChileTrabajos]  [CompuTrabajo]   [Fiscalía CL]  [Empleos Públ.] [Get on Board]
 (Web Scraping)   (Web Scraping)   (Internal API) (Internal API)  (Public REST API)
    │                │                │                │                │
    └────────────────┴────────────────┼────────────────┴────────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │   Filtro & Sanitización   │
                        │ (Palabras clave + Región) │
                        └─────────────┬─────────────┘
                                      ▼
                        ┌───────────────────────────┐
                        │  historial_empleos.json   │ ──► [ Deduplicación ]
                        └─────────────┬─────────────┘
                                      ▼
                          [ Telegram Bot API ] ──► 📲 Notificación en Celular```


🛠️ Tecnologías y Librerías
Lenguaje: Python 3.11+

Consumo de APIs y Peticiones: requests

Web Scraping y Parseo HTML: beautifulsoup4

Gestión de Entorno Local: python-dotenv

Persistencia y Control de Estado: json (almacenamiento local versionado)

Sanitización de Datos: html.escape (compatibilidad estricta con formato HTML de Telegram)

Automatización y Serverless: GitHub Actions (Ubuntu runner, programado vía Cron)

Gestión de Secretos: GitHub Secrets (protección estricta de credenciales de API)

📁 Estructura del Proyecto
job-monitor/
├── .github/
│   └── workflows/
│       └── job_monitor.yml       # Definición del flujo CI/CD y Cron en GitHub Actions
├── config.json                   # Filtros de búsqueda, palabras clave y regiones
├── historial_empleos.json        # Base de datos local para control de duplicados
├── main.py                       # Orquestador central y despachador de Telegram
├── requirements.txt              # Dependencias de producción
├── scraper_chiletrabajos.py      # Módulo extractor ChileTrabajos
├── scraper_computrabajo.py       # Módulo extractor CompuTrabajo
├── scraper_empleospublicos.py    # Módulo extractor Empleos Públicos (Servicio Civil)
├── scraper_fiscalia.py           # Módulo extractor Fiscalía de Chile
└── scraper_getonboard.py         # Módulo extractor Get on Board

⚙️ Configuración y Despliegue
1. Variables de Entorno (GitHub Secrets)
Para ejecutar este proyecto en la nube sin exponer credenciales sensibles, se deben configurar los siguientes secretos en el repositorio (Settings > Secrets and variables > Actions):

TELEGRAM_TOKEN: Token de autenticación provisto por @BotFather.

CHAT_ID: Identificador numérico de tu chat o canal receptor.

2. Personalización (config.json)
Puedes adaptar los términos de búsqueda y regiones sin tocar el código fuente modificando config.json:

{
  "filtros": {
    "palabras_busqueda": ["soporte", "informatica", "datos"],
    "palabras_titulo": [
      "ingeniería", "informática", "técnico", "analista", "datos"
    ]
  },
  "ubicaciones": {
    "region_chiletrabajos": "10",
    "slug_computrabajo": "los-lagos"
  }
}

# 1. Clonar el repositorio
git clone [https://github.com/mandarina125/job-monitor.git](https://github.com/mandarina125/job-monitor.git)
cd job-monitor

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear archivo .env en la raíz con tus credenciales
# TELEGRAM_TOKEN=tu_token_aqui
# CHAT_ID=tu_chat_id_aqui

# 4. Ejecutar el orquestador
python main.py

🔒 Permisos del Flujo CI/CD
El workflow de GitHub Actions requiere permisos de escritura en el repositorio (Settings > Actions > General > Workflow permissions > Read and write permissions) para comitear de vuelta las actualizaciones en historial_empleos.json y garantizar que el estado persista entre ejecucione

