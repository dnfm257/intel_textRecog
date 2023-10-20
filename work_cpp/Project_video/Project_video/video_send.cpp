#include <opencv2/opencv.hpp>
#include <zmq.hpp>

int main() {
    try {
        zmq::context_t context(1);
        zmq::socket_t socket(context, ZMQ_REP); // open socket REP&REQ mode
        socket.bind("tcp://*:8081"); // port 번호

        while (true) {
            zmq::message_t message;
            socket.recv(message, zmq::recv_flags::none); // 받은 메세지(이미지)

            // byte형식으로 받은 데이터 저장
            std::vector<uchar> data(message.size());
            memcpy(data.data(), message.data(), message.size());

            cv::Mat decodedImage = cv::imdecode(cv::Mat(data), cv::IMREAD_COLOR); // byte -> img decoding

            std::string reply_msg; // 클라이언트에 보낼 답장
            if (!decodedImage.empty()) {
                cv::imshow("Received from Raspberry Pi", decodedImage);

                // OCR부분

                reply_msg = "Processed Img";
            }
            else {
                reply_msg = "Received Empty Img";
            }

            cv::waitKey(10); // REP&REQ 프로토콜을 위한 딜레이(중요!)

            // 이미지 수신 확인 응답
            zmq::message_t reply(reply_msg);
            memcpy(reply.data(), reply_msg.c_str(), reply_msg.size());
            socket.send(reply, zmq::send_flags::none);
        }
    }
    // 에러가 발생할 경우 catch
    catch (zmq::error_t& e) {
        std::cerr << "ZeroMQ Error: " << e.what() << std::endl;
    }
    catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }
    
    return 0;
}