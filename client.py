from socket import *
from sys import *
from time import *
from threading import*

resumeFlag = False
numberOfConnections = None
intervalMetricReport = None
connectionType = None
fileAddress = None
outputLocation = None

interval_flag = None

#URL downloads for demo
#http://techslides.com/demos/sample-videos/small.mp4
#https://www.gstatic.com/webp/gallery/1.jpg

def parseArguments(argv):
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
            print("This is location on client where file is downloaded: " + outputLocation)


def TCP_connection(fileAddress):
    global interval_flag
    interval_flag = True
    resume = False
    cl = 0
    timeMain = 0
    time_interval = 0
    headDic = {}
    serverPort = 80
    # split file, extension and domain
    string = fileAddress
    split1 = string.split('//')
    domain = split1[1].split('/', 1)[0]
    addr = split1[1].split('/', 1)[1]
    fileExt = split1[1].rsplit('/', 1)[1]
    # connect to html or local server
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((domain, serverPort))  # '%s'%(domain) #'10.7.44.132'
    # GET query
    output = "GET /%s HTTP/1.1\r\nHOST: %s\r\nConnection: close\r\n\r\n" % (addr, domain)
    s.sendall(output.encode())
    # retrieve header and split header
    data = reply = s.recv(1024)
    header = reply.split(b'\r\n\r\n')[0]
    print(header)
    # decode header to str
    dHeader = header.decode('utf-8')
    # header
    splitHeader = dHeader.split('\r\n')
    # get image size
    for line in splitHeader:
        if "Accept-Ranges:" in line:
            resume = True
        if "Content-Length:" in line:
            cl = line.split(':')[1]
            break
    splitData = reply.split(b'\r\n\r\n')[1]
    # save image and append image in bytes
    f = open('%s' % (fileExt), 'wb')
    f.close()
    f = open('%s' % (fileExt), 'ab')
    f.write(splitData)
    # receive data in loop and write it in file
    downloaded = len(splitData)
    start = time()
    thisisfinal()
    while data:
        data = s.recv(1024)
        f.write(data)
        time_spend = (time())-start
        downloaded += len(data)
        if interval_flag == True:
            speed = int((downloaded / 1024) / time_spend)
            percentage = int((downloaded / float(cl)) * 100)
            print('%d %% downloaded;    Speed: %d kb/s ' % (percentage, speed), end='\r')
            interval_flag = False
        #print(interval_flag)
        #interval_flag = False

    s.close()

def thisisfinal():
    global interval_flag
    t = Timer(intervalMetricReport, thisisfinal)
    t.daemon = True
    t.start()
    interval_flag = True

    #sleep(intervalMetricReport)


if __name__ == '__main__':
    parseArguments(argv)
    TCP_connection(fileAddress)
