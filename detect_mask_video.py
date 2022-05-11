# import the necessary packages
from PIL import Image
import tensorflow as tf
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from imutils.video import VideoStream
from numpy import asarray
from numpy import expand_dims
import numpy as np
import cv2
import pickle
import scipy
import time

def detect_and_predict_mask(frame, faceNet, maskNet, MyFaceNet):
	# grab the dimensions of the frame and then construct a blob from it
	(h, w) = frame.shape[:2]
	blob = cv2.dnn.blobFromImage(frame, 1.0, (160, 160), (104.0, 177.0, 123.0))

	# pass the blob through the network and obtain the face detections
	faceNet.setInput(blob)
	detections = faceNet.forward()
	# print(detections.shape)

	# initialize our list of faces, their corresponding locations, and the list of predictions from our face mask network
	faces = []
	locs = []
	preds = []
	signature = []

	# loop over the detections
	for i in range(0, detections.shape[2]):
		# extract the confidence (i.e., probability) associated with the detection
		confidence = detections[0, 0, i, 2]

		# filter out weak detections by ensuring the confidence is greater than the minimum confidence
		if confidence > 0.5:
			# compute the (x, y)-coordinates of the bounding box for the object
			box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
			(startX, startY, endX, endY) = box.astype("int")

			# ensure the bounding boxes fall within the dimensions of the frame
			(startX, startY) = (max(0, startX), max(0, startY))
			(endX, endY) = (min(w - 1, endX), min(h - 1, endY))

			# extract the face ROI, convert it from BGR to RGB channel ordering, resize it to 224x224, and preprocess it
			face = frame[startY:endY, startX:endX]
			face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
			face = cv2.resize(face, (160, 160))
			face = img_to_array(face)
			face = preprocess_input(face)

			# add the face and bounding boxes to their respective lists
			faces.append(face)
			locs.append((startX, startY, endX, endY))

	# only make a predictions if at least one face was detected
	if len(faces) > 0:
		# for faster inference we'll make batch predictions on *all* faces at the same time rather than one-by-one predictions in the above `for` loop
		faces = np.array(faces, dtype="float32")
		preds = maskNet.predict(faces, batch_size=32)
		signature = MyFaceNet.predict(faces, batch_size=32)

	# return a 2-tuple of the face locations and their corresponding locations
	return (locs, preds, signature)

# load our serialized face detector model from disk
prototxtPath = r"face_detector\deploy.prototxt"
weightsPath = r"face_detector\res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)

# load the face mask detector model from disk
maskNet = load_model("mask_detector.h5")
MyFaceNet = load_model('facenet_keras.h5')
#HaarCascade = cv2.CascadeClassifier(cv2.samples.findFile(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'))

# load the database face
myfile = open("data.pkl", "rb")
database = pickle.load(myfile)
myfile.close()

# initialize the video stream
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()

# loop over the frames from the video stream
while True:
	# grab the frame from the threaded video stream and resize it to have a maximum width of 1280 pixels
	width = 1280
	height = 720
	dim = (width, height)

	frame = vs.read()
	frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
	timer = time.time()

	min_dist=100
	identity=' '

	# detect faces in the frame and determine if they are wearing a face mask or not
	(locs, preds, signature) = detect_and_predict_mask(frame, faceNet, maskNet, MyFaceNet)

	# loop over the detected face locations and their corresponding locations
	for (box, pred) in zip(locs, preds):
		# unpack the bounding box and predictions
		(startX, startY, endX, endY) = box
		(mask, withoutMask) = pred

		for key, value in database.items() :
			dist = scipy.linalg.norm(value-signature)
			if dist < min_dist:
				min_dist = dist
				identity = key

		# determine the class label and color we'll use to draw the bounding box and text
		label = "Mask" if mask > withoutMask else "No Mask"
		color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

		# include the probability in the label
		label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

		# display the label and bounding box rectangle on the output frame
		cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
		cv2.putText(frame, identity, (startX, startY - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
		cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)
		print(identity)

	# menampilkan FPS
	endtimer = time.time()
	fps = 1/(endtimer-timer)
	cv2.putText(frame, "{:.2f}FPS".format(fps), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

	# show the output frame
	cv2.imshow("Kendelanang Mask and Face Recognition", frame)

	# if the `esc` key was pressed, break from the loop
	k = cv2.waitKey(5) & 0xFF
	if k == 27:
		break

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()
print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))