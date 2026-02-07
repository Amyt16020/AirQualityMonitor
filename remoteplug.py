import asyncio
from tapo import ApiClient
import json
import os
import time


async def p105_on(dev_info:dict):
	username = dev_info["username"]
	password = dev_info["password"]
	ip_address = dev_info["ip address"]
	client = ApiClient(username, password)
	device = await client.p105(ip_address)
	print("Turning P105 on...")
	await device.on()


async def p105_off(dev_info:dict):
	client = ApiClient(dev_info["username"], dev_info["password"])
	device = await client.p105(dev_info["ip address"])
	print("Turning P105 off...")
	await device.off()


def test(info_file:str):
	if os.path.exists(info_file):
		with open(info_file, "r") as f:
			dev_info = json.load(f)
		asyncio.run(p105_on(dev_info))
		time.sleep(3)
		asyncio.run(p105_off(dev_info))
	else:
		print(f"Device info file not found.")
