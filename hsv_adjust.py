import subprocess
import pytesseract
import cv2
import numpy as np
import argparse


def clr_preprocess(img):
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	lower_green = np.array([100, 50, 50])
	upper_green = np.array([130, 255, 255])
	mask = cv2.inRange(hsv, lower_green, upper_green)
	result = cv2.bitwise_and(img, img, mask=mask)
	return result

def nothing(x):
	pass

def pickup(filename):
	cv2.namedWindow("Settings", cv2.WINDOW_NORMAL)
	cv2.createTrackbar('H_Lower', 'Settings', 0, 180, nothing)
	cv2.createTrackbar('S_Lower', 'Settings', 0, 255, nothing)
	cv2.createTrackbar('V_Lower', 'Settings', 0, 255, nothing)
	cv2.createTrackbar('H_Upper', 'Settings', 180, 180, nothing)
	cv2.createTrackbar('S_Upper', 'Settings', 255, 255, nothing)
	cv2.createTrackbar('V_Upper', 'Settings', 255, 255, nothing)
	
	img = cv2.imread(filename)
	if img is None:
		print(f"Failed to open image file: {filename}")
		exit()
	hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	while True:
		h_l = cv2.getTrackbarPos('H_Lower', 'Settings')
		s_l = cv2.getTrackbarPos('S_Lower', 'Settings')
		v_l = cv2.getTrackbarPos('V_Lower', 'Settings')
		h_u = cv2.getTrackbarPos('H_Upper', 'Settings')
		s_u = cv2.getTrackbarPos('S_Upper', 'Settings')
		v_u = cv2.getTrackbarPos('V_Upper', 'Settings')
		
		lower = np.array([h_l, s_l, v_l])
		upper = np.array([h_u, s_u, v_u])
		mask = cv2.inRange(hsv, lower, upper)
		result = cv2.bitwise_and(img, img, mask=mask)
		cv2.imshow('Result', result)
		cv2.imshow('Mask', mask)
		
		key = cv2.waitKey(1) & 0xFF
		if key == ord('q'):
			break
		elif key == ord('s'):
			print(f"Lower: [{h_l}, {s_l}, {v_l}]")
			print(f"Upper: [{h_u}, {s_u}, {v_u}]")
	cv2.destroyAllWindows()
	

if __name__ == "__main__":
	parser = argparse.ArgumentParser("OCR")
	parser.add_argument("-i", "--input", help="filename")
	args = parser.parse_args()
	if args.input:
		pickup(args.input)
