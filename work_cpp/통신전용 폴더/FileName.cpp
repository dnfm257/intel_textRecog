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
SOCKET ServSock = INVALID_SOCKET, ClntSock = INVALID_SOCKET;
WSADATA wsaData;
int iResult;
SOCKADDR_IN servAddr, clntAddr;
int szClntAddr, szservAddr;
std::string reply_msg;
int str_len;
zmq::message_t message;
void LDplayer(void);
int main() 
{
    try {
    
        zmq::context_t context(1);
        zmq::socket_t socket(context, ZMQ_REP);
        socket.bind("tcp://*:5000");
        while (true)
        {
            socket.recv(message, zmq::recv_flags::none);

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
            }
            printf("adsa2\n");
            cv::waitKey(10);
            std::cout << "1" << std::endl;

            // 이미지 수신 확인을 위해 응답을 보냅니다.
            zmq::message_t reply(reply_msg);
            memcpy(reply.data(), reply_msg.c_str(), reply_msg.size());
            socket.send(reply, zmq::send_flags::none);
            printf("adsadsa3\n");
            char key = (char)cv::waitKey(30);
            if (key == 'q' || key == 27)
            {
                break;
            }
        }
        atexit(LDplayer); //종료시 송신하는 함수
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

void LDplayer(void)
{
    while (1)
    {
        const char* cstr = reply_msg.c_str(); // str을 보내면 char형으로 변환
        int len = reply_msg.length(); // 문자열의 길이 가져오기   
        iResult = WSAStartup(MAKEWORD(2, 2), &wsaData);
        ServSock = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
        memset(&servAddr, 0, sizeof(servAddr));
        servAddr.sin_family = AF_INET; // address family Internet
        servAddr.sin_port = htons(5001); //Port to connect on
        inet_pton(AF_INET, "10.10.141.22", &servAddr.sin_addr);
        bind(ServSock, (SOCKADDR*)&servAddr, sizeof(servAddr));
        listen(ServSock, 5);
        szClntAddr = sizeof(clntAddr);
        ClntSock = accept(ServSock, (SOCKADDR*)&clntAddr, &szClntAddr);
        send(ClntSock, cstr, len, 0);
        //closesocket(ClntSock);
        //closesocket하면 LDpalyer에서 수신 후 바로 종료 사진 촬영등이 필요하면 넣지 말 것
    }
}
