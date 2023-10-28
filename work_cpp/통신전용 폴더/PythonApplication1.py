
import zmq
import numpy as np
import cv2
import socket

while True:
    # ZeroMQ Context
    context = zmq.Context()

    # Define the socket using the "Context"
    sock = context.socket(zmq.SUB)

    # Define subscription and messages with prefix to accept.
    sock.setsockopt_string(zmq.SUBSCRIBE, np.unicode(''))

    # Connect to the Server
    sock.connect("tcp://localhost:5555")
    try:
        msg = sock.recv_string(flags=zmq.NOBLOCK)
        img = np.frombuffer(msg, dtype=np.uint8)
        img = cv2.imdecode(img, cv2.IMREAD_COLOR)
        #��ó�� ���� ���� ���庯���� data�����
        # Display the image
        cv2.imshow('Image', img)
        
        cv2.waitKey(1)

    except zmq.Again as e:
        pass

    except KeyboardInterrupt:
        break
while False:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('10.10.141.22', 5001))     # ������ ������ ip�ּҿ� ��Ʈ��ȣ�� �Է�.
    sock.send(data.encode())

cv2.destroyAllWindows()
