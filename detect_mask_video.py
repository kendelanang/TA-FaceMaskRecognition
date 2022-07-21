# import the necessary packages
import cv2
import gtts
import numpy as np
import os
import pickle
import pyrebase
import serial
import scipy
import time
import tkinter as tk
from imutils.video import VideoStream
from keras.models import load_model
from numpy import asarray, identity
from numpy import expand_dims
from os import listdir
from PIL import Image
from playsound import playsound
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from tkinter import messagebox

# Firebase Config
firebaseConfig={
	"apiKey": "AIzaSyDa6rWfDO6zPf-dBsx64drac4m7Z03MCBI",
  	"authDomain": "facemaskrecognition-8c4ca.firebaseapp.com",
  	"databaseURL": "https://facemaskrecognition-8c4ca-default-rtdb.firebaseio.com",
  	"projectId": "facemaskrecognition-8c4ca",
  	"storageBucket": "facemaskrecognition-8c4ca.appspot.com",
  	"messagingSenderId": "1019636202693",
  	"appId": "1:1019636202693:web:d10b98c061b4182506c4ac",
  	"measurementId": "G-B1W7FY6RLV",
	"serviceAccount": "serviceAccountKey.json"}

firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()
realtimedb = firebase.database()
jumlahLogin = realtimedb.child("cobi/TLogin").get()

path_on_cloud = "userImage/"
path_local = "fotoPeserta/"
# storage.child(path_on_cloud).put(path_local) # Untuk Upload dari Local Ke Cloud
# storage.child(path_on_cloud).download("test download.jpg") # Untuk Download dari Cloud Ke Local

# Inisialisasi Serial COM Arduino Ke Python
ser = serial.Serial('COM3',9600)
ser.timeout = 1
simpan = False

# Load Face Detector Model & Face Mask Detector Model
prototxtPath = r"face_detector\deploy.prototxt"
weightsPath = r"face_detector\res10_300x300_ssd_iter_140000.caffemodel"
faceNet = cv2.dnn.readNet(prototxtPath, weightsPath)
maskNet = load_model("mask_detector.h5")
MyFaceNet = load_model('facenet_keras.h5')
HaarCascade = cv2.CascadeClassifier(cv2.samples.findFile(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'))

# Folder Foto Sser
folder='fotoPeserta/userImage/'
database = {}

# Load Database Face
myfile = open("data.pkl", "rb")
database = pickle.load(myfile)
myfile.close()

# initialize the video stream
print("[INFO] Program Dimulai...")
vs = VideoStream(src=1).start()

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

			# extract the face ROI, convert it from BGR to RGB channel ordering, resize it to 160x160, and preprocess it
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

def trainingWajah():
	response = messagebox.askyesnocancel("Peringatan", "Download Image Dari Firebase Lagi?")
	if response == True:
		intructions.config(text="Sedang Mengunduh Image")
		all_files = storage.child("userImage").list_files()
		for file in all_files:
			print("Sedang download"+file.name)
			file.download_to_filename(path_local + file.name)
			intructions.config(text="Download Selesai")
			print("Download selesai")

	if response == False:
		intructions.config(text="Sedang Melakukan Training Wajah")
		for filename in listdir(folder):

			path = folder + filename
			gbr1 = cv2.imread(folder + filename)
			
			wajah = HaarCascade.detectMultiScale(gbr1,1.1,4)
			
			if len(wajah)>0:
				x1, y1, width, height = wajah[0]         
			else:
				x1, y1, width, height = 1, 1, 10, 10
				
			x1, y1 = abs(x1), abs(y1)
			x2, y2 = x1 + width, y1 + height
			
			gbr = cv2.cvtColor(gbr1, cv2.COLOR_BGR2RGB)
			gbr = Image.fromarray(gbr)                  # konversi dari OpenCV ke PIL
			gbr_array = asarray(gbr)
			
			face = gbr_array[y1:y2, x1:x2]                        
			
			face = Image.fromarray(face)                       
			face = face.resize((160,160))
			face = asarray(face)
			
			face = face.astype('float32')
			mean, std = face.mean(), face.std()
			face = (face - mean) / std
			
			face = expand_dims(face, axis=0)
			signature = MyFaceNet.predict(face)
			
			database[os.path.splitext(filename)[0]]=signature

		myfile = open("data.pkl", "wb")
		pickle.dump(database, myfile)
		myfile.close()
		trainingselesai()


def absensiWajah():
# loop over the frames from the video stream
	global identity
	while True:
		if(ser.is_open == False):
			ser.open()
		
		# grab the frame from the threaded video stream and resize it to have a maximum width of 1280 pixels
		# width = 800
		# height = 600
		width = 854
		height = 480
		dim = (width, height)

		frame = vs.read()
		frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
		timer = time.time()

		min_dist=100
		identity=''

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
			global rabel 
			rabel = label
			color = (0, 255, 0) if label == "Mask" else (0, 0, 255)

			# include the probability in the label
			label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

			# display the label and bounding box rectangle on the output frame
			cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
			cv2.putText(frame, identity, (startX, startY - 100), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
			cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

			bacanama()
			#bacalogin()
			
			#print(ser.in_waiting)
			if ser.in_waiting>0:
				simpan = False
				if rabel == "Mask" and simpan == False:
					ser.write(str(identity+">").encode())
					simpan = True
					time.sleep(0)
					tts = gtts.gTTS("SELAMAT DATANG"+identity+". SILAHKAN MASUK", lang="id")
					tts.save('sebutnama.mp3')
					playsound('sebutnama.mp3')
					os.remove('sebutnama.mp3')

					# tts.save('C:/Users/iya/Documents/GitHub/TA-FaceMaskRecognition/sebutnama.mp3')
					# playsound('C:/Users/iya/Documents/GitHub/TA-FaceMaskRecognition/sebutnama.mp3')
					# os.remove('C:/Users/iya/Documents/GitHub/TA-FaceMaskRecognition/sebutnama.mp3')
					ser.close()
				
				if rabel == "No Mask" and simpan == False:
					ser.write(str(rabel+">").encode())
					simpan = True
					time.sleep(0)
					playsound('nomask.mp3')
					# playsound('C:/Users/iya/Documents/GitHub/TA-FaceMaskRecognition/nomask.mp3')
					ser.close()
					

		# menampilkan FPS
		endtimer = time.time()
		fps = 1/(endtimer-timer)
		
		#cv2.putText(frame, "{:.2f}FPS".format(fps), (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

		# show the output frame
		cv2.imshow("Kendelanang Mask and Face Recognition", frame)
		
		# if the `esc` key was pressed, break from the loop
		k = cv2.waitKey(5) & 0xFF
		if k == 27:
			break
	
	# do a bit of cleanup
	cv2.destroyAllWindows()
	vs.stop()

def bacanama():
	if rabel == "Mask":
		intructions.config(text="")
		intructions.config(text="Selamat Datang "+identity)

	else :
		intructions.config(text="")
		intructions.config(text="Gunakan Masker Dengan Benar!")
	
def trainingselesai():
    intructions.config(text="Training Wajah Selesai")

def daftar():
	entry1 = tk.Entry (root, font="Montserrat")
	canvas.create_window(457, 170, height=25, width=411, window=entry1)
	label1 = tk.Label(root, text="Nama ", font="Montserrat", fg="white", bg="black")
	canvas.create_window(90,170, window=label1)
	Daftar_text = tk.StringVar()
	Daftar_btn = tk.Button(root, textvariable=Daftar_text, font="Montserrat", bg="#20bebe", fg="white", height=1, width=15, command=daftar)
	Daftar_text.set("Mulai Capture")
	Daftar_btn.place(x = 252, y = 210)

def bacalogin():
	jmlLogin.config(text="Jumlah Login : "+str(jumlahLogin.val()))

def stream_handler(message):
	jmlLogin.config(text="Jumlah Login : "+str(message["data"]))
    #print(message["data"]) # {'title': 'Pyrebase', "body": "etc..."}

my_stream = realtimedb.child("cobi/TLogin").stream(stream_handler)


root = tk.Tk()
root.title("Deteksi Penggunaan Masker GUI")
root.geometry("700x400")
# mengatur canvas (window tkinter)
canvas = tk.Canvas(root, width=700, height=400)
canvas.grid(columnspan=3, rowspan=8)
canvas.configure(bg="black")
# judul
judul = tk.Label(root, text="Deteksi Penggunaan Masker", font=("Montserrat",34),bg="#242526", fg="white")
canvas.create_window(350, 80, window=judul)
#credit
made = tk.Label(root, text="Dikembangkan Oleh Rafael Alferdyas Putra", font=("Montserrat",13), bg="black",fg="white")
canvas.create_window(360, 20, window=made)

global intructions, jmlLogin

# tombol untuk Daftarkan data wajah
intructions = tk.Label(root, text="Selamat Datang", font=("Montserrat",15),fg="white",bg="black")
canvas.create_window(370, 300, window=intructions)
jmlLogin = tk.Label(root, text="Jumlah Login : ", font=("Montserrat",10),fg="white",bg="black")
canvas.create_window(70, 20, window=jmlLogin)
Rekam_text = tk.StringVar()
Rekam_btn = tk.Button(root, textvariable=Rekam_text, font="Montserrat", bg="#20bebe", fg="white", height=1, width=15, command=bacalogin)
Rekam_text.set("Refresh")
Rekam_btn.grid(column=0, row=7)

# tombol untuk training wajah
Rekam_text1 = tk.StringVar()
Rekam_btn1 = tk.Button(root, textvariable=Rekam_text1, font="Montserrat", bg="#20bebe", fg="white", height=1, width=15, command=trainingWajah)
Rekam_text1.set("Training Wajah")
Rekam_btn1.grid(column=1, row=7)

# tombol deteksi penggunaan masker
Rekam_text2 = tk.StringVar()
Rekam_btn2 = tk.Button(root, textvariable=Rekam_text2, font="Montserrat", bg="#20bebe", fg="white", height=1, width=20, command=absensiWajah)
Rekam_text2.set("Mulai Deteksi")
Rekam_btn2.grid(column=2, row=7)

root.mainloop()