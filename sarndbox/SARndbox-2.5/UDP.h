#ifndef UDP_H
#define UDP_H

#include <string>
#include <Kinect/FrameBuffer.h>
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

class UDP {
    public:
    UDP(std::string host, std::string port);
    void send(Kinect::FrameBuffer frameBuffer);

    private:
    std::string host;
    std::string port;
    sockaddr_storage addrDest = {};
    int sock;
};


#endif // UDP_H
