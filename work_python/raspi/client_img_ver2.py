import cv2
import zmq
import base64

context = zmq.Context()
socket = context.socket(zmq.REQ) # open socket REP&REQ mode
socket.connect('tcp://10.10.141.24:8080') # server ip:port

cap = cv2.VideoCapture(0) # open video

while True:
    ret, frame = cap.read() # read video img
    if not ret:
        break
        
    encoded, buffer = cv2.imencode('.jpg', frame) # img -> byte
    socket.send(buffer.tobytes()) # byte send
    
    respond_msg = socket.recv().decode('utf-8') # receive message(blocking method)
        
cap.release()
cv2.destroyAllWindows()