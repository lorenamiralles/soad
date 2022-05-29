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
		with open(filepath, 'r') as file_a:
			data = file_a.read()
			rows = data.split("\n")
			matrix = []
			for row in rows:
				new_row = []
				for j in row.split(" "):
					new_row.append(float(j))
				matrix.append(new_row)
			if any(len(matrix[0]) != len(row) for row in matrix):
				inp_error = True
		return matrix, inp_error
	
	def write_matrix_file(self, filepath, matrix):
		with open(filepath, 'w') as file_out:
			txt = ""
			for row in matrix:
				for item in row:
					txt += str(item) + " "
				txt += "\n"
			file_out.write(txt)

	def connect(self):
		s = socket.socket()  # Create a socket object
		s.connect((self.server_ip, self.server_port))  # Bind to the port
		print('sending c')
		s.send(b'c')
		s.recv(1024*1000)
		while True:
			inp = input('> ')
			if inp == 'exit':
				print('sending exit')
				s.send(b'exit')
				s.recv(1024*1000)
				exit()
			
			matrix_directories = [d.strip() for d in inp.split(',')]
			bad_directories = 0

			# Send all directories to server to compute matrix multiplications.
			for directory in matrix_directories:
				if directory[0] != '/':
					directory = os.path.join(os.getcwd(), directory)
				if not os.path.exists(directory):
					bad_directories += 1
					continue
				files = os.listdir(directory)
				print(directory)

				if not ('A.txt' in files and 'B.txt' in files):
					self.print_usage(f'Directory {directory} has missing files: A.txt or B.txt.')
					bad_directories += 1
					continue

				file_path_a = os.path.join(directory, 'A.txt')
				matrix_a, inp_error = self.read_matrix_file(file_path_a)
				if inp_error:
					self.print_usage(f'File {file_path_a} has bad format.')
					bad_directories += 1
					continue

				file_path_b = os.path.join(directory, 'B.txt')
				matrix_b, inp_error = self.read_matrix_file(file_path_b)
				if inp_error:
					self.print_usage(f'File {file_path_b} has bad format.')
					bad_directories += 1
					continue

				if (len(matrix_a[0]) != len(matrix_b)):
					self.print_usage(f'Matrices in directory {directory} cannot be multiplied.')
					bad_directories += 1
					continue

				job_data = json.dumps({'id': directory, 'a': matrix_a, 'b': matrix_b})
				print('sending job')
				s.send(b'job')
				s.recv(1024*1000)
				print('sending data')
				s.send(job_data.encode())
				s.recv(1024*1000)
			
			# Await responses of job.
			for i in range(len(matrix_directories)-bad_directories):
				response = json.loads((s.recv(1024*1000)).decode())
				directory = response['id']
				print(f'Response #{i}: Job finished for directory: {directory}')
				self.write_matrix_file(os.path.join(directory, 'OUT.txt'), response['c'])
