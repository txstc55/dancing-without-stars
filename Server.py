import socket


class Server(object):
    
  def __init__(self, host, port):
    """Init the server, set two sockets for players"""
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    self.socket.bind((host, port))
    self.sockets = [None, None]
    self.socket.listen(2)

  def establish_connection(self):
    """Waiting for two players to connect."""
    print("Waiting for Choreographer...")
    self.sockets[0], _ = self.socket.accept()
    choreographer = str(self.receive(0))
    print("Connection from " + choreographer + " as Choreographer established.")
    print("Waiting for Spoiler...")
    self.sockets[1], _ = self.socket.accept()
    spoiler = str(self.receive(1))
    print("Connection from " + spoiler + " as Spoiler established.")
    return choreographer, spoiler

  def send_all(self, data):
    """send data to both players"""
    for socket in self.sockets:
      socket.sendall(bytes(data, "utf-8"))

  def send_to(self, player, data):
    """0: Choreographer; 1: spoiler"""
    self.sockets[player].sendall(bytes(data, "utf-8"))

  def receive(self, player):
    """receive data from one player"""
    return self.sockets[player].recv(4096).decode("utf-8")

  def close(self):
    self.socket.close()