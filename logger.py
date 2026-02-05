import requests
import json

def upload_data(GAS_URL, v1, v2, v3, v4):
	payload = { "value1": v1, "value2": v2, "value3": v3, "value4": v4 }
	#payload = { "value1": v1, "value2": v2 }
	try:
		response = requests.post(
			GAS_URL, 
			data=json.dumps(payload),
			headers={'Content-Type': 'application/json'}
		)
		if response.status_code == 200:
			print(f"Send to Google Sheet success! return: {response.text}")
		else:
			print(f"Fail! Status code: {response.status_code}")
	except Exception as e:
		printf(f"Error: {e}")
