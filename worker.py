import socket
import json
from threading import Thread
import time

class Worker:
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
		self.s.sendall(b'w')

		try:
			self.mandaCositas()
		except KeyboardInterrupt:
			self.noExit = False
			self.s.sendall(b'exit')
			self.s.close()

	def mandaCositas(self):
		while self.noExit:

			self.s.sendall(b'ready')
			data = json.loads((self.s.recv(1024)).decode())
			self.trabajito = data


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
			self.s.sendall(b'done')
			self.s.sendall(json.dumps(result).encode())