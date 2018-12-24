from client import *
from multiClient import *
import os
def parseArgs(argv):
    for i in range(len(argv)):
        if argv[i] == "-n":
            global numberOfConnections
            numberOfConnections = int(argv[i + 1])
        if argv[i] == "-f":
            global fileAddress
            fileAddress = argv[i + 1]
        if argv[i] == "-o":
            global outputLocation
            outputLocation = argv[i + 1]
def joinFiles():
    fileName=fileAddress.split('/')[-1]
    fileLocation=fileAddress.split('//',1)[-1]
    if outputLocation==".":
        f=open(fileName,"ab+")
        f.seek(0)
        fileNameSplit=fileName.split(".")
        fileName=fileNameSplit[0]
        fileExt=fileNameSplit[1]
        for i in range (1,numberOfConnections+1):
            if os.path.isfile(fileName+str(i)+"."+fileExt):
                ftemp=open(fileName+str(i)+"."+fileExt,"rb")
                data=ftemp.read()
                f.write(data)
                size=os.path.getsize(fileName+str(i)+"."+fileExt)
                print("The file size is: ", size ,"of file",fileName+str(i)+"."+fileExt)
                ftemp.close()
                os.remove(fileName+str(i)+"."+fileExt)  
        f.close()
    else:
        f=open(outputLocation+"/"+fileName,"ab+")
        f.seek(0)
        fileNameSplit=fileName.split(".")
        fileName=fileNameSplit[0]
        fileExt=fileNameSplit[1]
        for i in range (1,numberOfConnections+1):
            if os.path.isfile(outputLocation+"/"+fileName+str(i)+"."+fileExt):
                ftemp=open(outputLocation+"/"+fileName+str(i)+"."+fileExt,"rb")
                data=ftemp.read()
                f.write(data)
                ftemp.close()
                os.remove(outputLocation+"/"+fileName+str(i)+"."+fileExt)
        f.close()
    
    

if __name__ == '__main__':
    threads=[0]
    parseArgs(argv)
    if numberOfConnections==1:
        TCP_single_connection(fileAddress)
    elif numberOfConnections>1:
        for i in range(1,numberOfConnections+1):
            threads.insert(i,multiThread(argv))
            threads[i].setName(i)
            threads[i].start()
        for i in range(1,numberOfConnections+1):
            threads[i].join()
        joinFiles()
