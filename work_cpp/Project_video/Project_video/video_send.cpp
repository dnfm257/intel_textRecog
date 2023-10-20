#include <opencv2/opencv.hpp>
#include <zmq.hpp>

int main() {
    try {
        zmq::context_t context(1);
        zmq::socket_t socket(context, ZMQ_REP); // open socket REP&REQ mode
        socket.bind("tcp://*:8081"); // port ��ȣ

        while (true) {
            zmq::message_t message;
            socket.recv(message, zmq::recv_flags::none); // ���� �޼���(�̹���)

            // byte�������� ���� ������ ����
            std::vector<uchar> data(message.size());
            memcpy(data.data(), message.data(), message.size());

            cv::Mat decodedImage = cv::imdecode(cv::Mat(data), cv::IMREAD_COLOR); // byte -> img decoding

            std::string reply_msg; // Ŭ���̾�Ʈ�� ���� ����
            if (!decodedImage.empty()) {
                cv::imshow("Received from Raspberry Pi", decodedImage);

                // OCR�κ�

                reply_msg = "Processed Img";
            }
            else {
                reply_msg = "Received Empty Img";
            }

            cv::waitKey(10); // REP&REQ ���������� ���� ������(�߿�!)

            // �̹��� ���� Ȯ�� ����
            zmq::message_t reply(reply_msg);
            memcpy(reply.data(), reply_msg.c_str(), reply_msg.size());
            socket.send(reply, zmq::send_flags::none);
        }
    }
    // ������ �߻��� ��� catch
    catch (zmq::error_t& e) {
        std::cerr << "ZeroMQ Error: " << e.what() << std::endl;
    }
    catch (std::exception& e) {
        std::cerr << "Exception: " << e.what() << std::endl;
    }
    
    return 0;
}