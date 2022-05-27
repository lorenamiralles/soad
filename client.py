import socket
import json
import os
import asyncio

class Client:
	def __init__(self, server_ip, server_port, client_port):
		self.server_ip = server_ip
		self.client_port = client_port
		self.server_port = server_port

	def print_usage(self, message):
		print(
			"""
		 _________________________________________________________________________________
		|                                                                                 |
		|                     AN ERROR OCCURED WITH YOUR JOB REQUEST                      |
		|_________________________________________________________________________________|""")
		print(f"""
		  Error message: {message} """)
		print("""                                                                                
		 _________________________________________________________________________________
		| Matrix multiplications directories must contain two files named A.txt and B.txt |
		| each of them having the corresponding matrices encoded as ascii files of        |
		| single-space separated values, each row having the same number of elements and  |
		| representing a row of the matrix.                                               |
		| For obvious reasons (common knowledge on matrix multiplication) A.txt must have |
		| the same number of columns as rows has B.txt.                                   |
		| In a single job you can input a list of target directories separated by commas. |
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
	
	def write_matrix_file(self, filepath, matrix):
		with open(filepath, 'w') as file_out:
			file_out.write('/n'.join([' '.join(row) for row in matrix]))

	def connect(self):
		s = socket.socket()  # Create a socket object
		s.connect((self.server_ip, self.server_port))  # Bind to the port
		s.sendall(b'c')
		while True:
			inp = input('> ')
			if inp == 'exit':
				s.sendall(bytes('exit', 'utf-8'))
				exit()
			
			matrix_directories = [d.strip() for d in inp.split(',')]

			# Send all directories to server to compute matrix multiplications.
			for directory in matrix_directories:
				if directory[0] != '/':
					directory = os.path.join(os.getcwd(), directory)
				files = os.listdir(directory)
				print(directory)

				if not ('A.txt' in files and 'B.txt' in files):
					self.print_usage(f'Directory {directory} has missing files: A.txt or B.txt.')
					continue

				file_path_a = os.path.join(directory, 'A.txt')
				matrix_a, inp_error = self.read_matrix_file(file_path_a)
				if inp_error:
					self.print_usage(f'File {file_path_a} has bad format.')
					continue

				file_path_b = os.path.join(directory, 'B.txt')
				matrix_b, inp_error = self.read_matrix_file(file_path_b)
				if inp_error:
					self.print_usage(f'File {file_path_b} has bad format.')
					continue

				if (len(matrix_a[0]) != len(matrix_b)):
					self.print_usage(f'Matrices in directory {directory} cannot be multiplied.')
					continue

				job_data = json.dumps({'id': directory, 'a': matrix_a, 'b': matrix_b})
				s.sendall(b'job')
				s.sendall(job_data.encode())
			
			# Await responses of job.
			for i in range(len(matrix_directories)):
				response = json.loads((s.recv(1024)).decode())
				directory = response['id']
				print(f'Response #{i}: Job finished for directory: {directory}')
				self.write_matrix_file(os.path.join(directory, 'OUT.txt'), response['c'])
