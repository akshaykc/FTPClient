'''
Created on Apr 13, 2016

@author: achaluv
'''
import socket
import threading
import segment
from threading import Timer
import sys

headerLen = 8

bufHead = 0
bufTail = 0
bufferWindow = []
bufSize = 0
timer = []


mutex = threading.Semaphore(1)
empty = threading.Semaphore(0)
item = threading.Semaphore(0)

class udpClient(threading.Thread):
    def __init__(self, hostName, udpServerPort, fileName, WindowSize, MSS):
        threading.Thread.__init__(self)
        global bufSize
        global bufferWindow
        global timer
        self.hostName = hostName
        self.udpServerPort = udpServerPort
        self.fileName = fileName
        self.WindowSize = WindowSize
        self.MSS = MSS
        self.segSize = MSS + headerLen
        
        for i in range(0, self.WindowSize):
            empty.release()
        bufSize = WindowSize
        self.retrasmiTO = 0.5
        bufferWindow = [None for i in range(0,bufSize)]
        timer = [None for i in range(bufSize)]
        
        self.sock = socket.socket(socket.AF_INET, # Internet
                    socket.SOCK_DGRAM) # UDP
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def retransmit(self, index):
        global bufferWindow
        global bufTail
        global timer
        print "Timeout for sequence number ", bufferWindow[index].getSeqNo()
        data = bufferWindow[index].getData()
        dataToSend = bytearray(data)
        self.sock.sendto(dataToSend,(socket.gethostbyname(self.hostName), self.udpServerPort))
        
    class RetransmittingTimer():
        def __init__(self, interval, f, *args):
            self.interval = interval
            self.f = f
            self.args = args
            
        def callback(self):
            self.f(*self.args)
            self.start()

        def cancel(self):
            self.timer.cancel()

        def start(self):
            self.timer = threading.Timer(self.interval, self.callback)
            self.timer.start()
    
    def sendToServer(self, segment):
        global bufferWindow
        global bufTail
        global bufHead
        global bufSize
        global timer
        global empty
        global mutex
        global item
        
        empty.acquire()
        mutex.acquire()
        
        bufferWindow[bufTail] = segment
        dataToSend = bytearray(segment.getData())
        
        self.sock.sendto(dataToSend, (socket.gethostbyname(self.hostName), self.udpServerPort))
        
        #timer[bufTail] = threading.Timer(self.retrasmiTO, self.retransmitTimer, [bufTail])
        #timer[bufTail].start()
        timer[bufTail] = self.RetransmittingTimer(0.2, self.retransmit,bufTail)
        timer[bufTail].start()
        bufTail = (bufTail + 1) % bufSize
        
        mutex.release()
        item.release()
        
    def rdt_send(self):
        slidingWindowProtocol = self.slidingWindow(self.sock)
        slidingWindowProtocol.start()
        seqNo = 0
        count = 0
        data = []
        with open(self.fileName, "rb") as inputFile:
            byte = inputFile.read(1)
            while True:
                if  byte != "":
                    data.append(byte)
                    count = count + 1
                if count == self.MSS or byte == "":
                    segmentToSend = segment.segment(seqNo, count, data)
                    self.sendToServer(segmentToSend)
                    seqNo = seqNo + count
                    count = 0
                    data = []
                    if  byte == "":
                        break
                byte = inputFile.read(1)
        
    def run(self):
        print "Client thread started"
        self.rdt_send()
        
        #print "UDP target IP:", self.hostName
        #print "UDP target port:", self.udpServerPort
        #print "message:", message
        print "Client thread closed"
            
    class slidingWindow(threading.Thread):
        def __init__(self, sock):
            threading.Thread.__init__(self)
            self.runState = True
            self.sock = sock
            
        def run(self):
            while self.runState:
                global bufHead
                global bufferWindow
                data, addr = self.sock.recvfrom(1024)
                data = bytearray(data)
                #print "Received message :", data
                recvdSegment = segment.segmentResponse(data, len(data))
                if recvdSegment.getType() == 1:
                    if recvdSegment.getSeqNo() == bufferWindow[bufHead].getSeqNo() + bufferWindow[bufHead].getDataSize():
                        self.processRcvdSegment(recvdSegment)
                    #elif recvdSegment.getSeqNo() == buffer[self.bufHead].getSeqNo():
        
        def processRcvdSegment(self, segment):
            global bufHead
            global bufSize
            global timer
            global empty
            global mutex
            global item
            item.acquire()
            mutex.acquire()
            
            timer[bufHead].cancel()
            bufHead = (bufHead + 1) % bufSize
            
            mutex.release()
            empty.release()

def main(argv):
    udpClientThread = udpClient(argv[0],int(argv[1]), argv[2], int(argv[3]), int(argv[4]))
    udpClientThread.start()
    
    
if __name__ == "__main__":
    main(sys.argv[1:])
                        