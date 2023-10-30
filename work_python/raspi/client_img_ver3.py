import cv2
import socket
import os
import numpy as np

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
buf_size = 1000000
sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buf_size)

server_ip = "10.10.141.24"
server_port = 8080

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cam Not Found")
    exit

while True:
    ret, frame = cap.read()
        
    if not ret:
        break
        
    # image -> jpg encoding
    ret, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
    
    # byte send
    sock.sendto(buffer.tobytes(), (server_ip, server_port))
                
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
cap.release()