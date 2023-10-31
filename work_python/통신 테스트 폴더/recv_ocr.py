from paddleocr import PaddleOCR
import cv2
import socket
import numpy as np
from collections import defaultdict

# byte로 받은 데이터를 img에 맞게 변환
def convert_img(data):
    data_arr = np.frombuffer(data, np.uint8) # numpy로 저장
    img = cv2.imdecode(data_arr, cv2.IMREAD_COLOR) # numpy -> img color decoding
    
    return img

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
def send_string(floorWords, locationWords):
    most_detfloorWords = max(floorWords, key=floorWords.get)
    most_detlocationWords = max(locationWords, key=locationWords.get)
    #통신코드
    #데이터 통합
    data1= '차량의 위치는 {}층 {}구역입니다.'.format(most_detfloorWords, most_detlocationWords)
    #데이터 전송
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('10.10.141.22', 5001))     # 접속할 서버의 ip주소와 포트번호를 입력.
    sock.send(data1.encode())
    """
    
    """
    print("result: ", most_detlocationWords)
    print("floor: ", most_detfloorWords)


# PaddleOCR 호출 및 옵션 설정(cuda 가속 여부, 언어, inference모델)
ocr = PaddleOCR(
    use_gpu=True, 
    gpu_id=0, 
    use_angle_cls=True, 
    lang="en")

# Socket 통신 = UDP
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
port = 8080
sock.bind(('', port))
buf_size = 1000000

# 검출된 단어 저장할 list
floorWords = defaultdict(int)
locationWords = defaultdict(int)

# 이미지 크기(5:4비율 유지)
width = 640
height = 512

# 관심영역 크기(start = 시작지점)
roi_x_start = (int)(width / 20)
roi_y_start = (int)(height / 8)
roi_width = (int)(width * 9 / 10)
roi_height = (int)(height / 2)

try:
    while True:
        data, addr = sock.recvfrom(buf_size) # 메세지(이미지) 받기
        
        img = convert_img(data) # 받은 메세지 byte -> img 형태로 변환
        
        if img is not None:
            frame = cv2.resize(img, (width, height), cv2.INTER_CUBIC) # 해상도 조절
            
            # ROI(관심영역) 설정
            ROI = frame[roi_y_start: roi_y_start+roi_height, roi_x_start: roi_x_start+roi_width]
        
            # 전처리
            pre_img = preprocess_image(ROI)
            
            cv2.imshow('detect', pre_img)
    
            # PaddleOCR 적용
            result = ocr.ocr(pre_img, cls=True)
    
            print(result[0]) # [[(x, y), (x, y), (x, y), (x, y)], [words, confidence]] 순서로 저장
    
            if result[0] is not None: # 텍스트 인식한 게 있다면
                for line in result[0]:
                    (k1_x, k1_y), (k2_x, k2_y), (k3_x, k3_y), (k4_x, k4_y) = line[0]
                    
                    # 좌상단 = min, 우하단 = max 좌표
                    (ed_x, ed_y) = max((k1_x, k1_y), (k2_x, k2_y), (k3_x, k3_y), (k4_x, k4_y))
                    (st_x, st_y) = min((k1_x, k1_y), (k2_x, k2_y), (k3_x, k3_y), (k4_x, k4_y))
            
                    words, confidence = line[1]
                    
                    # 인식 길이가 3 이상인 단어는 버림
                    if len(words) > 3:
                        continue
                    
                    print(words)
                    print(confidence)
                    
                    # 단어(key)에 대한 카운트(value)
                    if words[0] == 'B' or words[len(words) - 1] == 'F':
                        floorWords[words] += 1 # 층수
                    else:
                        locationWords[words] += 1 # 구역
                    
                    # 화면에 표시
                    str = words + " {:.2f}".format(confidence)
                    cv2.rectangle(frame, (int(st_x+roi_x_start), int(st_y+roi_y_start)), (int(ed_x+roi_x_start), int(ed_y+roi_y_start)), (0, 255, 0), 2)
                    cv2.putText(frame, str, (int(st_x+roi_x_start), int(st_y+roi_y_start - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    
            cv2.imshow('video', frame)
            
        # waitKey() = 프레임 조절
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 텍스트 send
    send_string(floorWords, locationWords)
    
 
# 오류 catch 
except Exception as e:
    print(f"Exception: {str(e)}")

cv2.destroyAllWindows()
