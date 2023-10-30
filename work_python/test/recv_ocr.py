from paddleocr import PaddleOCR
import cv2
import socket
import numpy as np
from collections import defaultdict

# 전처리 부분
def preprocess_image(img):
    blurred = cv2.GaussianBlur(img, (5, 5), 0)
    sharpened = cv2.addWeighted(img, 1.5, blurred, -0.5, 0)
    
    ycrcb_img = cv2.cvtColor(sharpened, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = cv2.split(ycrcb_img) # Y, Cr, Cb 로 분리
    
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    clahe_Y = clahe.apply(Y) # Y(밝기값)에 대한 평준화 -> 명암 대비 커지게
    #eq_Y = cv2.equalizeHist(Y)
    
    dst_img = cv2.merge([clahe_Y, Cr, Cb]) # 다시 YCbCr 합치기
    dst_img = cv2.cvtColor(dst_img, cv2.COLOR_YCrCb2BGR)
    
    return dst_img

#많이 검출된 단어 뽑아서 전송
def send_string(detected_words):
    if detected_words:
        most_detected_words = max(detected_words, key=detected_words.get)
        #여기에 서버로 단어 전송할 코드
        
        str = "result: "
        print(str + most_detected_words)


# PaddleOCR 호출 및 옵션 설정(cuda 가속 여부, 언어, inference모델)
ocr = PaddleOCR(
    use_gpu=True, 
    gpu_id=0, 
    use_angle_cls=True, 
    lang="en")

# Socket 통신 = REQ(request) & REP(reply) mode
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 8080
sock.bind(('', port))
buf_size = 1000000

# 검출된 단어 저장할 list
detected_words = defaultdict(int)

#이미지 크기(5:4비율 유지)
width = 640
height = 512

try:
    while True:
        data, addr = sock.recvfrom(buf_size) # 메세지(이미지) 받기
        
        data_arr = np.frombuffer(data, np.uint8) # numpy로 저장
        img = cv2.imdecode(data_arr, cv2.IMREAD_COLOR) # numpy -> img color decoding
        
        if img is not None:     
            frame = cv2.resize(img, (width, height), cv2.INTER_CUBIC) # 해상도 조절
            
            # ROI(관심영역) 설정
            (roi_x, roi_y), (roi_w, roi_h)= (int(width / 20), int(height / 8)), (int((width / 10) * 9), int(height / 2))
            ROI = frame[roi_y: roi_y+roi_h, roi_x: roi_x+roi_w]
        
            # 전처리
            pre_img = preprocess_image(ROI)
            
            cv2.imshow('detect', pre_img)
    
            # PaddleOCR 적용
            result = ocr.ocr(pre_img, cls=True)
    
            print(result[0]) # [[(x, y), (x, y), (x, y), (x, y)], [words, confidence]] 순서로 저장
    
            if result[0] is not None: # 텍스트 인식한 게 있다면
                for line in result[0]:
                    (st_x, st_y), (k1_x, k1_y), (ed_x, ed_y), (k2_x, k2_y) = line[0]
                    # 좌상단 = min, 우하단 = max 좌표
                    (ed_x, ed_y) = max((st_x, st_y), (k1_x, k1_y), (ed_x, ed_y), (k2_x, k2_y))
                    (st_x, st_y) = min((st_x, st_y), (k1_x, k1_y), (ed_x, ed_y), (k2_x, k2_y))
            
                    words, confidence = line[1]
                    print(words)
                    print(confidence)
                    
                    detected_words[words] += 1 # 단어(key)에 대한 카운트(value)
                    
                    # 화면에 표시
                    str = words + " {:.2f}".format(confidence)
                    cv2.rectangle(frame, (int(st_x+roi_x), int(st_y+roi_y)), (int(ed_x+roi_x), int(ed_y+roi_y)), (0, 255, 0), 2)
                    cv2.putText(frame, str, (int(st_x+roi_x), int(st_y+roi_y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
  
            cv2.imshow('video', frame)  
            
        # waitKey() = 프레임 조절
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 텍스트 send
    send_string(detected_words)
 
# 오류 catch 
except Exception as e:
    print(f"Exception: {str(e)}")


cv2.destroyAllWindows()