import socket 
import threading
import pickle
import numpy as np
# import security
from security import decoding_dict,Key_Dim,Key_inverse,generateCRC



PORT = 8000

SERVER = "127.0.0.2"
HEADER = 64
# SERVER = socket.gethostbyname(socket.gethostname())
# ADDR = (SERVER,PORT)
FORMAT = "utf-8"

DISCONNECT_MESSAGE="!DISCONNECT"

#server class to handle all server related works
class Server :
	def __init__(self, server_ip, server_port):
		self.IP = server_ip            #ip of server
		self.PORT = server_port		   #port of server
		self.clientConnections = []    #active connection list of clients connected to this server
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)       #creating socket object named server
		self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     #setting socket up
		self.ADDR=(self.IP,self.PORT)  #tuple of server ip and server address
	
	def print_msg(self,comment):
		print("\033[93m {}\033[00m".format(comment))
		print()


	def print_cmd(self,comment):
		print("\033[96m {}\033[00m".format(comment))

	def print_error(self,comment):
		print("\033[91m {}\033[00m".format(comment))
		print()

	def server_start(self):

		try:
			self.server.bind(self.ADDR)             #binding the created socket to server ip and port (ADDR=(IP,PORT))

		except socket.error as e:
			print(str(e))
		self.server.listen(10)
		self.print_cmd(f"[*] Starting server ({self.IP}) on port {self.PORT}")
		while True :                                
			connection,address=self.server.accept()         #accepting client socket, address(ip,port) from client
			thread=threading.Thread(target=self.handle_client,args=(connection,address))
			thread.start()
			print(f"[ACTIVE CONNECTIONS] {threading.activeCount()-1}")

	def handle_client(self,conn,address) :
		self.print_cmd(f"[NEW CONNECTION] {address} connected ")
		lock = threading.Lock()
		lock.acquire()
		rec = self.receive(conn)
		cipher_matrix,crc=pickle.loads(rec)
		crc=int(crc)
		# print("crc",crc)
		lock.release()
		plain_text = self.decrypt(cipher_matrix) 
		# plain_text =plain_text+"error"
		print("Message received:", plain_text)
		crc_rec = generateCRC(plain_text)
		if (crc_rec == crc):
			self.print_msg("Message received without error")
		else:
			self.print_error("Error:Message contains error")
		conn.close()

	def receive(self,cli):
	    msg=""
	    msg_length=cli.recv(HEADER).decode(FORMAT)
	    if msg_length :
	        msg_length=int(msg_length)
	        msg=cli.recv(msg_length)
	        
	    return msg

	def decrypt(self,cipher_matrix):
		# print("cipher_matrix ")
		# print(cipher_matrix)
		key_dimension = Key_Dim
		encoded_mat= np.transpose(np.dot(Key_inverse,cipher_matrix))
		encoded_plain_txt = encoded_mat.reshape(1, cipher_matrix.shape[0]*cipher_matrix.shape[1])
		encoded_plain_txt=encoded_plain_txt[0]
		plain_text=''
		for c in encoded_plain_txt:
			if c == 27:
				plain_text += " "
			else :
				plain_text+=decoding_dict[c]

		return plain_text.rstrip()



def main():
    print("[STARTING] server is starting...")
    server=Server(SERVER,PORT)                               #creating server object and initializing its ip and port
    server.server_start()
    print(f"[LISTENING] Server is listening on {SERVER}")

main()