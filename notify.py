import requests
from datetime import datetime

def send_telegram_msg(token, chat_id, message):
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

if __name__ == "__main__":
	try:
		with open("token.txt", "r") as f:
			token = f.readline().rstrip()
			chat_id = f.readline().rstrip()
		now = datetime.now()
		timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
		msg = f"\nSay Hello from Raspberry Pi ({timestamp})"
		send_telegram_msg(token, chat_id, msg)
	except FileNotFoundError:
		print("Missing token.txt")
	
