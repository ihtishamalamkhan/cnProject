from socket import *
from sys import *
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
            
            
            
def connectionEstablishment
    
if __name__ == '__main__':
    parseArguments(argv)
    connectionEstablishement()

    
