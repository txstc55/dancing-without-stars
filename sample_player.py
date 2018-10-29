#!/usr/bin/python
import sys, random
from copy import deepcopy
from client import Client
from getopt import getopt, GetoptError

"""
python3 sample_player.py -H <host> -p <port> <-c|-s>
"""
def process_file(file_data):
	"""read in input file"""
	dancers = {}
	dancer_id = -1
	f = file_data.split("\n")
	for line in f:
		print(line)
		tokens = line.split()
		if len(tokens) == 2:
			dancer_id+=1
			dancers[dancer_id] = (int(tokens[0]), int(tokens[1]), latest_color)
		elif len(tokens)>2:
			latest_color = int(tokens[-1])
	return dancers

def print_usage():
	print("Usage: python3 sample_player.py -H <host> -p <port> [-c/-s]")

def get_args():
	host = None
	port = None
	player = None
	##########################################
	#PLEASE ADD YOUR TEAM NAME#
	##########################################
	name = "MY TEAM NAME"
	##########################################
	#PLEASE ADD YOUR TEAM NAME#
	##########################################
	try:
		opts, args = getopt(sys.argv[1:], "hcsH:p:", ["help"])
	except GetoptError:
		print_usage()
		sys.exit(2)
	for opt, arg in opts:
		if opt in ("-h", "--help"):
			print_usage()
			sys.exit()
		elif opt == "-H":
			host = arg
		elif opt == "-p":
			port = int(arg)
		elif opt == "-c":
			player = "c"
		elif opt == "-s":
			player = "s"
	if host is None or port is None or player is None:
		print_usage()
		sys.exit(2)
	return host, port, player, name

def get_buffer_stars(stars):
	stars_str = ""
	for s in stars:
		stars_str += (str(s[0]) + " " + str(s[1]) + " ")
	return stars_str

class Player:
	def __init__(self, board_size, num_color, k, dancers):
		self.board_size = board_size
		self.num_color = num_color
		# k dancers for each color
		self.k = k
		# self.dancers is a dictionary with key as the id of the dancers
		# with value as the tuple of 3 (x, y, c)
		# where (x,y) is initial position of dancer
		# c is the color id of the dancer
		self.dancers = dancers

	# TODO add your method here
	# Add your stars as a spoiler
	def get_stars(self):
		#
		#
		# You need to return a list of coordinates representing stars
		# Each coordinate is a tuple of 2 values (x, y)
		#
		#
		stars = []
		x = -1
		y = -1
		occupied = set()
		for id in self.dancers:
			occupied.add((self.dancers[id][0], self.dancers[id][1]))
		while len(stars) < self.k:
			x = random.randint(0, self.board_size - 1)
			y = random.randint(0, self.board_size - 1)
			if (x, y) not in occupied:
				# check manhattan distance with other stars
				ok_to_add = True
				for s in stars:
					if abs(x - s[0]) + abs(y - s[1]) < self.num_color + 1:
						ok_to_add = False
						break
				if ok_to_add:
					stars.append((x, y))
					occupied.add((x, y))
		return stars

	# TODO add your method here
	# Add your moves as a choreographer
	def get_moves(self, stars):
		#
		#
		# You need to return a list of moves from the beginning to the end of the game
		# Each move is a dictionary with key as the id of the dancer you want to move
		# with value as a tuple of 2 values (x, y) representing the new position of the dancer
		#
		#

		# pick 5 random dancers from dancers
		moves = []
		occupied = set()
		for id in self.dancers:
			occupied.add((self.dancers[id][0], self.dancers[id][1]))
		for star in stars:
			occupied.add(star)
		for i in range(100): # do 20 turns, each turn pick 5 random dancers
			move = {}
			count = 0
			while count < 5:
				# pick random dancers
				picked = random.sample(self.dancers.keys(), 5 - count)
				for id in picked:
					x, y, color = self.dancers[id]
					if id in move:
						continue
					c = random.sample([(1, 0), (-1, 0), (0, 1), (0, -1)], 1)[0]
					x2 = x + c[0]
					y2 = y + c[1]
					if (x2, y2) in occupied:
						continue
					if x2 not in range(self.board_size) or y2 not in range(self.board_size):
						continue
					move[id] = (x2, y2)
					self.dancers[id] = ((x2, y2, self.dancers[id][2]))
					occupied.remove((x, y))
					occupied.add((x2, y2))
					count += 1
			moves.append(move)
		return moves

def main():
	host, port, p, name = get_args()
	# create client
	client = Client(host, port)
	# send team name
	client.send(name)
	# receive other parameters
	parameters = client.receive()
	parameters_l = parameters.split()
	board_size = int(parameters_l[0])
	num_color = int(parameters_l[1])
	k = int(parameters_l[2]) # max num of stars
	# receive file data
	file_data = client.receive()
	# process file
	dancers = process_file(file_data) # a set of initial dancers
	__dancers = deepcopy(dancers)
	player = Player(board_size, num_color, k, dancers)
	# now start to play
	if p == "s":
		print("Making stars")
		stars = player.get_stars()
		print(stars)
		# send stars
		client.send(get_buffer_stars(stars))
	else: # choreographer
		# receive stars from server
		stars_str = client.receive()
		stars_str_l = stars_str.split()
		stars = []
		for i in range(int(len(stars_str_l)/2)):
			stars.append((int(stars_str_l[2*i]), int(stars_str_l[2*i+1])))

		moves = player.get_moves(stars)
		for move in moves: # iterate through all the moves
			print(move)
			move_str = str(len(move))
			for id in move: # for each dancer id in this move
				x, y, color = __dancers[id]
				nx, ny = move[id]
				move_str += " " + str(x) + " " + str(y) + " " + str(nx) + " " + str(ny)
				__dancers[id] = (nx, ny, 0)

			client.send(move_str)

		# send DONE flag
		client.send("DONE")
		# send a line to signal the server to stop
		rid = random.sample(__dancers.keys(), 1)[0]
		random_dancer = __dancers[rid]
		client.send(str(random_dancer[0]) + " " + str(random_dancer[1]) + " " + str(random_dancer[0]) + " " + str(random_dancer[1] + 4))

	# close connection
	client.close()

if __name__ == "__main__":
	main()
