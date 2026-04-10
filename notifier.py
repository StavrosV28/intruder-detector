import requests
import os
from dotenv import load_dotenv

load_dotenv()

BOT_API_TOKEN = os.getenv("BOT_API_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

def send_alert(notif):
    url = f"https://api.telegram.org/bot{BOT_API_TOKEN}/sendMessage"
    
    data = {"chat_id": CHAT_ID, "text": notif}
    
    response = requests.post(url, json=data)

    
    
