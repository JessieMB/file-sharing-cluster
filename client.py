'''
Script for client side
@author: hao
'''
from tqdm import tqdm, trange
from time import sleep
import protocol
import config
from socket import *
import os
from os.path import isfile, join


class client:
    
    fileList=[] # list to store the file information
    uploadList=[] # list to store uploadable files
    #Constructor: load client configuration from config file
    def __init__(self):
        self.serverName, self.serverPort, self.clientPort, self.downloadPath, self.uploadPath = config.config().readClientConfig()

    # Function to produce user menu 
    def printMenu(self):
        print("--------------------------------------")        
        print("Welcome to S L I M E W I R E!")
        print("Please select operations from menu")
        print("--------------------------------------")
        print("1. Files Currently on Server")
        print("2. Download File From Server")
        print("3. Message Server")       
        print("4. Upload File to Server")                
        print("5. Quit")

    # Function to get user selection from the menu
    def getUserSelection(self):       
        ans=0
        # only accept option 1-5
        while ans>5 or ans<1:
            self.printMenu()
            try:
                ans=int(input())
            except:
                ans=0
            if (ans<=5) and (ans>=1):
                return ans
            print("Invalid Option")

    # Build connection to server
    def connect(self):
        serverName = self.serverName
        print(serverName)
        serverPort = self.serverPort
        print(serverPort)
        clientSocket = socket(AF_INET, SOCK_STREAM)
        print(clientSocket)
        clientSocket.connect((serverName,serverPort))
        return clientSocket

    # Get file list from server by sending the request
    def getFileList(self):
        mySocket=self.connect()
        mySocket.send(protocol.prepareMsg(protocol.HEAD_REQUEST," "))
        header, msg=protocol.decodeMsg(mySocket.recv(1024).decode())
        mySocket.close()
        if(header==protocol.HEAD_LIST): 
            files=msg.split(",")
            self.fileList=[]
            for f in files:
                self.fileList.append(f)
        else:
            print ("Error: cannot get file list!")

    def getUploadableFileList(self):
        mySocket=self.connect()
        mySocket.send(protocol.prepareMsg(protocol.HEAD_REQUEST," "))
        header, msg=protocol.decodeMsg(mySocket.recv(1024).decode())
        mySocket.close()
        filesInUploadList = [f for f in os.listdir(self.uploadPath) if isfile(join(self.uploadPath, f))]
        self.uploadList=[]        
        for f in filesInUploadList:
            self.uploadList.append(f)
        
        #if(header==protocol.HEAD_LIST): 
            #files=msg.split(",")
            #self.uploadList=[]
            #for f in files:
                #self.uploadList.append(f)
        #else:
            #print ("Error: cannot get file list!")

    # function to print files in the list with the file number
    def printFileList(self):
        count=0
        for f in self.fileList:
            count+=1
            print('{:<3d}{}'.format(count,f))
    
    # function to print uploadable files from client
    
    def printUploadableFileList(self):
        count=0
        upload_list = self.getUploadableFileList()
        for f in self.uploadList:
            count+=1
            print('{:<3d}{}'.format(count,f))    

    # Function to select the file from file list by file number,
    # return the file name user selected
    def selectDownloadFile(self):
        if(len(self.fileList)==0):
            self.getFileList()
        ans=-1
        while ans<0 or ans>len(self.fileList)+1:
            self.printFileList()
            print("Please select the file you want to download from the list (enter the number for file):")
            try:
                ans=int(input())
            except:
                ans=-1
            if (ans>0) and (ans<len(self.fileList)+1):
                return self.fileList[ans-1]
            print("Invalid number")

    def selectUploadFile(self):
        if(len(self.uploadList)==0):
            self.getUploadableFileList()
        ans=-1
        while ans<0 or ans>len(self.uploadList)+1:
            self.printUploadableFileList()
            print("Please select the file you want to upload from the list (enter the number for file):")
            try:
                ans=int(input())
            except:
                ans=-1
            if (ans>0) and (ans<len(self.uploadList)+1):
                return self.uploadList[ans-1]
            print("Invalid number")

    def getClientFileList(self):
        print(os.listdir(self.uploadPath))
        return os.listdir(self.uploadPath)
    
    def uploadFile(self,fileName):
        mySocket=self.connect()
        mySocket.send(protocol.prepareMsg(protocol.HEAD_UPLOAD, fileName))
        with open(self.uploadPath+"/"+fileName, 'wb') as f:
            print ('file opened')
            while True:
                #print('uploading data...')
                bar = trange(1)                
                data = mySocket.recv(1024)
                for i in bar:
                    sleep(0.5)
                    if not (i):
                        tqdm.write("Uploading file %s" % fileName)                
                #print('data=%s', (data))
                if not data:
                    break
            # write data to a file
                f.write(data)
        print(fileName+" has been uploaded!")
        mySocket.close()
        
    
    # Function to send download request to server and wait for file data
    
    def downloadFile(self,fileName):
        mySocket=self.connect()
        mySocket.send(protocol.prepareMsg(protocol.HEAD_DOWNLOAD, fileName))
        with open(self.downloadPath+"/"+fileName, 'wb') as f:
            print ('file opened')
            while True:
                #print('receiving data...')
                bar = trange(1)
                data = mySocket.recv(1024)
                for i in bar:
                    sleep(0.5)
                    if not (i):
                        tqdm.write("Downloading file %s" % fileName)
                #print('data=%s', (data))
                if not data:
                    break
            # write data to a file
                f.write(data)
        print(fileName+" has been downloaded!")
        mySocket.close()
        
    def chatWithServer(self):
        mySocket=self.connect()
        sentence = input('Send message to server:')        
        mySocket.send(protocol.prepareMsg(protocol.HEAD_CHAT, sentence))        
        mySocket.send(sentence.encode())
        modifiedSentence = mySocket.recv(1024)
        print('From Server: ' + modifiedSentence.decode())
        mySocket.close()
        # Main logic of the clien, start the client application
        
    def start(self):
        opt=0
        while opt!=5:
            opt=self.getUserSelection()
            if opt==1:
                if(len(self.fileList)==0):
                    self.getFileList()
                self.printFileList()                  
            elif opt==2:
                self.downloadFile(self.selectDownloadFile())
            elif opt==3:
                self.chatWithServer()
            elif opt==4:
                self.uploadFile(self.selectUploadFile())
            else:
                pass
                
def main():
    c=client()
    c.start()
main()
