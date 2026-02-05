from picamera2 import Picamera2
#from picamera2 import Preview
from libcamera import controls
import time
from datetime import datetime
import cv2
import numpy as np
import ocr
import logger


def picam2Preview():
	picam2 = Picamera2()
	
	preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
	picam2.configure(preview_config)
	
	picam2.start_preview(Preview.QTGL)
	
	picam2.start()
	
	try:
		time.sleep(10)
	finally:
		picam2.stop_preview()
		picam2.stop()
	
	print('Done.')


def cv2Preview():
	liveview_w = 800
	liveview_h = 600
	x1 = 342
	y1 = 66

	x_hcho = 339
	y_hcho = 47
	
	x_co = 342
	y_co = 250
	
	x_co2 = 344
	y_co2 = 301
	w1 = 132
	h1 = 54
	border_color = (0, 255, 0)
	border_hcho = (0, 128, 200)
	border_co = (128, 0, 64)
	border_co2 = (200, 0, 128)
	
	picam2 = Picamera2()
	preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
	picam2.configure(preview_config)
	picam2.start()
	
	picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
	
	with open("./url.txt", "rt") as f:
		GAS_URL = f.readline()
		GAS_URL = GAS_URL.rstrip()

	try:
		while True:
			frame = picam2.capture_array()
			frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
			
			disp = frame_bgr.copy()
			cv2.rectangle(disp, (x1, y1), (x1 + w1, y1 + h1), border_color, 2)
			cv2.rectangle(disp, (x_hcho, y_hcho), (x_hcho + w1, y_hcho + h1), border_hcho, 2)
			cv2.rectangle(disp, (x_co, y_co), (x_co + w1, y_co + h1), border_co, 2)
			cv2.rectangle(disp, (x_co2, y_co2), (x_co2 + w1, y_co2 + h1), border_co2, 2)
			cv2.putText(disp, f"{x1},{y1}", (x1 + 4, y1 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 232, 0), 1, cv2.LINE_AA)
						
			cv2.imshow("Camera View", disp)
			
			key = cv2.waitKey(1) & 0xFF
			if key == ord('q'):
				break
			elif key == ord('c'):
				now = datetime.now()
				filename = now.strftime("%H-%M-%S.png")
				success = cv2.imwrite(filename, frame_bgr)
				if success:
					print("Capture image done")
				else:
					print("Error: failed to save image")
			elif key == ord('w'):
				if y1 > 1:
					y1 -= 1
			elif key == ord('s'):
				if y1 < liveview_h - h1 - 1:
					y1 += 1
			elif key == ord('a'):
				if x1 > 1:
					x1 -= 1
			elif key == ord('d'):
				if x1 < liveview_w - w1 - 1:
					x1 += 1
			elif key == ord('p'):
				now = datetime.now()
				timestamp_str = now.strftime("%H-%M-%S")
				
				roi_co2 = frame_bgr[y_co2:y_co2+h1, x_co2:x_co2+w1]
				fixed_co2 = ocr.preprocess(roi_co2)
				co2_value = ocr.ssocr_7seg(fixed_co2, False)

				time.sleep(0.1)
				roi_hcho = frame_bgr[y_hcho:y_hcho+h1, x_hcho:x_hcho+w1]
				fixed_hcho = ocr.preprocess(roi_hcho)
				hcho_value = ocr.ssocr_7seg(fixed_hcho, True)

				time.sleep(0.1)
				roi_co = frame_bgr[y_co:y_co+h1, x_co:x_co+w1]
				fixed_co = ocr.preprocess(roi_co)
				co_value = ocr.ssocr_7seg(fixed_co, False)

				logger.upload_data(GAS_URL, hcho_value, co2_value, co_value, timestamp_str)

				cv2.imshow('CO2', fixed_co2)
				cv2.imwrite(f"CO2-{timestamp_str}.png", roi_co2)
				
				cv2.imshow('HCHO', fixed_hcho)
				cv2.imwrite(f"HCHO-{timestamp_str}.png", roi_hcho)
				
				cv2.imshow('CO', fixed_co)
				cv2.imwrite(f"CO-{timestamp_str}.png", roi_co)
				
				print(f"CO2: {co2_value} | HCHO: {hcho_value} | CO: {co_value}")
	finally:
		picam2.stop()
		cv2.destroyAllWindows()
		
	

def main():
	cv2Preview()

if __name__ == "__main__":
    main()
