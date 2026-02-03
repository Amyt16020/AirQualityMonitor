from picamera2 import Picamera2
#from picamera2 import Preview
from libcamera import controls
import time
from datetime import datetime
import cv2
import numpy as np
#from textrecognize import func1
from recog1 import detect_text

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
	picam2 = Picamera2()
	preview_config = picam2.create_preview_configuration(main={"size": (800, 600)})
	picam2.configure(preview_config)
	picam2.start()
	
	picam2.set_controls({"AfMode": controls.AfModeEnum.Continuous})
	
	#filename = "amy_001.png"

	try:
		while True:
			frame = picam2.capture_array()
			frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
			
			#frame_bgr = func1(frame_bgr)
			frame_bgr = detect_text(frame_bgr)
			cv2.imshow("Picamera2 Feed", frame_bgr)
			
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
			#if cv2.waitKey(1) & 0xFF == ord('q'):
			#	break
#	except KeyboardInterrupt:
	finally:
		picam2.stop()
		cv2.destroyAllWindows()
		
	

def main():
	cv2Preview()

if __name__ == "__main__":
    main()
