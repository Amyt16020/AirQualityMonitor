import subprocess
import pytesseract
import cv2
import numpy as np


def ssocr_7seg(cv2_img, num_of_digits=-1):
	success, encoded_image = cv2.imencode('.png', cv2_img)
	if not success:
		return "Error: failed to encode image"
	
	byte_data = encoded_image.tobytes()
	
	cli_command = ["ssocr", "-d", f"{num_of_digits}", "invert", "-"]
	
	try:
		process = subprocess.Popen(
			cli_command,
			stdin = subprocess.PIPE,
			stdout = subprocess.PIPE,
			stderr = subprocess.PIPE
		)
		stdout_data, stderr_data = process.communicate(input=byte_data)
		if process.returncode == 0:
			return True, stdout_data.decode().strip()
#		elif process.returncode == 1:
#			print(f"SSOCR Error({process.returncode}): {stderr_data.decode().strip()}")
#			return stdout_data.decode().strip()
		else:
			return False, f"SSOCR Error({process.returncode}): {stderr_data.decode().strip()}"
	except subprocess.CalledProcessError as e:
		return False, f"Error: {e.output.decode()}"


def tesseract_7seg(cv2_img):
	custom_config = r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789.'
	text = pytesseract.image_to_string(cv2_img, config=custom_config)
	return text

def morphology(image, morph_open=False, iterations=2):
	kernel = np.ones((3, 3), np.uint8)
	op = cv2.MORPH_OPEN if morph_open else cv2.MORPH_CLOSE
	return cv2.morphologyEx(image, op, kernel, iterations=iterations)

def dilate(image, iterations=1):
	kernel = np.ones((3, 3), np.uint8)
	return cv2.dilage(image, kernel, iterations=iterations)

def erode(image, iterations=1):
	kernel = np.ones((3, 3), np.uint8)
	return cv2.erode(image, kernel, iterations=iterations)

def preprocess(image, using_blur=False, binarization=True):
	gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
	clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
	contrast_enhanced = clahe.apply(gray)
	
	if using_blur:
		blurred = cv2.GaussianBlur(contrast_enhanced, (5, 5), 0)
	else:
		blurred = contrast_enhanced
	
	if binarization:
		_, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
	else:
		thresh = blurred
	
	return thresh

def preprocess_green(img):
	lower = np.array([65, 45, 75])
	upper = np.array([95, 255, 255])
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lower, upper)
	result = cv2.bitwise_and(img, img, mask=mask)
	return result

def preprocess_blue(img):
	lower = np.array([95, 100, 80])
	upper = np.array([135, 255, 255])
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lower, upper)
	result = cv2.bitwise_and(img, img, mask=mask)
	return result

def preprocess_brown(img):
	lower = np.array([25, 0, 60])
	upper = np.array([90, 255, 255])
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	mask = cv2.inRange(hsv, lower, upper)
	result = cv2.bitwise_and(img, img, mask=mask)
	return result
