from picamera2 import Picamera2
#from picamera2 import Preview
from libcamera import controls
import time
from datetime import datetime
import cv2
import numpy as np
import ocr
import logger
import notify


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
	
	# ROI data: list of dictionaries containing name and coordinates [x, y, w, h]
	rois = [
		{"name": "HCHO", "coords": [250, 50, 120, 50]  },  # ROI 1
		{"name": "CO",   "coords": [250, 200, 110, 48] },  # ROI 2
		{"name": "CO2",  "coords": [250, 350, 110, 48] }   # ROI 3
	]
	
	active_idx = 0  # Default to the first ROI
	step = 10       # Initial step size, pixels to move per keypress
	
	# Timer setup
	last_save_time = time.time()
	save_interval = 60  # seconds
	detect_count = 0
	log_interval = 60   # (save_interval * log_interval) seconds
	timer_enabled = False  # Timer starts OFF by default
	
	print("--- Gas Monitor ROI Calibration ---")
	print("Keys: 1=HCHO, 2=CO, 3=CO2 | WASD=Move | T=Toggle Step | Q=Quit")

	picam2 = Picamera2()
	preview_config = picam2.create_preview_configuration(main={"size": (liveview_w, liveview_h)})
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
			
			# Status Overlay
			active_name = rois[active_idx]["name"]
			cv2.putText(disp, f"Adjusting: {active_name} | Step: {step}", (10, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
			# Show if timer is ON (Green) or OFF (Red)
			timer_status = "ON" if timer_enabled else "OFF"
			timer_color = (0, 255, 0) if timer_enabled else (0, 0, 255)
			cv2.putText(disp, f"TIMER: {timer_status}", (10, 60),
					cv2.FONT_HERSHEY_SIMPLEX, 0.6, timer_color, 1)
			
			for i, roi in enumerate(rois):
				name = roi["name"]
				x, y, w, h = roi["coords"]
				# Highlight the active ROI with a different color (Red vs Green)
				if i == active_idx:
					color = (0, 200, 0) # Green for active
					thickness = 3
				else:
					color = (60, 60, 240) # Red for inactive
					thickness = 1
				# Draw Rectangle
				cv2.rectangle(disp, (x, y), (x + w, y + h), color, thickness)
				#Draw Gas Name Label
				cv2.putText(disp, name, (x, y - 10),
							cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

			current_time = time.time()
			# Show countdown only if timer is active
			if timer_enabled:
				seconds_left = max(0, int(save_interval - (current_time - last_save_time)))
				cv2.putText(disp, f"Next Detect: {seconds_left}s", (10, 85),
						cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 1)

			cv2.imshow("Camera View", disp)
			
			# --- Periodic Logic ---
			if timer_enabled and (current_time - last_save_time >= save_interval):
				results = []
				for roi in rois:
					name = roi["name"]
					x, y, w, h = roi["coords"]
					# Crop the ROI from the frame: frame[y1:y2, x1:x2]
					roi_crop = frame_bgr[y:y+h, x:x+w]
					processed = ocr.preprocess(roi_crop)
					try:
						ocr_str = ocr.ssocr_7seg(processed)
						value = float(ocr_str)
						results.append(value)
					except ValueError:
						results.append("n/a")
				last_save_time = current_time # Reset timer
				print(f"-- {results[0]} | {results[1]} | {results[2]}")
				detect_count += 1
				if detect_count >= log_interval:
					logger.upload_data(GAS_URL,
						results[0], results[1], results[2], "n/a")

			# Keyboard Input Handling
			key = cv2.waitKey(1) & 0xFF
			
			# 1. Select ROI
			if key == ord('1'): active_idx = 0   # HCHO
			elif key == ord('2'): active_idx = 1 # CO
			elif key == ord('3'): active_idx = 2 # CO2
			
			# 2. Move ROI (w=up, s=down, a=left, d=right)
			elif key == ord('w'): rois[active_idx]["coords"][1] -= step
			elif key == ord('s'): rois[active_idx]["coords"][1] += step
			elif key == ord('a'): rois[active_idx]["coords"][0] -= step
			elif key == ord('d'): rois[active_idx]["coords"][0] += step
			
			# 3. Toggle Step size
			elif key == ord('t'):
				step = 1 if step == 10 else 10
				print(f"Step change to: {step}")

			# 4. Toogle Timer ON/OFF
			elif key == ord('u'):
				timer_enabled = not timer_enabled
				if timer_enabled:
					last_save_time = time.time()  # Reset timer when turned on
				print(f"Timer Enabled: {timer_enabled}")

			# 5. Exit
			elif key == ord('q'):
				break
			elif key == ord('c'):
				now = datetime.now()
				filename = now.strftime("%H-%M-%S.png")
				success = cv2.imwrite(filename, frame_bgr)
				if success:
					print("Capture image done")
				else:
					print("Error: failed to save image")
			elif key == ord('p'):
				now = datetime.now()
				timestamp_str = now.strftime("%H-%M-%S")
				
				imgs = []
				results = []
				for i, roi in enumerate(rois):
					name = roi["name"]
					x, y, w, h = roi["coords"]
					roi_img = frame_bgr[y:y+h, x:x+w]
					processed = ocr.preprocess(roi_img)
					imgs.append(processed)
					try:
						ocr_str = ocr.ssocr_7seg(processed)
						value = float(ocr_str)
						results.append(value)
					except ValueError:
						results.append("n/a")

				logger.upload_data(GAS_URL,
					results[0], results[1], results[2],
					timestamp_str)

				cv2.imshow(rois[0]["name"], imgs[0])			
				cv2.imshow(rois[1]["name"], imgs[1])			
				cv2.imshow(rois[2]["name"], imgs[2])
				names = [rois[0]["name"], rois[1]["name"], rois[2]["name"]]
				print(f"{names[0]}: {results[0]} | {names[1]}: {results[1]} | {names[2]}: {results[2]}")
	finally:
		picam2.stop()
		cv2.destroyAllWindows()
		
	

def main():
	cv2Preview()

if __name__ == "__main__":
    main()
