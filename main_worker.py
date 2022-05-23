from worker import Worker
import sys

if __name__ == "__main__":
	if len(sys.argv) == 1:
		server_ip = '127.0.0.1'
		server_port = 8080
		worker_port = 9090
	else:
		server_ip = sys.argv[1]
		server_port = int(sys.argv[2])
		worker_port = int(sys.argv[3])
	s = Worker(server_ip, server_port, worker_port)
	s.connect()
