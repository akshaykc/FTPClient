import struct
import sys
headerLen = 8

class segment():
    def __init__(self, seqNo, size, data):
        self.seqNo = seqNo
        self.type = 0
        self.size = size
        self.data = [0 for i in range(0,headerLen+size)]
        self.data[0:4] = bytearray(struct.pack("!I", self.seqNo))
        self.data[4]=self.data[5]=0
        self.data[6]=self.data[7]=85
        for count in range(0,len(data)):
            self.data[headerLen+count]=ord(data[count])
        
    def getData(self):
        return self.data
    
    def getSize(self):
        return len(self.data)
    
    def check(self, data):
        return 0
    
    def getType(self):
        return self.type
        
    def getSeqNo(self):
        return self.seqNo
    
    def getDataSize(self):
        return len(self.data) - headerLen
        
class segmentResponse():
    def __init__(self, data, size):
        self.data = data
        
        self.seqNo = struct.unpack('>I', self.data[0:4])[0]
        
        if self.data[6] == 0x55 and  self.data[7] == 0x55:
            self.type = 0
        elif self.data[6] == 0xAA and  self.data[7] == 0xAA:
            self.type = 1
            
    def getData(self):
        return self.data
    
    def getDataWithoutHeader(self):
        return self.data[headerLen:]
    
    def getSize(self):
        return len(self.data)
    
    def check(self):
        return 0
    
    def getType(self):
        return self.type
        
    def getSeqNo(self):
        return self.seqNo
    
    def getDataSize(self):
        return len(self.data) - headerLen
    
class segmentAck():
    def __init__(self, nextSeqNo, size):
        self.data = [0 for _ in range(size)]
        self.seqNo = nextSeqNo
        self.data[0:4] = bytearray(struct.pack("!I", self.seqNo))
        self.data[4]=self.data[5]=0
        #Assign indicating Ack packet
        self.data[6] = 0xAA
        self.data[7] = 0xAA
        self.checkSum = self.check()
        
    def getData(self):
        return self.data
    
    def getSize(self):
        return len(self.data)
    
    def check(self):
        return 0
    
    def getType(self):
        return self.type
        
    def getSeqNo(self):
        return self.seqNo
    
    def getDataSize(self):
        return len(self.data) - headerLen