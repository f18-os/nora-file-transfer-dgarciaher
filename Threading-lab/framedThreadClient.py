#! /usr/bin/env python3

# Echo client program
import socket, sys, re
import params
from framedSock import FramedStreamSock
from threading import Thread
import time


print( "would you like to use stammer proxy or file server?" )

choice = input()

if (choice == "stammer proxy")  :        # picks stammer proxy or file server depending on user input
    ipAd = "localhost:50000"
elif (choice == "file server")  :
    ipAd = "localhost:50001"


switchesVarDefaults = (
    (('-s', '--server'), 'server', ipAd),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
)


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

class ClientThread(Thread):
    def __init__(self, serverHost, serverPort, debug):
        Thread.__init__(self, daemon=False)
        self.serverHost, self.serverPort, self.debug = serverHost, serverPort, debug
        self.start()
    def run(self):    # tells thread what to run by overriding run
       s = None
       for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
           af, socktype, proto, canonname, sa = res
           try:
               print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
               s = socket.socket(af, socktype, proto)
           except socket.error as msg:
               print(" error: %s" % msg)
               s = None
               continue
           try:
               print(" attempting to connect to %s" % repr(sa))
               s.connect(sa)
           except socket.error as msg:
               print(" error: %s" % msg)
               s.close()
               s = None
               continue
           break

       if s is None:
           print('could not open socket')
           sys.exit(1)

       fs = FramedStreamSock(s, debug=debug)  # makes an obj to handle sending & receiving messages

       print("Enter file name: ")
       fileName = input() 

       try:
            oFile =open(fileName, "rb")
            data= oFile.read()

            fs.sendmsg(fileName.encode())

            i=0;
            while i<= len(data):
              str = data[i:i+100]
              fs.sendmsg(str)
              i+=100

            fs.sendmsg(b"%%e")

       except (FileNotFoundError):
            print("ur file ain't here")

ClientThread(serverHost, serverPort, debug)