from client import Client
import sys

if __name__ == "__main__":
	if len(sys.argv) == 1:
		server_ip = '127.0.0.1'
		server_port = 8080
		client_port = 8081
	else:
		server_ip = sys.argv[1]
		server_port = int(sys.argv[2])
		client_port = int(sys.argv[3])
	s = Client(server_ip, server_port, client_port)
	s.connect()
