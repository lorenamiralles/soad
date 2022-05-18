from server import Server
import sys

if __name__ == "__main__":
  server_ip = sys.argv[1]
  server_port = int(sys.argv[2])
  s = Server(server_ip, server_port)
  s.listen()
