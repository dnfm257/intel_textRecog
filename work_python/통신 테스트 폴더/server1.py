import socket
y=0 # flag

# TCP/IP 소켓을 생성합니다.
while(1):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # 소켓에 IP 주소와 포트 번호를 바인드합니다.
    server_socket.bind(('10.10.141.22', 6001))
    print("bind\n")
    # 클라이언트로부터의 연결을 기다립니다.
    server_socket.listen(2)

    print('클라이언트로부터의 연결을 기다리는 중...')

    # 클라이언트로부터 연결 요청이 오면 수락합니다.
    client_socket, addr = server_socket.accept()

    print('클라이언트가 연결되었습니다:', addr)

    # 클라이언트로부터 메시지를 받아 출력합니다.
    data_A = client_socket.recv(1024)

    print('받은 데이터:', data_A.decode())
    # 소켓을 닫습니다.
    client_socket.close()
    server_socket.close()
   
