import subprocess
import cv2
import numpy as np


def ssocr_7seg(cv2_img, decimal=True):
	success, encoded_image = cv2.imencode('.png', cv2_img)
	if not success:
		return "Error: failed to encode image"
	
	byte_data = encoded_image.tobytes()
	
	if decimal:
		cli_command = ["ssocr", "-d", "-1", "invert", "-"]
	else:
		cli_command = ["ssocr", "-d", "-1", "omit_decimal", "invert", "-"]
	
	try:
		process = subprocess.Popen(
			cli_command,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
		)
		stdout_data, stderr_data = process.communicate(input=byte_data)
		if process.returncode != 0:
			return f"SSOCR Error: {stderr_data.decode().strip()}"
		return stdout_data.decode().strip()
	except subprocess.CalledProcessError as e:
		return f"Error: {e.output.decode()}"

def preprocess(image):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
	contrast_enhanced = clahe.apply(gray)
	blurred = cv2.GaussianBlur(contrast_enhanced, (5, 5), 0)
	_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	kernel = np.ones((3, 3), np.uint8)
	fixed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
	return fixed

