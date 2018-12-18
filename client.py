from socket import *
from sys import *
from select import*

resumeFlag=False
numberOfConnections=None
intervalMetricReport=None
connectionType=None
fileAddress=None
outputLocation=None

def parseArguments(argv):
    for i in range(len(argv)):
        if argv[i]=="-r":
            global resumeFlag
            resumeFlag=True
            print("there is -r in arguments")
        if argv[i]=="-n":
            global numberOfConnections
            numberOfConnections=int(argv[i+1])
            print ("num connections are: ", numberOfConnections)
        if argv[i]=="-i":
            global intervalMetricReport
            intervalMetricReport= float(argv[i+1])
            print ("Time interval between metric reporting is: " , intervalMetricReport)
        if argv[i]=="-c":
            global connectionType
            connectionType= argv[i+1]
            print("The connection type is : "+connectionType)
        if argv[i]=="-f":
            global fileAddress
            fileAddress=argv[i+1]
            print("The file location is: "+fileAddress)
        if argv[i]=="-o":
            global outputLocation
            outputLocation=argv[i+1]
            print("This is location on client where file is downloaded: "+outputLocation)

def TCP_connection(fileAddress):
    serverPort = 80
    string = fileAddress
    split1 = string.split('//')
    string1 = split1[1]
    split2 = string1.split('/')
    split3 = split2[1].split('.')
    domain = split2[0]
    file = split3[0]
    ext = split3[1]
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((domain, 80))
    output = 'GET /%s.%s HTTP/1.0\r\n\r\n' % (file,ext)
    s.sendall(output.encode())
    reply = b''

    while True:
        data = s.recv(2048)
        if not data: break
        reply += data

    headers = reply.split(b'\r\n\r\n')[0]
    image = reply[len(headers) + 4:]

    # save image
    f = open('%s.%s' % (file, ext), 'wb')
    f.write(image)
    f.close()

    s.close()


if __name__ == '__main__':
    parseArguments(argv)
    TCP_connection(fileAddress)
