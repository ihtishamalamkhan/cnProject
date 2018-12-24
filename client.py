from socket import *
from sys import *
from time import *
from threading import*
from pathlib import Path
import os
from main import *

#URL downloads for demo
#http://techslides.com/demos/sample-videos/small.mp4
#https://www.gstatic.com/webp/gallery/1.jpg

resumeFlag = False
numberOfConnections = None
intervalMetricReport = None
connectionType = None
fileAddress = None
outputLocation = None
def parseArguments(argv):
    '''This function takes command line arguments and assigns each meaningful argument to a variable which are used later'''
    for i in range(len(argv)):
        

        if argv[i] == "-r":
            global resumeFlag
            resumeFlag = True
            print("there is -r in arguments")
        if argv[i] == "-n":
            global numberOfConnections
            numberOfConnections = int(argv[i + 1])
            print("num connections are: ", numberOfConnections)
        if argv[i] == "-i":
            global intervalMetricReport
            intervalMetricReport = float(argv[i + 1])
            print("Time interval between metric reporting is: ", intervalMetricReport)
        if argv[i] == "-c":
            global connectionType
            connectionType = argv[i + 1]
            print("The connection type is : " + connectionType)
        if argv[i] == "-f":
            global fileAddress
            fileAddress = argv[i + 1]
            print("The file location is: " + fileAddress)
        if argv[i] == "-o":
            global outputLocation
            outputLocation = argv[i + 1]
            if outputLocation==".":
                print("The file will be downloaded in the same folder as client.py")
            else:
                print("This is location on client where file is downloaded: " + outputLocation)

def TCP_single_connection(fileAddress):
    parseArguments(argv)
    global interval_flag
    interval_flag = True
    resume = False
    contentLength = 0
    timeMain = 0
    time_interval = 0
    headDic = {}
    serverPort = 80

    # split file, fileName and domain
    string = fileAddress
    split1 = string.split('//')
    domain = split1[1].split('/', 1)[0]
    addr = split1[1].split('/', 1)[1]
    fileName = split1[1].rsplit('/', 1)[1]
    print(addr)
    print(fileName)
        

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
            contentLength = int(line.rsplit(':')[1])
            print ("Length of content: ",contentLength)

    
    alreadyDownloaded=0
    data=None
    splitData=None
    file=None

    #if conditions runs when the file is to be stored in the current directory
    if outputLocation=="." :
        checkFile= os.path.isfile(fileName) #check if file already exists

        #if file exists and fileSizeonlocalDisk==sizeOfFileOnServer
        if checkFile and os.path.getsize(fileName)== int(contentLength): 
            print( "This File already exists")
            return

        #else if file exists and user wants to resume last download for the file and the file is allowed to be resumed  and file has not been completely downloaded
        elif checkFile and resumeFlag==True and resume==True and os.path.getsize(fileName) < int(contentLength): 
            print ("File was resumed")
            alreadyDownloaded=os.path.getsize(fileName)
            f = open('%s' % (fileName), 'ab+')

        #else if file exists and one of the two flags is false (meaning resume not enabled) and file has not been completely downloaded yet
        #here I have restarted the file download and overwritten the last download, since resuming is not allowed
        elif checkFile and (resumeFlag==False or resume==False) and os.path.getsize(fileName) < int(contentLength):
            print ("This is length of already downloaded file: ", os.path.getsize(fileName)," And the total fileLength is ", int(contentLength))
            f = open('%s' % (fileName), 'ab+')
            f.seek(0) #means cursor at beginning, it will rewrite the already written file

        #else if file does not exist then open file for append
        elif (not checkFile):
            f = open('%s' % (fileName), 'ab+')
            f.seek(0)
            
    #these are all same conditions as above, this will run for when the user wants to save the file in a different location        
    else:
        fileLocation=outputLocation+"/"+fileName
        checkFile=os.path.isfile(fileLocation)
        if checkFile and os.path.getsize(fileLocation)==int(contentLength):
            print ("This File already exists")
            return
        elif checkFile and resumeFlag==True and resume==True and os.path.getsize(fileLocation) < int(contentLength):
            alreadyDownloaded=os.path.getsize(fileLocation)
            f = open(outputLocation+"/"+fileName, 'ab+')
        elif checkFile and (resumeFlag==False or resume==False) and os.path.getsize(fileLocation) < int(contentLength):
            print ("This is length of already downloaded file: ", os.path.getsize(fileLocation)," And the total fileLength is ", int(contentLength))
            f = open(outputLocation+"/"+fileName, 'ab+')
            f.seek(0)
        elif (not checkFile):
            f = open(outputLocation+"/"+fileName, 'ab+')
            f.seek(0)

    #Get request, which also specifies the range of bytes which are to be retrieved
    output = "GET /%s HTTP/1.1\r\nHOST: %s\r\nConnection: close\r\nRange: bytes=%d-\r\n\r\n" % (addr, domain,alreadyDownloaded)
    clientSocket.sendall(output.encode())

    #retrieving data
    data = reply = clientSocket.recv(1024)
    splitData = reply.split(b'\r\n\r\n')[1]
    getHeader = reply.split(b'\r\n\r\n')[0]
    f.write(splitData)
    # receive data in loop and write it in file 
    downloaded = len(splitData)
    start = time()
    thisisfinal()

    #while the file has not completely downloaded, keep receiving from server
    while data:
        data = clientSocket.recv(1024)
        time_spend = (time())-start
        f.write(data)
        
        downloaded += len(data)
        if interval_flag == True and time_spend>0: 
            speed = int((downloaded / 1024) / time_spend)
            percentage = int((downloaded / float(contentLength)) * 100)
            print('%d %% downloaded;    Speed: %d kb/s ' % (percentage, speed), end='\r')
            interval_flag = False
    print("100% downloaded.")

    #connection closed
    clientSocket.close()

def thisisfinal():
    '''This function is used for metric reporting after a specific interval of time, The Timer() function first arguments shows the amount of time after which
       the metric should be displayed and the second argument shows the function which is to be called after that time'''
    global interval_flag
    #thisisfinal() calls itself in recursive manner and we can display metric after specific interval of time
    t = Timer(intervalMetricReport, thisisfinal)
    #timer object's deamon() function is called, as soon as the main thread ends this timer will stop
    t.daemon = True
    t.start()
    interval_flag = True



