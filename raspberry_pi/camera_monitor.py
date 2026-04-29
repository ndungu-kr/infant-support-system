import paho.mqtt.client as mqtt
import json
import os
import threading
import time
import sys
import cv2
import dlib
import numpy as np
from picamera2 import Picamera2

"""
Infant Monitor

 feature 1: detect infant facial feature (eyes and mouth) to determine if the infant is sleeping, awake, or crying 
 (for crying, the infant needs to open their mouth and the noise detector needs to exceed the noise threshold to be consider crying)
 
 feature 2: (only when trigger by node red) first, detect infant presence by checking if the head is on camera using dlib cnn (for higher accuracy)
			if the infant is presence, detect if infant is moving, if infant havent move for x second, send alert
"""

# Configuration
#----------------

# Camera config
RESOLUTION = (480,640)
FPS = (33333, 33333) #30 fps

# MQTT config
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "infant/sensors"

# Noise threshold to be consider crying
NOISE_THRESHOLD = 500

# Motion detection config
MOTION_THRESHOLD = RESOLUTION[0] * RESOLUTION[1] * 0.05 # if the number of pixels change more than this = infant move

# Motion detection time
MOTION_DETECTION_SEC = 5.0 # the motion detector will run for x sec and if infant did not move at all during that time = return alert

# Run motion detection (only when triggered) & HOG + landmarks to check for eyes and mouth every x second
MAIN_CHECK_INTERVAL_SEC = 1 

#dlib CNN interval
CNN_INTERVAL_SEC = 300.0 # Run CNN (which is more accurate than HOG) to check if the infant is on screen every x second
ACCEPTABLE_ASSUMPTION_RANGE_SEC = 10.0 # IF CNN is called x second ago, assume that the result still stands

# Face state threshold
EAR_THRESHOLD = 0.2 # Eye aspect ratio above this = eye opened
MAR_THRESHOLD = 0.5 # Mouth aspect ratio above this = mouth opened

#Dlib model paths
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

LANDMARK_MODEL = os.path.join(_SCRIPT_DIR, "shape_predictor_68_face_landmarks.dat")
CNN_MODEL = os.path.join(_SCRIPT_DIR, "mmod_human_face_detector.dat")

#Debug 
DEBUG_SHOW_CAMERA = True # If true will show the camera display
DEBUG_WINDOW_NAME = "Infant monitor debug"

class InfantMonitor:
	def __init__(self):
		# dlib models
		self._hog_detector = dlib.get_frontal_face_detector()
		self._cnn_detector = dlib.cnn_face_detection_model_v1(CNN_MODEL)
		self._landmark_predictor = dlib.shape_predictor(LANDMARK_MODEL)
		
		# camera
		self._camera = Picamera2()
		config = self._camera.create_preview_configuration(main={"size": RESOLUTION}, controls={"FrameDurationLimits": FPS})
		self._camera.configure(config)
		self._camera.start()
		time.sleep(2) # Let auto-exposure settle before processing begins
		
		# arduino sensors
		self._arduino_lock = threading.Lock()
		# noise value
		self._latest_noise = 0
		# node red trigger process
		self._node_red_trigger = False
		
		# MQTT client - loop_start() will run a background thread automatically
		self._mqtt_client = mqtt.Client()
		self._mqtt_client.on_connect = self._on_mqtt_connect
		self._mqtt_client.on_message = self._on_mqtt_message
		self._mqtt_client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
		self._mqtt_client.loop_start()
		
		# create a background thread for CNN to check if infant is on camera
		self._cnn_trigger = threading.Event()
		self._cnn_result = "infant_present"
		self._cnn_result_lock = threading.Lock() #use lock to prevent racing issue
		self._cnn_frame = None
		self._cnn_frame_lock = threading.Lock() #use lock to prevent racing issue
		self._cnn_running = True
		
		self._cnn_thread = threading.Thread(target=self._cnn_worker, daemon=True)
		
		self._cnn_thread.start()
		
		# motion state
		self._hist_lock = threading.Lock()
		self._prev_eq_hist = None
		self._current_eq_hist = None
		
		# HOG timer
		self._last_hog_time = 0.0
		self._current_face_state = "none"
		self._is_crying = False
		
		# CNN scheduling timer
		self._cnn_time_lock = threading.Lock()
		self._last_cnn_time = 0.0
		
		# prevent duplicate output
		self._last_printed = {}
		
# MQTT CALLBACKS---------------------------------------------------------
	def _on_mqtt_connect(self, client, userdata, flags, rc):
		if rc ==0:
			client.subscribe(MQTT_TOPIC)
			
	def _on_mqtt_message(self, client, userdata, msg):
		try:
			data = json.loads(msg.payload.decode("utf-8"))
			with self._arduino_lock:
				self._latest_noise = int(data.get("LOUDNESS",0))
				# add the node red trigger here
				
		except:
			pass
	
	@property
	def _noise(self):
		with self._arduino_lock:
			return self._latest_noise
			
	@property
	def _trigger_process(self):
		with self._arduino_lock:
			return self._node_red_trigger

# WORKER THREADS----------------------------------------------------------

	# background thread for dlib cnn and motion detection
	def _cnn_worker(self):
		while self._cnn_running:
			self._cnn_trigger.wait() #sleeps until it is called
			self._cnn_trigger.clear()
			
			if not self._cnn_running:
				break
			
			now = time.time()
			
			if now - self._cnn_time >= ACCEPTABLE_ASSUMPTION_RANGE_SEC:
				
				with self._cnn_frame_lock:
					frame = self._cnn_frame
					
				if frame is None:
					continue
					
				# downscale the frame into a smaller one to improve efficiency as we are only using it to check if the toddler is on screen
				h, w = frame.shape[:2]
				scale = 320/w
				small = cv2.resize(frame, (320, int(h * scale)))
				small = np.ascontiguousarray(small[:, :, :3], dtype=np.uint8)
				
				detections = self._cnn_detector(small,1)
				
				result = "infant_present" if len(detections) > 0 else "not_found"
				with self._cnn_result_lock:
					self._cnn_result = result
				with self._cnn_time_lock:
					self._last_cnn_time = now
					
				print("calling cnn")
			# motion detection is only triggered whenever node red triggers this thread and cnn detected infant is present
			if self._trigger_process and result == "infant_present":
				motion = self._handle_motion()
				
				# return the result immediately
				output = self._build_output(motion)
				self._print_to_node_red(output)
				
	@property
	def _infant_presence(self):
		with self._cnn_result_lock:
			return self._cnn_result
			
	@property
	def _cnn_time(self):
		with self._cnn_time_lock:
			return self._last_cnn_time
			
# HOG + LANDMARK DETECTION ----------------------------------------------------------------------------

	# return the coordination of the face
	def _landmark_pts(self, shape, indices):
		return np.array([[shape.part(i).x, shape.part(i).y] for i in indices] ,dtype=np.float64)
		
	# EAR = (sum of two vertical distance)/(2 * horizontal distance)
	# left eye indices = 36-41 right eye = 42-47
	# low EAR = eye closed
	def _eye_aspect_ratio(self, shape, left=True):
		pts = self._landmark_pts(shape, range(36,42) if left else range(42,48))
		A = np.linalg.norm(pts[1] - pts[5])
		B = np.linalg.norm(pts[2] - pts[4])
		C = np.linalg.norm(pts[0] - pts[3])
		return (A + B) / (2.0 * C) if C > 0 else 0.0
		
	# MAR = vertical mouth opening/ horizontal mouth width
	# Outer lip indices = 48-59
	# High MAR = mouth open
	def _mouth_aspect_ratio(self, shape):
		pts = self._landmark_pts(shape, range(48,60))
		A = np.linalg.norm(pts[2] - pts[10])
		B = np.linalg.norm(pts[0] - pts[6])
		return (A / B) if B > 0 else 0.0
		
	# return false when face is turned too far sideways for reliable EAR/MAR
	# check x-spread between left and right eye clusters
	# spread below 20px = face too sideways
	def _both_eyes_visible(self, shape):
		left_x = np.mean(self._landmark_pts(shape,range(36,42))[:,0])
		right_x = np.mean(self._landmark_pts(shape,range(42,48))[:,0])
		return abs(right_x - left_x) > 20
		
	# HOG + landmark detection
	def _run_hog_landmarks(self, gray_frame, noise_level):
		h = gray_frame.shape[0]
		upper = gray_frame[:h // 2,:]
		
		# start by checking the upper frame first
		dets = self._hog_detector(upper,1)
		use_frame = upper
		
		if len(dets) ==0:
			dets = self._hog_detector(gray_frame,1)
			use_frame = gray_frame
		
		# if no face is detected
		if len(dets) ==0:
			self._current_face_state = "face_not_visible"
			return None
			
		# in case there is more than one face detected (could be false positive), choose the largest one
		det = max(dets, key=lambda d: (d.right() - d.left()) * (d.bottom() - d.top()))
		
		shape = self._landmark_predictor(use_frame, det)
		
		if not self._both_eyes_visible(shape):
			self._current_face_state = "face_not_visible"
			return None
		
		# Eyes
		ear = (self._eye_aspect_ratio(shape, left=True) + self._eye_aspect_ratio(shape, left=False)) / 2.0
		
		# Mouth
		mar = self._mouth_aspect_ratio(shape)
		
		# if mouth is open and noise level exceed threshold = crying
		if mar > MAR_THRESHOLD and noise_level >= NOISE_THRESHOLD:
			self._is_crying = True
		else:
			self._is_crying = False
					
		#if eye lower than threshold = sleeping, else awake
		if ear < EAR_THRESHOLD:
			self._current_face_state = "sleeping"
		else:
			self._current_face_state = "awake"
		
# Motion Detection -------------------------------------------------------------------
	# comparing the difference between consecutive histogram-equalised frames and return the number of changed pixel.
	# Equalisation mitigates lighting changes that will cause false positve movement.
	def _compute_motion_score(self, equalised):
		if self._prev_eq_hist is None:
			self._prev_eq_hist = equalised.copy()
			return 0
		
		diff = cv2.absdiff(self._prev_eq_hist, equalised)
		_, thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)
		score = int(np.sum(thresh > 0))
		self._prev_eq_hist = equalised.copy()
		return score
		
	# if the number of changed pixel exceed motion threshold = the infant moved
	def _handle_motion(self):
		start = time.time()
		
		# keep running for x second, or until it found the something has moved in the camera. it also have the same amount of interval time for each call as the hog
		while time.time() - start <= MOTION_DETECTION_SEC:
			with self._hist_lock:
				frame = self._current_eq_hist
			
			score = self._compute_motion_score(frame)
			
			if score > MOTION_THRESHOLD:
				return True
			
			time.sleep(MAIN_CHECK_INTERVAL_SEC)
		
		return False
		
# OUTPUT---------------------------------------------------
	def _build_output(self, motion):
		return {
			"presence": self._infant_presence,
			"state": self._current_face_state,
			"crying": self._is_crying,
			"cameraMotion": motion
			}
	
	# used for comparing with the previous output key value
	def _output_key(self, output):
		return (output["presence"], output["state"], output["cameraMotion"], output["crying"])
	
	# if it is not the same as previous output, print json to
	def _print_to_node_red(self, output):
		key = self._output_key(output)
		last_key = self._output_key(self._last_printed) if self._last_printed else None
		
		if key != last_key:
			print(json.dumps(output),flush=True)
			self._last_printed = output.copy()
		
	def _debug_print(self, frame_rgb):
		if not DEBUG_SHOW_CAMERA:
			return
			
		display = cv2.cvtColor(frame_rgb,cv2.COLOR_RGB2BGR)
		cv2.imshow(DEBUG_WINDOW_NAME, display)
		cv2.waitKey(1)
		
# Main loop--------------------------------------------------------------------

	def run(self):
		try:
			while True:
				now = time.time()
				frame = self._camera.capture_array()
				
				# for debuging display
				self._debug_print(frame)
				
				# Preprocess: grayscale + histogram equalise
				gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
				equalised = cv2.equalizeHist(gray)
				
				# pass the frame to CNN thread
				with self._cnn_frame_lock:
					self._cnn_frame = frame.copy()
				with self._hist_lock:
					self._current_eq_hist = equalised
					
				# schedule CNN trigger if time has passed CNN_INTERVAL_SEC or it has been triggered by node red
				if now - self._cnn_time >= CNN_INTERVAL_SEC or self._trigger_process:
					self._cnn_trigger.set()
					
				if now - self._last_hog_time >= MAIN_CHECK_INTERVAL_SEC:
				
					# read latest noise from Arduino
					noise_level = self._noise
				
					# HOG + landmarks 
					self._last_hog_time = now
					self._run_hog_landmarks(gray, noise_level)
					
					# output
					output = self._build_output(None)
				
					self._print_to_node_red(output)
				
		except KeyboardInterrupt:
			pass
		finally:
			#clean shutdown
			self._cnn_running = False
			self._cnn_trigger.set() #unblock cnn_worker so it can exits
			self._cnn_thread.join(timeout=3.0)
			self._mqtt_client.loop_stop()
			self._mqtt_client.disconnect()
			self._camera.stop()
			
			#debug display window
			if DEBUG_SHOW_CAMERA:
				cv2.destroyAllWindows()
			
		
if __name__ == "__main__":
	monitor = InfantMonitor()
	monitor.run()
		
		
