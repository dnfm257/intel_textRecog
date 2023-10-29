
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
        #전처리 끝난 값을 저장변수는 data라고가정
        # Display the image
        cv2.imshow('Image', img)
        
        cv2.waitKey(1)

    except zmq.Again as e:
        pass

    except KeyboardInterrupt:
        break
while False:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('10.10.141.22', 5001))     # 접속할 서버의 ip주소와 포트번호를 입력.
    sock.send(data.encode())
"""
#스마트폰에 sms로 결과 값을 보내는 코드
from twilio.rest import Client

account_sid = 'AC830601052a526b757f23cac741e8becb'
auth_token = 'token ' # 나중에 입력
client = Client(account_sid, auth_token)

message = client.messages.create(
  from_='+12563685788',
  body=data,encode(),
  to='+821031198106'
)

print(message.sid)
"""

cv2.destroyAllWindows()
