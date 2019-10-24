#include "UDP.h"

#include <sys/types.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <memory.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <errno.h>
#include <stdlib.h>
#include <iostream>
#include <fstream>
#include <algorithm> 


int resolvehelper(const char* hostname, int family, const char* service, sockaddr_storage* pAddr)
{
    int result;
    addrinfo* result_list = NULL;
    addrinfo hints = {};
    hints.ai_family = family;
    hints.ai_socktype = SOCK_DGRAM; // without this flag, getaddrinfo will return 3x the number of addresses (one for each socket type).
    result = getaddrinfo(hostname, service, &hints, &result_list);
    if (result == 0) {
        memcpy(pAddr, result_list->ai_addr, result_list->ai_addrlen);
        freeaddrinfo(result_list);
    }

    return result;
}

UDP::UDP(std::string host, std::string port) {
    this->host = host;
    this->port = port;
    this->sock = socket(AF_INET, SOCK_DGRAM, 0);

    int result = 0;

    char szIP[100];

    sockaddr_in addrListen = {}; // zero-int, sin_port is 0, which picks a random port for bind.
    addrListen.sin_family = AF_INET;
    result = bind(sock, (sockaddr*)&addrListen, sizeof(addrListen));
    if (result == -1)
    {
       int lasterror = errno;
       std::cout << "bind error: " << lasterror;
    }
    result = resolvehelper(host.c_str(), AF_INET, port.c_str(), &addrDest);
    if (result != 0)
    {
       int lasterror = errno;
       std::cout << "resolve error: " << lasterror;
    }
    struct timeval tv;
    tv.tv_sec = 1;
    tv.tv_usec = 100000;
    if (setsockopt(this->sock, SOL_SOCKET, SO_SNDTIMEO ,&tv,sizeof(tv)) < 0) {
        std::cout << "set timeout error: \n";
    }
}

void UDP::send(Kinect::FrameBuffer frameBuffer) {
    float* data = frameBuffer.getData<float>();
    std::ofstream myfile("height.dat", std::ios::out | std::ios::binary);
    myfile.write((char*)data, 640 * 480 * 4);
    myfile.close();
    // char const * p = reinterpret_cast<char const *>(data);
    // float a = 0;
    // int totalSize = frameBuffer.getSize(0) * frameBuffer.getSize(1) * sizeof(a);
    // std::cout << "Sending " << totalSize << " bytes\n";
    // int packetSize = 1200;
    // for (int offset = 0; offset < totalSize; offset += packetSize) {
    //     int actualPacketSize = std::min(totalSize - offset, packetSize);
    //     int result = sendto(this->sock, data + offset, actualPacketSize, 0, (sockaddr*)&addrDest, sizeof(addrDest));
    //     if (result != 0)
    //     {
    //     int lasterror = errno;
    //     std::cout << "send error: " << lasterror << " offset " << offset << "\n";
    //     }
    // }
    // int result = sendto(this->sock, data, size, 0, (sockaddr*)&addrDest, sizeof(addrDest));
    // if (result != 0)
    // {
    //    int lasterror = errno;
    //    std::cout << "send error: " << lasterror;
    // }
}