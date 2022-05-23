import socket
import json
import os


class Client:
	def __init__(self, server_ip, server_port, client_port):
		self.server_ip = server_ip
		self.client_port = client_port
		self.server_port = server_port

	def print_usage(self):
		print(
			"""
		___________________________________________________________________________________
		|																				  |
		|					   AN ERROR OCCURED WITH YOUR JOB REQUEST					  |
		|_________________________________________________________________________________|
		|																				  |
		| Matrix multiplications directory must contain tow files named A.txt and B.txt   |
		| each of them having the corresponding matrices encoded as ascii files of 		  |
		| single-space separated values, each row having the same number of elements and  |
		| representing a row of the matrix.												  |
		| For obvious reasons (common knowledge on matrix multiplication) A.txt must have |
		| the same number of columns as rows has B.txt.									  |
		|_________________________________________________________________________________|
		""")

	def read_matrix_file(self, filepath):
		inp_error = False
		matrix = []
		with open(filepath, 'r') as file_a:
			matrix = [row.split(' ') for row in file_a.readlines()]
			if any(len(matrix[0]) != len(row) for row in matrix):
				inp_error = True
		return matrix, inp_error

	def connect(self):
		s = socket.socket()  # Create a socket object
		s.connect((self.server_ip, self.server_port))  # Bind to the port
		s.sendall(b'c')
		while True:
			inp = input('> ')
			if inp == 'exit':
				s.sendall(bytes('exit', 'utf-8'))
				exit()

			directory = os.getcwd()
			files = os.listdir(directory)

			if not ('A.txt' in files and 'B.txt' in files):
				self.print_usage()
				continue

			matrix_a, inp_error = self.read_matrix_file(os.path.join(directory, 'A.txt'))
			if inp_error:
				self.print_usage()
				continue

			matrix_b, inp_error = self.read_matrix_file(os.path.join(directory, 'B.txt'))
			if inp_error:
				self.print_usage()
				continue

			job_data = json.dumps({'id': directory, 'a': matrix_a, 'b': matrix_b})
			s.sendall(b'job')
			s.sendall(job_data.encode())
