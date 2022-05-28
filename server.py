import socket
import json
from threading import Thread
from copy import deepcopy
import time


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
		thread_start_job = Thread(target=start_job, args=(self,))
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
			print('accept connection: ', connection)
			thread_dispatch = Thread(target=dispatch_connection, args=((self, connection),))
			# thread.daemon = False
			thread_dispatch.start()

		thread_divide_job.join()

	def client_receive(self, client_con):
		print('client thread')
		while self.listening:
			print('client connection 1: ', client_con)
			req = (client_con.recv(1024)).decode()
			client_con.send(b'ok')
			print('client command', req)
			if req == 'exit':
				print('	client exited')
				self.listening = False
				return
			elif req == 'job':
				print(' appending job')
				print('client connection 2: ', client_con)
				data = json.loads((client_con.recv(1024)).decode())
				client_con.send(b'ok')
				matrix_id = data.get("id")
				matrix_a = data.get("a")
				matrix_b = data.get("b")
				print('matrix_a',matrix_a)
				print('matrix_b',matrix_b)
				self.waiting.append([client_con, matrix_id, matrix_a, matrix_b])
				print(' workers queue:', len(self.workers))
				print(' waiting queue:', len(self.waiting))
			elif req == 'job finished':
				print(' worker finished')
			else:
				print('	unknown client command: ', req)
				self.listening = False

	def worker_thread(self, worker_con):
		print('worker thread')
		while self.listening:
			print('worker connection 1: ', worker_con)
			res = worker_con.recv(1024).decode()
			worker_con.send(b'ok')
			print('worker command', res)
			if res == 'exit':
				print('	worker exited')
				return
			elif res == 'ready':
				print(' appending worker')
				self.workers.append(worker_con)
			elif res == 'done':
				print('	worker done')
				print('worker connection 2: ', worker_con)
				data_bytes = (worker_con.recv(1024))
				worker_con.send(b'ok')
				data_json = data_bytes.decode()
				print(data_json)
				data = json.loads(data_json)
				matrix_id = data.get("matrix_id")
				c_i = data.get("c_i")
				c_j = data.get("c_j")
				chunk_c = data.get("chunk_c")
				print('chunk_c: ', chunk_c)
				print('count: ', self.processing[matrix_id][1])
				self.processing[matrix_id][1] += 1
				self.processing[matrix_id][2][c_i][c_j] = chunk_c
				matrix_c = self.processing[matrix_id][2]
				c_n = len(matrix_c)
				c_m = len(matrix_c[0])
				print('matrix_c: ', matrix_c)
				print('c_n: ', c_n)
				print('c_m: ', c_m)
				if self.processing[matrix_id][1] == c_n * c_m:
					client_con = self.processing[matrix_id][0]
					self.done.append([client_con, matrix_id, matrix_c])
					self.processing.pop(matrix_id)
			else:
				print('	unknown worker command: ', res)
				self.listening = False


def dispatch_connection(arg):
	server = arg[0]
	con = arg[1]
	print('dispatch connection: ', con)
	sender = con.recv(1).decode()
	con.send(b'ok')
	if sender == 'c':
		print('request from client')
		server.client_receive(con)
	elif sender == 'w':
		print('request from worker')
		server.worker_thread(con)
	else:
		print('wrong sender: ' + sender)
	con.close()  # Close the connection


def divide_job(server):
	while server.listening:
		if len(server.waiting) > 0:
			print('dividing matrices')
			job = server.waiting.pop(0)
			con = job[0]
			matrix_id = job[1]
			matrix_a = job[2]
			matrix_b = job[3]
			rows_a = len(matrix_a)
			cols_a = len(matrix_a[0])
			rows_b = len(matrix_b)
			cols_b = len(matrix_b[0])
			rows_c = rows_a
			cols_c = cols_b
			print('matrix_a',matrix_a)
			print('matrix_b',matrix_b)
			print('rows_c: ', rows_c)
			print('cols_c: ', cols_c)
			matrix_c = [[0] * cols_c] * rows_c
			server.processing[matrix_id] = [con, 0, matrix_c]
			for c_i in range(rows_c):
				for c_j in range(cols_c):
					chunk_a = deepcopy(matrix_a)
					chunk_b = deepcopy(matrix_b)
					print('pre chunk_a',chunk_a)
					print('pre chunk_b',chunk_b)
					for a_i in range(rows_a):
						for a_j in range(cols_a):
							if a_i != c_i:
								chunk_a[a_i][a_j] = 0.0
					for b_i in range(rows_b):
						for b_j in range(cols_b):
							if b_j != c_j:
								chunk_b[b_i][b_j] = 0.0
					print('post chunk_a',chunk_a)
					print('post chunk_b',chunk_b)
					server.sending.append(json.dumps({
						"matrix_id": matrix_id,
						"c_i": c_i,
						"c_j": c_j,
						"chunk_a": chunk_a,
						"chunk_b": chunk_b
					}))


def start_job(server):
	while server.listening:
		if len(server.sending) > 0 and len(server.workers) > 0:
			print('sending job to worker')
			worker_con = server.workers.pop(0)
			job = server.sending.pop(0)
			print('worker connection 3: ', worker_con)
			worker_con.send(job.encode())


def finish_job(server):
	while server.listening:
		if len(server.done) > 0:
			print('job finished')
			job = server.done.pop(0)
			client_con = job[0]
			matrix_id = job[1]
			matrix_c = job[2]
			response = json.dumps({"id": matrix_id, "c": matrix_c})
			print('client connection 3: ', client_con)
			client_con.send(response.encode())
