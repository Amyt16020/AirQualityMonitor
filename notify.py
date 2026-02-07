import requests
from datetime import datetime

def send_telegram_msg(info:dict, message):
	token = info["token"]
	chat_id = info["chat_id"]
	url = f"https://api.telegram.org/bot{token}/sendMessage"
	payload = {
		"chat_id": chat_id,
		"text": message
	}
	try:
		response = requests.post(url, data=payload)
		if response.status_code == 200:
			print("Send Telegram message successfully.")
		else:
			print(f"Failed! Status Code: {response.status_code}")
	except Exception as e:
		print(f"Network Error: {e}")
	
