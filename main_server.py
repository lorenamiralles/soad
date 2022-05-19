from server import Server
import sys


if __name__ == "__main__":
	if len(sys.argv) == 1:
		server_ip = '127.0.0.1'
		server_port = 8080
	else:
		server_ip = sys.argv[1]
		server_port = int(sys.argv[2])
	s = Server(server_ip, server_port)
	s.listen()
