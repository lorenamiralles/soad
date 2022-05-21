import socket
import json
from threading import Thread


class Server:
	def __init__(self, server_ip, server_port, ):
		self.server_ip = server_ip
		self.server_port = server_port
		self.waiting = []
		self.processing = []
		self.done = []
		self.workers = []

	def listen(self):
		thread_divide = Thread(target=divide_job, args=((self),))
		thread_send = Thread(target=send_job, args=((self),))
		thread_divide.start()
		thread_send.start()

		server_socket = socket.socket()  # Create a socket object
		server_socket.bind((self.server_ip, self.server_port))  # Bind to the port
		server_socket.listen(5)  # Now wait for client connection.
		while True:
			connection, addr = server_socket.accept()  # Establish connection with client.
			print('Got connection from', addr)
			thread_dispatch = Thread(target=dispatch_connection, args=((self, connection),))
			# thread.daemon = False
			thread_dispatch.start()

		# thread_divide.join()

	def client_thread(self, c):
		print('client thread')
		while True:
			res = (c.recv(1024)).decode()
			print(res)
			if res == 'exit':
				print('	client exited')
				return
			elif res == 'job':
				data = json.loads((c.recv(1024)).decode())
				matrix_id = data.get("id")
				matrix_a = data.get("a")
				matrix_b = data.get("b")
				self.waiting.append([matrix_id, matrix_a, matrix_b])
			else:
				print('	unknown command')

	def worker_thread(self, c):
		print('worker thread')
		while True:
			res = c.recv(1024)
			print(res)
			if res == 'exit':
				print('	worker exited')
				return
			elif res == 'ready':
				data = json.loads((c.recv(1024)).decode())
				worker_ip = data.get("ip")
				worker_port = data.get("port")
				self.workers.append([worker_ip, worker_port])


def dispatch_connection(arg):
	server = arg[0]
	con = arg[1]
	sender = con.recv(1024)
	if sender == b'c':
		print('request from client')
		server.client_thread(con)
	elif sender == b'w':
		print('request from worker')
		server.worker_thread(con)
	else:
		print('wrong sender: ' + sender)
	con.close()  # Close the connection


def divide_job(arg):
	server = arg[0]
	while True:
		if len(server.waiting) > 0:
			job = server.waiting.pop(0)
			matrix_id = job[0]
			matrix_a = job[1]
			matrix_b = job[2]
			rows_a = len(matrix_a)
			cols_a = len(matrix_a[0])
			rows_b = len(matrix_b)
			cols_b = len(matrix_b[0])
			rows_c = rows_a
			cols_c = cols_b
			for c_i in range(rows_c):
				for c_j in range(cols_c):
					chunk_a = matrix_a
					chunk_b = matrix_b
					for a_i in range(rows_a):
						for a_j in range(cols_a):
							if a_i != c_i:
								chunk_a[a_i][a_j] = 0
					for b_i in range(rows_b):
						for b_j in range(cols_b):
							if b_j != c_j:
								chunk_b[b_i][b_j] = 0
					server.processing.append(json.dumps({
						"matrix_id": matrix_id,
						"c_i": c_i,
						"c_j": c_j,
						"chunk_a": chunk_a,
						"chunk_b": chunk_b
					}))


def send_job(arg):
	server = arg[0]
	while True:
		if len(server.processing) > 0 and len(server.workers) > 0:
			worker = server.workers.pop(0)
			socket_to_worker = socket.socket()  # Create a socket object
			socket_to_worker.connect((worker.worker_ip, worker.worker_port))  # Bind to the port
			job = server.processing.pop(0)
			socket_to_worker.send(job.encode())
