from socket import socket

class Server(object):
    
  def __init__(self, host, port):
    """Init the server, set two sockets for players"""
    self.socket = socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind((host, port))
    self.sockets = [None, None]
    self.socket.listen(2)

  def establish_connection(self):
    """Waiting for two players to connect."""
    print("Waiting for Choreographer...")
    self.sockets[0], _ = self.socket.accept()
    print("Connection from Choreographer established.")
    print("Waiting for Spoiler...")
    self.sockets[1], _ = self.socket.accept()
    print("Connection from Spoiler established.")

  def send_all(self, data):
    """send data to both players"""
    s.sendall(data) for s in self.sockets

  def receive(self, player):
    """receive data from one player"""
    return self.sockets[player].recv(4096)

  def __del__(self):
    self.socket.close()
