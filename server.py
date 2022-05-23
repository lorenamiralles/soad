import socket
import json
from threading import Thread


class Server:
	def __init__(self, server_ip, server_port, ):
		self.server_ip = server_ip
		self.server_port = server_port
		self.waiting = []
		self.sending = []
		self.processing = {}  # dictionary
		self.done = []
		self.workers = []
		self.clients = []
		self.listening = True

	def listen(self):
		thread_divide_job = Thread(target=divide_job, args=((self),))
		thread_start_job = Thread(target=start_job, args=((self),))
		thread_finish_job = Thread(target=finish_job, args=((self),))
		thread_divide_job.start()
		thread_start_job.start()
		thread_finish_job.start()

		server_socket = socket.socket()  # Create a socket object
		server_socket.bind((self.server_ip, self.server_port))  # Bind to the port
		server_socket.listen(5)  # Now wait for client connection.
		while self.listening:
			connection, addr = server_socket.accept()  # Establish connection with client.
			print('Got connection from', addr)
			thread_dispatch = Thread(target=dispatch_connection, args=((self, connection),))
			# thread.daemon = False
			thread_dispatch.start()

	# thread_divide_job.join()

	def client_receive(self, c):
		print('client thread')
		while True:
			req = (c.recv(1024)).decode()
			print(req)
			if req == 'exit':
				print('	client exited')
				return
			elif req == 'job':
				data = json.loads((c.recv(1024)).decode())
				client_ip = data.get("ip")
				client_port = data.get("port")
				matrix_id = data.get("id")
				matrix_a = data.get("a")
				matrix_b = data.get("b")
				self.waiting.append([client_ip, client_port, matrix_id, matrix_a, matrix_b])
			else:
				print('	unknown command')

	def worker_thread(self, con):
		print('worker thread')
		while True:
			res = con.recv(1024)
			print(res)
			if res == 'exit':
				print('	worker exited')
				return
			elif res == 'ready':
				self.workers.append([con])
			elif res == 'done':
				data = json.loads((con.recv(1024)).decode())
				matrix_id = data.get("matrix_id")
				c_i = data.get("c_i")
				c_j = data.get("c_j")
				chunk_c = data.get("chunk_c")
				self.processing[matrix_id][2] += 1
				self.processing[matrix_id][3][c_i][c_j] = chunk_c
				matrix_c = self.processing[matrix_id][3]
				c_n = len(matrix_c)
				c_m = len(matrix_c[0])
				if self.processing[matrix_id][2] == c_n * c_m:
					client_ip = self.processing[matrix_id][0]
					client_port = self.processing[matrix_id][1]
					self.done.append([client_ip, client_port, matrix_id, matrix_c])
					self.processing.pop(matrix_id)


def dispatch_connection(arg):
	server = arg[0]
	con = arg[1]
	sender = con.recv(1024)
	if sender == b'c':
		print('request from client')
		server.client_receive(con)
	elif sender == b'w':
		print('request from worker')
		server.worker_thread(con)
	else:
		print('wrong sender: ' + sender)
	con.close()  # Close the connection


def divide_job(arg):
	server = arg
	while True:
		if len(server.waiting) > 0:
			job = server.waiting.pop(0)
			client_ip = job[0]
			client_port = job[1]
			matrix_id = job[2]
			matrix_a = job[3]
			matrix_b = job[4]
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
					server.sending.append(json.dumps({
						"matrix_id": matrix_id,
						"c_i": c_i,
						"c_j": c_j,
						"chunk_a": chunk_a,
						"chunk_b": chunk_b
					}))
			matrix_c = [[0] * rows_c, [0] * cols_c]
			server.processing[matrix_id] = [client_ip, client_port, 0, matrix_c]


def start_job(arg):
	server = arg
	while True:
		if len(server.sending) > 0 and len(server.workers) > 0:
			worker = server.workers.pop(0)
			job = server.sending.pop(0)
			socket_to_worker = socket.socket()
			socket_to_worker.connect((worker[0], worker[1]))
			socket_to_worker.sendall(job.encode())


def finish_job(arg):
	server = arg
	while True:
		if len(server.done) > 0:
			job = server.done.pop(0)
			client_ip = job[0]
			client_port = job[1]
			matrix_id = job[2]
			matrix_c = job[3]
			socket_to_client = socket.socket()
			socket_to_client.connect((client_ip, client_port))
			response = json.dumps({"id": matrix_id, "c": matrix_c})
			socket_to_client.sendall(response.encode())
