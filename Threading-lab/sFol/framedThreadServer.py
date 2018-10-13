#! /usr/bin/env python3
import sys, os, socket
import params, time
from threading import Thread
from framedSock import FramedStreamSock

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()

lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
bindAddr = ("127.0.0.1", listenPort)
lsock.bind(bindAddr)
lsock.listen(5)
print("listening on:", bindAddr)

class ServerThread(Thread):
    requestCount = 0            # one instance / class
    def __init__(self, sock, debug):
        Thread.__init__(self, daemon=True)
        self.fsock, self.debug = FramedStreamSock(sock, debug), debug
        self.start()
    def run(self):
        try:
            msg = self.fsock.receivemsg()

            msg = msg.decode()

            oFile = open(msg,"wb+")

            while True:
                msg = self.fsock.receivemsg()

                if not msg:
                    if self.debug: print(self.fsock, "server thread done")
                    return
                if b'%%e' in msg:
                    oFile.close()
                    return

                oFile.write(msg)
                self.fsock.sendmsg(msg)
        except (TypeError) :
            sys.exit(1)


        # while True:
        #     msg = self.fsock.receivemsg()
        #     if not msg:
        #         if self.debug: print(self.fsock, "server thread done")
        #         return
        #     requestNum = ServerThread.requestCount
        #     time.sleep(0.001)
        #     ServerThread.requestCount = requestNum + 1
        #     msg = ("%s! (%d)" % (msg, requestNum)).encode()
        #     self.fsock.sendmsg(msg)


while True:
    sock, addr = lsock.accept()
    ServerThread(sock, debug)