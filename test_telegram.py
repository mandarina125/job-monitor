import requests

# Reemplaza 'TU_TOKEN_AQUI' con el token que te dio BotFather
TOKEN = "9004414867:AAEEa_L1RJfX3cJ6FeZ4XCS9_MTgEuH_xXU"
CHAT_ID = "9221580402"

url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
payload = {
    "chat_id": CHAT_ID,
    "text": "🤖 ¡Hola! Tu bot de búsqueda de empleo ya está conectado y listo para avisarte.",
}

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("¡Mensaje enviado con éxito! Revisa tu Telegram.")
else:
    print("Error al enviar el mensaje:", response.text)