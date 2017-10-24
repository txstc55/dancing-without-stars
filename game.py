import sys, socket, time, os
from Server import Server
from copy import deepcopy

"""
Usage: python3 game.py -h <host> -p <port> -f <filename> -s <size>
"""


class Game(object):

	def __init__(self, host, port, input_file, size):
		"""Initialize game"""
		# read file input
		self.file_input, self.dancers = self.__process_input(input_file)
		# setup board
		self.board_size = size
		self.num_color = len(self.dancers)
		self.board = self.__setup_board(self.dancers, size)
		self.stars = list()
		self.dancer_steps = 0
		# initialize server
		self.server, self.choreographer, self.spoiler = self.__setup_server(host, port)

	def __setup_server(self, host, port):
		server = Server(host, port)
		choreographer, spoiler = server.establish_connection()
		return server, choreographer, spoiler

	def __process_input(self, filename):
		"""read in input file"""
		file_input = open(filename)
		dancers = list()
		cur = -1
		for line in file_input:
			tokens = line.split()
			if len(tokens) == 0:
				continue # skip empty lines
			elif len(tokens) == 2:
				dancers[cur].add((int(tokens[0]), int(tokens[1])))
			else:
				cur = int(tokens[len(tokens) - 1]) - 1
				dancers.append(set())
		return file_input, dancers

	def __setup_board(self, dancers, size):
		"""Initialize board"""
		# fill all the space with 0
		board = [[0 for i in range(size)] for j in range(size)]
		# fill in all the dancer with their colors
		for color in range(len(dancers)):
			for pos in dancers[color]:
				board[pos[0]][pos[1]] = color + 1
		return board

	def __inside_board(self, x, y):
		"""check if this position is inside board"""
		if x not in range(self.board_size) or y not in range(self.board_size):
			return False
		return True

	def __manhattan_distance(self, x1, y1, x2, y2):
		return abs(x1 - x2) + abs(y1 - y2)

	def __is_star_valid(self, x, y):
		"""Check if it is valid to place a start at this position"""
		if not self.__inside_board(x, y):
			return False # outside board
		valid = False
		if self.board[x][y] == 0:
			valid = True
			# check manhattan distance with other stars
			for s in self.stars:
				if self.__manhattan_distance(s[0], s[1], x, y) < self.num_color + 1:
					valid = False # manhattan distance can't smaller than c + 1
					break
		return valid

	def __is_dancer_move_valid(self, start_x, start_y, end_x, end_y):
		"""Check if this dancer move is valid"""
		if not (self.__inside_board(start_x, start_y) and self.__inside_board(end_x, end_y)):
			return False # one of points outside board
		elif self.board[start_x][start_y] in (0, -1):
			return False # no dancer at this location
		elif start_x == end_x and start_y == end_y:
			return False # no movement at all
		elif self.board[end_x][end_y] == -1:
			return False # there is a star at end location
		else:
			return True

	def __check_finish(self):
		"""check if the current game is finished"""
		return self.__is_game_finish(self.board, self.dancers)

	def __check_one_direction(self, start_x, start_y, x_act, y_act, board, dancers):
		"""
		direction means vertically or horizontally\n
		it depends on x_act and y_act\n
		This function will start with a node\n
		move to one end of this line and start checking if this line contains all colors.
		"""
		n_board = deepcopy(board)
		n_dancers = deepcopy(dancers)
		cur_x = start_x
		cur_y = start_y
		# move to one end first
		while n_board[cur_x+x_act][cur_y+y_act] not in (0, -1):
			cur_x += x_act
			cur_y += y_act
		# start to check one by one, use a set to keep track of color
		colorset = set()
		while n_board[cur_x][cur_y] not in (0, -1) and n_board[cur_x][cur_y] not in colorset:
			c = n_board[cur_x][cur_y]
			colorset.add(c)
			n_board[cur_x][cur_y] = 0 # unmark
			n_dancers[c-1].remove((cur_x, cur_y)) # remove from set
			cur_x -= x_act # move towards the other end
			cur_y -= y_act
		# check if set contains all the colors
		if len(colorset) == self.num_color:
			return True, n_board, n_dancers
		else:
			return False, n_board, n_dancers

	def __is_game_finish(self, board, dancers):
		"""Check if this game state is finished"""
		# check if all dancers are removed
		empty = True
		index = 0
		for i in range(len(dancers)):
			group = dancers[i]
			index = i
			if len(group) != 0:
				empty = False
				break
		if empty:
			return True
		# not empty, pick one dancer from group
		start = next(iter(dancers[index]))
		cur_x = start[0]
		cur_y = start[1]
		# check vertically
		validline, n_board, n_dancers = self.__check_one_direction(cur_x, cur_y, -1, 0, board, dancers)
		if validline:
			return self.__is_game_finish(n_board, n_dancers)
		# check horizontally
		validline, n_board, n_dancers = self.__check_one_direction(cur_x, cur_y, 0, -1, board, dancers)
		if validline:
			return self.__is_game_finish(n_board, n_dancers)
		# not valid still not finish
		return False

	def __place_stars(self, stars):
		"""
		Place a list of stars on the board\n
		return true if success and false and error message if fail
		"""
		success = True
		msg = None
		for s in stars:
			if self.__is_star_valid(s[0], s[1]):
				self.stars.append(s)
				self.board[s[0]][s[1]] = -1 # mark it on board
			else:
				success = False
				msg = "Spoiler placed an invalid star at: " + str(s[0]) + ", " + str(s[1])
				break
		return success, msg
	
	def __update_dancers(self, moves):
		"""
		Make a list of parallel movements.\n
		Those movements count as 1 move since they happen at the same time.
		"""
		self.dancer_steps += 1
		success = True
		msg = None
		moved = set()
		for m in moves:
			x1 = m[0]
			y1 = m[1]
			x2 = m[2]
			y2 = m[3]
			# check if this dancer has already been moved
			if (x1, y1) in moved or (x2, y2) in moved:
				success = False
				msg = "Choreographer attempt to move a dance twice in one move from " + str(x1) + ", " + str(y1) \
				  + " to " + str(x2) + ", " + str(y2)
				break
			if self.__is_dancer_move_valid(x1, y1, x2, y2):
				# make the move
				c = self.board[x1][y1] # color
				self.dancers[c-1].remove((x1, y1))
				self.dancers[c-1].add((x2, y2))
				moved.add((x2, y2))
				if self.board[x2][y2] != 0: # need to swap
					t_c = self.board[x2][y2]
					self.dancers[t_c-1].remove((x2, y2))
					self.dancers[t_c-1].add((x1, y1))
					moved.add((x1, y1))
				self.board[x1][y1], self.board[x2][y2] = self.board[x2][y2], self.board[x1][y1] # swap
			else:
				success = False
				msg = "Choreographer made an invalid move from " + str(x1) + ", " + str(y1) \
				  + " to " + str(x2) + ", " + str(y2)
				break
		return success, msg

	def get_board(self):
		return self.board

	def start_game(self):
		# send input file to both players
		print("Sending input file to both players...")
		self.server.send_all(self.file_input)
		# now wait for spoiler to send stars
		print("Waiting for spoiler to send the stars...")
		start_time = time.time()
		star_data = self.server.receive(1)
		end_time = time.time()
		if time.time() - start_time > 120:
			print("Spoiler exceeds time limit!")
			sys.exit()
		print("Received stars!")
		# parse stars
		s_list = star_data.split()
		stars = list()
		for i in range(len(s_list)/2):
			stars.append((int(s_list[i]), int(s_list[i+1])))
		print(stars)
		print("Adding stars to the board...")
		# process stars
		success, msg = self.__place_stars(stars)
		if not success:
			print(msg)
			sys.exit()
		print("Done.")
		# send stars to choreographer
		print("Sending stars to the choreographer...")
		self.server.send_to(0, star_data)
		# receive moves from choreographer
		print("Receiving moves from choreographer...")
		start_time = time.time()
		choreo_finish = False
		while True:
			if time.time() - start_time > 120:
				break # exceed time limit
			move_data = self.server.receive(0)
			end_time = time.time()
			# parse move data
			m_list = move_data.split()
			moves = list()
			for i in range(len(m_list)/4):
				moves.append([int(m_list[i]), int(m_list[i+1]), int(m_list[i+2]), int(m_list[i+3])])
			# make move
			move_success, msg = self.__update_dancers(moves)
			if not success:
				print(msg) # invalid move
				sys.exit()
			# check if game is finished
			if self.__check_finish():
				choreo_finish = True
				break
		# check if finish or timeout
		if choreo_finish or self.__check_finish():
			print("Game finished!")
			print(self.choreographer + " has taken " + self.dancer_steps + " steps.")
		else:
			print("Choreographer exceeds time limit!")


if __name__ == "__main__":
	game = Game("localhost", 12345, "./sample_dancedata.txt", 400)