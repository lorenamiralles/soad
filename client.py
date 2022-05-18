import socket

class Client:
  def __init__(self, server_ip, server_port, client_port):
    self.server_ip = server_ip
    self.client_port = client_port
    self.server_port = server_port

  def connect(self):
    s = socket.socket()                           # Create a socket object
    s.connect((self.server_ip, self.server_port))        # Bind to the port
    s.send(b'c')
    while True:
      msg = input('> ')
      s.send(bytes(msg, 'utf-8'))
    s.close()