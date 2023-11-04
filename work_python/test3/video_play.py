from paddleocr import PaddleOCR
import cv2
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
    
    dst_img = cv2.merge([clahe_Y, Cr, Cb]) # 다시 YCbCr 합치기
    dst_img = cv2.cvtColor(dst_img, cv2.COLOR_YCrCb2BGR)
    
    #dst_img = ~dst_img
    
    return dst_img


# 많이 검출된 단어 찾기
def detect_word(detected_words): 
    most_detected_words = max(detected_words, key=detected_words.get)
    
    # 한번만 검출되면 무시
    if detected_words[most_detected_words] == 1:
        most_detected_words = "None"
    
    return most_detected_words

# 제일 면적이 넓은 단어 찾기
def most_area_word(area):
    most_area_word = max(area, key=area.get)
    
    return most_area_word
    
# PaddleOCR 호출 및 옵션 설정(cuda 가속 여부, 언어, inference모델)
ocr = PaddleOCR(
    use_gpu=False, 
    gpu_id=0, 
    cpu_threads=14, 
    use_angle_cls=True, 
    lang="en")

# 검출된 단어 저장할 list
floorWords = defaultdict(int)
locationWords = defaultdict(int)

# 이미지 크기(영상 비율 유지)
width = 800
height = 450

# 관심영역 크기(start = 시작지점)
roi_x_start = (int)(width / 20)
roi_y_start = (int)(height / 8)
roi_width = (int)(width * 9 / 10)
roi_height = (int)(height / 2)

# 제일 많이 인식한 단어들
most_detfloorWords = "None"
most_detlocationWords = "None"

# 컴퓨터 카메라, 영상을 사용할 경우
file_path = 'D:/intel2_firmware/GitHub/video_sample/lotte_outlet.avi'
cap = cv2.VideoCapture(file_path)
if not cap.isOpened():
    exit

try:
    while True:
        ret, img = cap.read()
        
        if not ret:
            print("videos not found")
            break
        
        if img is not None:
            frame = cv2.resize(img, (width, height), cv2.INTER_LINEAR) # 해상도 조절
            
            # ROI(관심영역) 설정
            ROI = frame[roi_y_start: roi_y_start+roi_height, roi_x_start: roi_x_start+roi_width]
        
            # 전처리
            pre_img = preprocess_image(ROI)
            
            cv2.imshow('detect', pre_img)
    
            # PaddleOCR 적용
            result = ocr.ocr(pre_img, cls=True)
    
            #print(result) # [[(x, y), (x, y), (x, y), (x, y)], [words, confidence]] 순서로 저장
                      
            if result[0] is not None: # 텍스트 인식한 게 있다면
                
                area = defaultdict(int) # 넓이 저장
                
                # result[0][] = line 한 장면에서 검출된 단어 개수만큼
                for line in result[0]:
                    points = np.array([line[0][0], line[0][1], line[0][2], line[0][3]], dtype=np.int0)
                    words, confidence = line[1]
                    
                    # 인식단어 길이가 1 이상, 3 이하인 단어만 통과
                    if len(words) < 1 or len(words) > 3:
                        continue
                    
                    # 텍스트 위치에서 가장 작은 사각형 찾기
                    x, y, w, h = cv2.boundingRect(points)
                        
                    # 텍스트 넓이 저장
                    area[words] = w * h
                    
                # 해당 장면에서 넓이가 제일 넓은 단어만 추출
                if area:
                    area_word = most_area_word(area)
                
                # 단어(key)에 대한 카운트(value)
                if area_word[0] == 'B' or area_word[len(area_word) - 1] == 'F':
                    floorWords[area_word] += 1 # 층수
                else:
                    locationWords[area_word] += 1 # 구역
                    
                # 좌표 구해서 텍스트 box만들기
                str = area_word #+ " {:.2f}".format(confidence)
                real_x, real_y = (int)(x + roi_x_start), (int)(y + roi_y_start)
                cv2.rectangle(frame, (real_x, real_y), (real_x+w, real_y+h), (0, 255, 0), 2)
                cv2.putText(frame, str, (real_x, real_y - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
  
            cv2.imshow('video', frame)
            
        # waitKey() = 프레임 조절
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
            
    
    # 텍스트 send - 텍스트가 검출되지 않았을 경우 None으로 대체
    if floorWords:
        most_detfloorWords = detect_word(floorWords)
        print("floor: {}, count: {}".format(most_detfloorWords, floorWords[most_detfloorWords]))
        
    if locationWords:
        most_detlocationWords = detect_word(locationWords)
        print("location: {}, count: {}".format(most_detlocationWords, locationWords[most_detlocationWords]))
    
 
# 오류 catch 
except Exception as e:
    print(f"Exception: {str(e)}")

cv2.destroyAllWindows()