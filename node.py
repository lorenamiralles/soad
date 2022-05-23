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
		self.s.send(b'w')

		thread = Thread(target=dispatch_connection, args=((self, "receive"),))
		thread.start()
		thread2 = Thread(target=dispatch_connection, args=((self, "send"),))
		thread2.start()
		try:
			self.trabajaLeches()
		except KeyboardInterrupt:
			self.noExit = False
			self.s.send(b'exit')
			self.s.close()
			thread.join()
			thread2.join()

	def trabajaLeches(self):
		while self.noExit:
			if self.trabajito != None:
				# DO trabajito
				a = self.trabajito.get("chunk_a")
				b = self.trabajito.get("chunk_b")
				c_i = self.trabajito.get("c_i")
				c_j = self.trabajito.get("c_j")

				suma = 0

				for i in range(len(a)):
					suma += a[c_i][i] * b[i][c_j]
				
				result = {"matrix_id": self.trabajito.get("matrix_id"),
						  "chunk_c": suma,
						  "c_i": c_i,
						  "c_j": c_j,
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
				self.s.sendall(b'ready')
			if self.result != None:
				self.s.sendall(b'done')
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


