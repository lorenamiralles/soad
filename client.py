import socket
import json


class Client:
	def __init__(self, server_ip, server_port, client_port):
		self.server_ip = server_ip
		self.client_port = client_port
		self.server_port = server_port

	def connect(self):
		s = socket.socket()  # Create a socket object
		s.connect((self.server_ip, self.server_port))  # Bind to the port
		s.send(b'c')
		while True:
			msg = input('> ')
			s.send(bytes(msg, 'utf-8'))
			# id = 123
			# a = [[1, 2], [3,4]]
			# b = [[4, 5], [6,7]]
			# data = json.dumps({"id": id, "a": a, "b": b})
			# s.send(data.encode())
