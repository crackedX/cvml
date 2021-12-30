# Grab video from webcam, make some fancy effect, send it to UDP stream in MJPEG format

STREAMOUTIP = "127.0.0.1"
STREAMOUTPORT = 1234
STREAMCHUNK = 1300

import cv2
import socket


div = 40
bs = 49
c = 10

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cap = cv2.VideoCapture(0 + cv2.CAP_DSHOW)


while(True):
	#grab frame from camera
	ret, frame = cap.read()
	
	#make it fancy

	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	#frameabs = cv2.convertScaleAbs(frame, alpha = 2.5, beta = 50)
	
	mask = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,bs,c)
	mergeimg = cv2.bitwise_and(frame, frame, mask = mask)
		
	imgsmall = cv2.resize(mergeimg, (80,60), interpolation = cv2.INTER_LINEAR)
	imgsmallreduced = imgsmall // div * div + div // 2
	#imgsmallreduced = imgsmall
	imglarge = cv2.resize(imgsmallreduced, (800,600), interpolation = cv2.INTER_NEAREST)
	

	#reference video on screen
	cv2.imshow('img',imglarge)

	#encode to jpeg and send MPEG header
	outjpg = cv2.imencode('.jpg', imglarge, [int(cv2.IMWRITE_JPEG_QUALITY), 85])[1].tobytes()
	sock.sendto(("--video boundary--\nContent-length: " + str(len(outjpg)) + "\nContent-type: image/jpeg\n\n").encode(), (STREAMOUTIP, STREAMOUTPORT))
	
	#chunk steam up for UDP transmission with no fragments
	for i in range(0,len(outjpg), STREAMCHUNK):
		sock.sendto(outjpg[i:i+STREAMCHUNK], (STREAMOUTIP, STREAMOUTPORT))
		
	k = cv2.waitKey(1)
	if k & 0xFF == ord('q'):
		break
		
	if k & 0xFF == ord('d'):
		bs = bs + 2
		print("bs = {}".format(bs))
		
	if k & 0xFF == ord('x'):
		bs = bs - 2
		print("bs = {}".format(bs))

	if k & 0xFF == ord('c'):
		c = c + 1
		print("c = {}".format(c))

	if k & 0xFF == ord('z'):
		c = c - 1
		print("c = {}".format(c))

cap.release()
cv2.destroyAllWindows()
