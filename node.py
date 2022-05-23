import socket
import json
from threading import Thread

from matplotlib.font_manager import json_dump

class Client:
	def __init__(self, server_ip, server_port, node_port):
		self.server_ip = server_ip
		self.node_port = node_port
		self.server_port = server_port

		self.trabajito = None
		self.result = None
		
		self.s = None

		self.noExit = True

	def connect(self):
		
		self.s = socket.socket()  # Create a socket object
		self.s.connect((self.server_ip, self.server_port))  # Bind to the port
		self.s.send(b'n')

		thread = Thread(target=dispatch_connection, args=((self, "receive"),))
		thread.start()
		thread2 = Thread(target=dispatch_connection, args=((self, "send"),))
		thread2.start()

		self.trabajaLeches()

		thread.join()
		thread2.join()


	def trabajaLeches(self):

		while self.noExit:
			if self.trabajito != None:
				# DO trabajito
				a = self.trabajito.get("chunk_a")
				b = self.trabajito.get("chunk_b")
				ci = self.trabajito.get("c_i")
				cj = self.trabajito.get("c_j")

				suma = 0

				for i in range(len(a)):
					suma += a[ci][i] * b[i][cj]
				
				result = {"matrix_id": self.trabajito.get("matrix_id"),
						  "chunk_c": suma,
						  "c_i": ci,
						  "c_j": cj,
						  }
				
				self.result = result
				self.trabajito = None

	def receiveCositas(self):
		while self.noExit:
			data = json.loads((self.s.recv(1024)).decode())
			if data == b'exit':
				self.noExit = False
				self.s.close()
			else:
				self.trabajito = data

	def mandaCositas(self):
		while self.noExit:
			if self.trabajito == None:
				self.s.sendall(b'w')
				self.s.sendall(b'ready')
				self.s.sendall(b'w')
			if self.result != None:
				self.s.sendall(json.dumps(self.result).encode())
				self.result = None


def dispatch_connection(arg):
	node = arg[0]
	tipo = arg[1]
	if tipo == "receive":
		node.receiveCositas()
	elif tipo == "send":
		node.mandaCositas()
	else: 
		print("Error")


