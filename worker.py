import socket
import json
from threading import Thread
import time

doDEBUG = True

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

		if doDEBUG:
			print("Connected to server")
		

		self.s.sendall(b'w')
		if doDEBUG:
			print("Sent w")
		try:
			if doDEBUG:
				print("Starting thread")
			self.mandaCositas()
		except KeyboardInterrupt:
			self.noExit = False
			self.s.sendall(b'exit')
			if doDEBUG:
				print("Sent exit")
			self.s.close()
			if doDEBUG:
				print("Closed socket")

	def mandaCositas(self):
		while self.noExit:
			self.s.sendall(b'ready')
			if doDEBUG:
				print("Sent ready")
			data = json.loads((self.s.recv(1024)).decode())
			if doDEBUG:
				print("Received data")
				print(data)
			self.trabajito = data
			if doDEBUG:
				print("Loading data")
			a = self.trabajito.get("chunk_a")
			b = self.trabajito.get("chunk_b")
			c_i = self.trabajito.get("c_i")
			c_j = self.trabajito.get("c_j")

			suma = 0
			print('a: ', a)
			print('b: ', b)
			print('c_i: ', c_i)
			print('c_j: ', c_j)
			for i in range(len(a)):
				suma += a[c_i][i] * b[i][c_j]
			
			result = {"matrix_id": self.trabajito.get("matrix_id"),
						"chunk_c": suma,
						"c_i": c_i,
						"c_j": c_j,
						}
			if doDEBUG:
				print("Computed result")
				print("Result:", suma)
			self.s.sendall(b'done')
			if doDEBUG:
				print("Sent done")
			time.sleep(1)
			self.s.sendall(json.dumps(result).encode())
			if doDEBUG:
				print("Sent result")
			time.sleep(1)