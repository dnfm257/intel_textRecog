#define _WINSOCK_DEPRECATED_NO_WARNINGS
#define _CRT_SECURE_NO_WARNINGS

#include <opencv2/opencv.hpp>
#include <zmq.hpp>
#include <winsock2.h>
#include <iostream>
//#include <tesseract/baseapi.h>
//#include <leptonica/allheaders.h>
#include <sstream>
#include <map>
#include <stdio.h>
#include <stdlib.h>
#include <ws2tcpip.h>

#pragma comment(lib, "ws2_32")
int y = 0, k = 0;// flag용 변수
SOCKET ServSock = INVALID_SOCKET, ClntSock = INVALID_SOCKET; //통신용 socket선언
WSADATA wsaData; //윈도우 소켓함수(필수)
int iResult; //오류확인용 변수
SOCKADDR_IN servAddr, clntAddr; //주소값
int szClntAddr, szservAddr; // 주소의 입력값
std::string reply_msg; //전송확인용 메세지
int str_len; //글자의 길이
zmq::message_t message;
void LDplayer(void); //통신 함수
int main() 
{
    try {
    
        zmq::context_t context(1);
        zmq::socket_t socket(context, ZMQ_REP); //소켓설정
        socket.bind("tcp://*:5000"); //소켓의 ip와 port설정 => ip는 서버이기 때문에 TCP통신을 한다는 것만 표시 
        while (true)
        {
            socket.recv(message, zmq::recv_flags::none); //소켓에서 정보(통신연결확인)를 받아오는 함수

            std::vector<uchar> data(message.size());
            memcpy(data.data(), message.data(), message.size());
           cv::Mat decodedImage = cv::imdecode(cv::Mat(data), cv::IMREAD_COLOR);
           printf("adsadsa\n");
            if (!decodedImage.empty()) {
                cv::imshow("Received from Raspberry Pi", decodedImage);
                // 전처리
               
                reply_msg = "Processed Img";

            }

            else {
                reply_msg = "Received Empty Img";
                break;
            }
            printf("adsa2\n");
            cv::waitKey(10);
            std::cout << "1" << std::endl;

            // 이미지 수신 확인을 위해 응답을 보냅니다.
            zmq::message_t reply(reply_msg);
            memcpy(reply.data(), reply_msg.c_str(), reply_msg.size()); // 통신확인용 socket초기화
            socket.send(reply, zmq::send_flags::none); // 통신확인을 위한 전송함수 이 문구를 지우면 통신이 되지않음
            printf("adsadsa3\n"); // 전송완료 검증용 release 버전에서는 제거 바람
            char key = (char)cv::waitKey(30);
            if (key == 'q' || key == 27)
            {
                break;
            }
        }
        atexit(LDplayer); //종료시 송신하는 함수 단 q로 종료해야지 발동함
            //socket.close();
    }
    catch (zmq::error_t& e) {
        std::cerr << "ZeroMQ Error: " << e.what() << std::endl;
    }
    catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }
    
    return 0;
}

void LDplayer(void) //zmq방식에서는 socket의 중복이 발생할 수 있기 때문에 별도의 socket(ip:10.10.141.22/port:5001)을 제작함
{
    while (1)
    {
        const char* cstr = reply_msg.c_str(); // str을 보내면 char형으로 변환
        int len = reply_msg.length(); // 문자열의 길이 가져오기   
        iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
        ServSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        memset(&servAddr, 0, sizeof(servAddr));
        servAddr.sin_family = AF_INET; // address family Internet
        servAddr.sin_port = htons(5001); //Port
        inet_pton(AF_INET, "10.10.141.22", &servAddr.sin_addr);// ip설정
        bind(ServSock, (SOCKADDR*)&servAddr, sizeof(servAddr)); //socket bind
        listen(ServSock, 5); //연결 갯 수 조정
        szClntAddr = sizeof(clntAddr);
        ClntSock = accept(ServSock, (SOCKADDR*)&clntAddr, &szClntAddr);
        send(ClntSock, cstr, len, 0);
        //closesocket(ClntSock); //closesocket하면 LDpalyer에서 수신 후 바로 종료 사진 촬영등이 필요하면 넣지 말 것
    }
}
