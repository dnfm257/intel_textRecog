import zmq
import numpy as np
import cv2

context = zmq.Context()
socket = context.socket(zmq.REP) # open socket REP&REQ mode
socket.bind("tcp://*:8081") # port 번호

while True:
    try:
        message = socket.recv() # 메세지(이미지) 받기
        
        nparr = np.frombuffer(message, np.uint8) # numpy로 저장
        img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR) # numpy -> img decoding

        if img_np is not None:
            cv2.imshow('Received from Raspberry Pi', img_np)
            
            # OCR
            
            reply_msg = "Processed Img" # 클라이언트에 보낼 답장
            
        else:
            reply_msg = "Received Empty Img"

        cv2.waitKey(1)

        # 이미지 수신 확인 응답
        socket.send_string(reply_msg)
        
    # 에러가 발생할 경우 catch
    except zmq.Again as e:
        print("Timeout error: did not receive request from client")
        
    except zmq.ZMQError as e:
        print(f"ZeroMQ Error: {str(e)}")
        
    except Exception as e:
         print(f"Exception: {str(e)}")