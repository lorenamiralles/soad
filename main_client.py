from client import Client
import sys

if __name__ == "__main__":
  server_ip = sys.argv[1]
  server_port = int(sys.argv[2])
  client_port = int(sys.argv[3])
  s = Client(server_ip, server_port, client_port)
  s.connect()
