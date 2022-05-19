import socket
import json
from threading import Thread


class Server:
    def __init__(self, server_ip, server_port, ):
        self.server_ip = server_ip
        self.server_port = server_port
        self.work_queue = []
        self.processing_queue = []
        self.return_queue = []

    def listen(self):
        s = socket.socket()  # Create a socket object
        s.bind((self.server_ip, self.server_port))  # Bind to the port
        s.listen(5)  # Now wait for client connection.
        while True:
            c, addr = s.accept()  # Establish connection with client.
            print('Got connection from', addr)
            thread = Thread(target=dispatch_connection, args=((self, c),))
            # thread.daemon = False
            thread.start()

    def client_thread(self, c):
        print('client thread')
        while True:
            res = (c.recv(1024)).decode()
            print(res)
            if res == 'exit':
                print('    client exited')
                return
            elif res == 'job':
                data = json.loads((c.recv(1024)).decode())
                matrix_a = data.get("a")
                matrix_b = data.get("c")
            else:
                print('    unknown command')

    def node_thread(self, c):
        print('node thread')
        while True:
            res = c.recv(1024)
            if res == 'exit':
                return


def dispatch_connection(arg):
    server = arg[0]
    c = arg[1]
    peer = c.recv(1024)
    if peer == b'c':
        server.client_thread(c)
    elif peer == b'n':
        print(peer)
        server.node_thread(c)
    else:
        print(peer)
    c.close()  # Close the connection
