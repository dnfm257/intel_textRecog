from paddleocr import PaddleOCR
import cv2
from collections import defaultdict

# PaddleOCR 호출(cuda 가속 여부, 언어)
ocr = PaddleOCR(use_gpu=True, gpu_id=0, use_angle_cls=True, lang="en")

# 전처리 부분
def preprocess_image(image):
    image_img = cv2.cvtColor(image, cv2.COLOR_BGR2YCrCb)
    Y, Cr, Cb = cv2.split(image_img) # Y, Cr, Cb 로 분리
    eq_Y = cv2.equalizeHist(Y) # Y(밝기값)에 대한 평준화 -> 명암 대비 커지게
    dst_img = cv2.merge([eq_Y, Cr, Cb]) # 다시 YCbCr 합치기
    dst_img = cv2.cvtColor(dst_img, cv2.COLOR_YCrCb2BGR)
    return dst_img

# 컴퓨터 카메라, 영상을 사용할 경우
file_path = 'C:/Users/iot24/intel_textRecog/test/video_sample/G_well.avi'
cap = cv2.VideoCapture(file_path)
if not cap.isOpened():
    exit
    
# 검출된 단어 저장할 list
detected_words = defaultdict(int)

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("videos not found")
        break
    
    if frame is not None:
        frame = cv2.resize(frame, (800, 450), cv2.INTER_AREA) # 800x450 해상도
        
        (roi_x, roi_y), (roi_w, roi_h) = (0, 150), (800, 150)
        ROI = frame[roi_y: roi_y+roi_h, roi_x: roi_x+roi_w]
        
        pre_img = preprocess_image(ROI)
        cv2.imshow('recog', pre_img)
        
        result = ocr.ocr(pre_img, cls=True) # PaddleOCR 적용
    
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
                cv2.rectangle(frame, (int(st_x), int(st_y + roi_y)), (int(ed_x), int(ed_y + roi_y)), (0, 255, 0), 2)
                cv2.putText(frame, str, (int(st_x), int(st_y + roi_y - 8)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
  
        cv2.imshow('video', frame)
        
        # waitKey() = REP & REQ 프로토콜 유지(다음 프레임 전까지 send respond)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
#많이 검출된 단어 뽑기
if detected_words:
    most_detected_words = max(detected_words, key=detected_words.get)
    #여기에 서버로 단어 전송할 코드
    print(most_detected_words)
    print(detected_words[most_detected_words])
    
cap.release()
cv2.destroyAllWindows()
