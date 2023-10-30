import cv2
import socket
import numpy as np

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 8080
s.bind(('', port))

try:
    while True:
        data, addr = s.recvfrom(1000000)
        
        data_arr = np.frombuffer(data, np.uint8)
        img = cv2.imdecode(data_arr, cv2.IMREAD_COLOR)
        
        if img is not None:
            cv2.imshow('Img Server', img)
        
        if cv2.waitKey(1) & 0xFF == 27:
            break

except Exception as e:
    print(f"An error occurred: {e}")
    
finally:
    cv2.destroyAllWindows()