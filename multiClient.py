from time import *
from threading import*
from pathlib import Path
import os
from sys import *
from socket import *
from math import *
class multiThread(Thread): 
    resumeFlag = False
    numberOfConnections = None
    intervalMetricReport = None
    connectionType = None
    fileAddress = None
    outputLocation = None
    argv=None
    rangeMin=0
    interval=0
    contentLength= None
    def __init__(self, argv):
        Thread.__init__(self)
        self.argv=argv

        
    def parseArgumentsM(self,argv):
        '''This function takes command line arguments and assigns each meaningful argument to a variable which are used later'''

        for i in range(len(self.argv)):
            if argv[i] == "-r":
                global resumeFlag
                resumeFlag = True
            if argv[i] == "-n":
                global numberOfConnections
                numberOfConnections = int(argv[i + 1])
            if argv[i] == "-i":
                global intervalMetricReport
                intervalMetricReport = float(argv[i + 1])
                
            if argv[i] == "-c":
                global connectionType
                connectionType = argv[i + 1]
                
            if argv[i] == "-f":
                global fileAddress
                fileAddress = argv[i + 1]
                
            if argv[i] == "-o":
                global outputLocation
                outputLocation = argv[i + 1]
                if outputLocation==".":
                    print("The file will be downloaded in the same folder as client.py")
                else:
                    print("This is location on client where file is downloaded: " + outputLocation)
    def rangeGet(self):
        '''the function takes to arguments, this function gives the max byte ranges for each thread'''
        self.interval =floor( int(self.contentLength)/numberOfConnections)
        self.rangeMax=int(self.getName())*self.interval
        
    def run(self):
        self.parseArgumentsM(argv)
        rangeMax=0
        resume = False
        contentLength = 0
        timeMain = 0
        time_interval = 0
        serverPort = 80
        global interval_flag
        interval_flag=True
        interval_flag=[interval_flag]*numberOfConnections

        # split file, fileName and domain
        string = fileAddress
        split1 = string.split('//')
        domain = split1[1].split('/', 1)[0]
        addr = split1[1].split('/', 1)[1]
        fileName = split1[1].rsplit('/', 1)[1]
        
            

        # connect to the server
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((domain, serverPort))

        #get Header Query
        headerQuery="HEAD /%s HTTP/1.1\r\nHOST: %s\r\n\r\n" % (addr, domain)
        clientSocket.sendall(headerQuery.encode())

        #headerQuery's reply is translated to utf-8 and split 
        headerReply=clientSocket.recv(1024)
        headerReply=headerReply.decode('utf-8')
        headerReply = headerReply.split('\r\n')
        
        #headerReply is checked if it supports resuming , its length is also extracted
        for line in headerReply:
            if "Accept-Ranges: " in line:
                resume = True
            if "Content-Length:" in line:
                self.contentLength = int(line.rsplit(':')[1])
                
        #the function below gets the max range for each thread
        self.rangeGet()
        #minimum range for the current thread
        self.rangeMin=self.rangeMax-self.interval
        

        #print("Thread: ",self.getName()," rangeMin= ",self.rangeMin," and rangeMax= ",self.rangeMax )

        data=None
        splitData=None

        #Filename and file extension are extracted
        fileThreadName=fileName.split('.')[0] 
        fileExtension=fileName.split('.')[1]
        
        #if conditions runs when the file is to be stored in the current directory
        if outputLocation=="." :
            checkFile= os.path.isfile(fileThreadName+self.getName()+"."+fileExtension) #check if file already exists
            print(checkFile,"This is check File by thread: ", self.getName())
            
            #if file exists and fileSizeonlocalDisk==sizeOfFileOnServer
            if checkFile and os.path.getsize(fileThreadName+self.getName()+"."+fileExtension)== self.rangeMax: 
                print( "This File already exists")
                return

            #else if file exists and user wants to resume last download for the file and the file is allowed to be resumed  and file has not been completely downloaded
            elif checkFile and self.resumeFlag==True and resume==True and os.path.getsize(fileThreadName+self.getName()+"."+fileExtension) < self.rangeMax: 
                print ("File was resumed")
                
                self.rangeMin=os.path.getsize(fileThreadName+self.getName()+"."+fileExtension)+1
                f = open(fileThreadName+self.getName()+"."+fileExtension, 'ab+')
                print("After resume rangeMin is: ",self.rangeMin," And max range is : ",self.rangeMax,"By thread ", self.getName())
                print ("resumed file by thread: ", self.getName())

                
            #else if file exists and one of the two flags is false (meaning resume not enabled) and file has not been completely downloaded yet
            #here I have restarted the file download and overwritten the last download, since resuming is not allowed
            elif checkFile and (self.resumeFlag==False or resume==False) and os.path.getsize(fileThreadName+self.getName()+"."+fileExtension) < self.rangeMax:
                print ("This is length of already downloaded file: ", os.path.getsize(fileThreadName+self.getName()+"."+fileExtension)," And the total fileLength is ", int(contentLength)," Thread: ", self.getName() )
                f = open(fileThreadName+self.getName()+"."+fileExtension, 'ab+')
                f.seek(0) #means cursor at beginning, it will rewrite the already written file
                
            #else if file does not exist then open file for append
            elif (not checkFile):
                print("I was printed by: ", self.getName())
                f = open(fileThreadName+self.getName()+"."+fileExtension, 'ab+')
                f.seek(0)
    
                
        #these are all same conditions as above, this will run for when the user wants to save the file in a different location        
        else:
            fileLocation=outputLocation+"/"+fileThreadName+self.getName()+"."+fileExtension
            checkFile=os.path.isfile(fileLocation)
            if checkFile and os.path.getsize(fileLocation)==int(self.rangeMax):
                print ("This File already exists")
                return
            elif checkFile and self.resumeFlag==True and resume==True and os.path.getsize(fileLocation) < int(self.rangeMax):
                print ("File was resumed")
                rangeMin=os.path.getsize(fileLocation)+1
                print("After resume rangeMin is: ",rangeMin)
                f = open(fileLocation, 'ab')
                print ("resumed file by thread: ", self.getName())
            elif checkFile and (self.resumeFlag==False or resume==False) and os.path.getsize(fileLocation) < int(self.rangeMax) :
                f = open(fileLocation, 'ab+')
                f.seek(0)
            elif (not checkFile):
                f = open(fileLocation, 'ab+')
                f.seek(0)

        #Get request, which also specifies the range of bytes which are to be retrieved

        #GET request for when the thread that started last, this one will retreive data till the last byte
        if int(self.getName())==numberOfConnections:
            print("get wali rangeMin: ", self.rangeMin, "and range mAx ", self.rangeMax)
            output = "GET /%s HTTP/1.1\r\nHOST: %s\r\nConnection: close\r\nRange: bytes=%d-\r\n\r\n" % (addr, domain,self.rangeMin)
        #Get request for rest of the threads
        else:
            print("get wali rangeMin: ", self.rangeMin, "and range mAx ", self.rangeMax)
            output = "GET /%s HTTP/1.1\r\nHOST: %s\r\nConnection: close\r\nRange: bytes=%d-%d\r\n\r\n" % (addr, domain,self.rangeMin,self.rangeMax-1)    
        #sending Get request
        clientSocket.sendall(output.encode())

        
        #retrieving data
        data = reply = clientSocket.recv(1024)
        splitData = reply.split(b'\r\n\r\n')[1]
        getHeader = reply.split(b'\r\n\r\n')[0]
        f.write(splitData)
        # receive data in loop and write it in file
        downloaded = len(splitData)
        start = time()
        self.thisisfinal()

        #while the file has not completely downloaded, keep receiving from server
        while data:
            data = clientSocket.recv(1024)
            f.write(data)
            time_spend = (time())-start
            downloaded += len(data)
            if interval_flag[int(self.getName())-1] == True and time_spend>0: 
                speed = int((downloaded / 1024) / time_spend)
                percentage = int((downloaded / float(self.contentLength)) * 100)
                print('Connection: %s  %d %% downloaded;    Speed: %d kb/s ' % (self.getName(),percentage, speed), end='\r')
                interval_flag[int(self.getName())-1] = False
        print("Connection: ",self.getName(), "100% downloaded.")
        #connection closed
        clientSocket.close()

    def thisisfinal(self):
        '''This function is used for metric reporting after a specific interval of time, The Timer() function first arguments shows the amount of time after which
           the metric should be displayed and the second argument shows the function which is to be called after that time'''
        global interval_flag
        #thisisfinal() calls itself in recursive manner and we can display metric after specific interval of time
        t = Timer(self.intervalMetricReport, self.thisisfinal)
        #timer object's deamon() function is called, as soon as the main thread ends this timer will stop
        threadName=int(self.getName())
        t.daemon = True
        t.start()
        interval_flag[threadName-1] = True
    

