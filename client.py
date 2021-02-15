import socket
import threading
import sys
import numpy as np
import pickle
import security
from security import encoding_dict,Key_Dim,Key



PORT = 8000
HEADER = 64
FORMAT = "utf-8"
SERVER = "127.0.0.2"
DISCONNECT_MESSAGE="!DISCONNECT"

def print_cmd(comment):
    print("\033[96m {}\033[00m".format(comment))


###*******CLIENT CLASS*****###
class Client:
    def __init__(self, server_ip, port):
        self.SERVER_IP = server_ip                              #server's ip to connect to
        self.PORT = port										#server's port to connect to 							
        self.ADDR=(self.SERVER_IP,self.PORT)  							#tuple of server ip and server address      
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)    #socket object on client side
        self.client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
       




    def connectToServer(self):
        try:
            self.client.connect((self.ADDR))                      #establish connection with server on address ADDR=SERVER_IP,SERVER_PORT

        except socket.error as e:
            self.print_error(str(e))
            sys.exit()
     
        
    def print_error(self,comment):
        print("\033[91m {}\033[00m".format(comment))
        print()
    
    def print_msg(self,comment):
        print("\033[93m {}\033[00m".format(comment))
        print()

        

    def pad_msg(self,msg, size):
        while (len(msg))% size != 0:
            msg+=' '
        return msg
 
    def encrypt(self,plain_text,key_dimension):

            if(len(plain_text))%key_dimension != 0:
                plain_text = self.pad_msg(plain_text, key_dimension)

            # print("pl ", plain_text)
            encoded_plain_txt=[]
            for i in plain_text:
                if i == " " :
                    encoded_plain_txt.append(27)
                else :
                    encoded_plain_txt.append(encoding_dict[i])

                
            # print(encoded_plain_txt)
            encoded_plain_txt = np.array(encoded_plain_txt)
            encoded_matrix = encoded_plain_txt.reshape(int(len(plain_text)/key_dimension),key_dimension)
            cipher_matrix = np.dot(security.Key,np.transpose(encoded_matrix))
            return cipher_matrix


    def recieve_message(self):
        msg=""
        msg_length=self.client.recv(HEADER).decode(FORMAT)   #get length of  msg to receive by using initial HEADER size of header=64B
        if msg_length :
            msg_length=int(msg_length)                      #convert length to int as it was received in utf-8 format
            msg=self.client.recv(msg_length).decode(FORMAT)  #reset HEADER size to received msg length size and receive msg
        return msg

    def send(self,message) :
        
        # print(" message " ,message)
       
        msg_length = len(message)
        # print(msg_length)
        send_length = str(msg_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        lock =threading.Lock()
        lock.acquire()
        self.client.send(send_length)
        self.client.send(message)
        lock.release()
        
   
def main():
    client =Client(SERVER,PORT)
    client.connectToServer()
    print_cmd("Enter plain text: ")
    plain_text=str(input()).upper()
    print("Plain text ",plain_text)
    crc=security.generateCRC(plain_text)
    # print("CRC ",crc)
    # print(type(crc))
    # print(" security .key_dimension ",security.Key_Dim)
    cipher_matrix=client.encrypt(plain_text,Key_Dim)
    print(cipher_matrix)
    # print(crc)
    message = pickle.dumps([cipher_matrix,str(crc)])
    client.send(message)
main()