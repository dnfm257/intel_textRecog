# Python용 코드

## 1. PaddleOCR 서버

#### * PaddleOCR 적용 방법
1. python 3.9.13 설치(최신버전 비권장)


2. 필요한 라이브러리 설치
```sh
pip install paddlepaddle #for gpu cuda acceleration paddlepaddle-gpu

pip install paddleocr

pip install opencv-python
```

3. PaddleOCR 옵션 조정
```py
# PaddleOCR 호출 및 옵션 설정(cuda 가속 여부, 언어, inference모델)
ocr = PaddleOCR(
    use_gpu=True, 
    gpu_id=0, 
    use_angle_cls=True, 
    lang="en")
```

### 1) test/recv_ocr.py
  - socket 통신을 사용하여 전송받은 이미지를 PaddleOCR 적용
  - 최종적으로 나온 차량위치(층수, 구역)를 다시 User(클라이언트)에게 전송

  #### 사용법
  1. 서버 포트 번호 수정
```py
port = 8080 # example
```
  2. User(클라이언트) ip 수정
```py
sock2.connect(('10.10.141.22', 6001)) # 연결할 클라이언트의 ip주소와 포트번호를 입력
```
  3. 이미지 크기 수정(비율은 맞추면서 바꿀것)
```py
# 이미지 크기(영상 비율 유지)
width = 800
height = 450
```

### 2) test2/video_recv.py
  - ZeroMQ를 사용하여 클라이언트로부터 전송된 이미지를 화면에 표시

### 3) test3/video_play.py
  - 로컬에 있는 영상으로 PaddleOCR을 적용
  - 통신에 대한 코드가 없음

  #### 사용법
  1. 영상 경로 수정
```py
file_path = 'D:/intel2_firmware/GitHub/video_sample/lotte_outlet.avi'
```

### 4) test4/test4.py
  - socket 통신을 사용하여 클라이언트로부터 전송된 이미지를 화면에 표시


### 5) test_openvino/paddle_openvino.py(미구현)
  - Openvino를 사용한 PaddleOCR 구동
  - 아직 오류가 있어 수정 필요


## 2. 라즈베리파이 클라이언트
### 1) client_img_ver2.py
  - ZeroMQ를 사용한 클라이언트-서버 통신
  - 비동기 메세징 통신으로 PUB&SUB / REQ&REP 2가지 통신 방법

#### ZeroMQ 적용 방법
```sh
pip install pyzmq
```


### 2) client_img_ver3.py
  - socket 통신을 사용한 클라이언트-서버 통신
  - 이미지 전송을 위해 UDP로 구현


## 3. 통신 테스트 폴더

### 1) server1.py
  - 서버에서 다른 클라이언트와의 연결
#### User(server) ip 수정
```py
 # 소켓에 IP 주소와 포트 번호를 바인드합니다.
    server_socket.bind(('10.10.141.22', 6001))
```
```py
data_A = client_socket.recv(1024) #buffer크기 수정
``` 
### 2) TCP client.py
  - client로 부터 메세지를 보내는 코드

#### Twilio 적용방법
```sh
pip install twilio
```
#### User(클라이언트) ip 수정
```py
data = (f'차량의 위치는 none층 none구역입니다.')# none에 측정한 값 대입
sock2.connect(('10.10.141.22', 6001)) # 접속할 서버의 ip주소와 포트번호를 입력.
```
#### User(Twilio) 정보 수정
```py
account_sid = 'AC830601052a526b757f23cac741e8becb'
    auth_token = '' #보안 이슈로 나중에 입력
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='+12563685788',
        body=data.encode(),
        to='+821031198106'
    )
```
