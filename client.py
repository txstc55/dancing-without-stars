import socket


class Client(object):
    
  def __init__(self, host, port):
    """Initialize client and connect"""
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.connect((host, port))
    print("Connected to server.")

  def send(self, data):
    """send data to server"""
    self.socket.sendall(bytes(data, "utf-8"))

  def receive(self):
    """receive data from server"""
    return self.socket.recv(4096).decode("utf-8")

  def close(self):
    self.socket.close()