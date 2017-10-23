import sys, socket, time, os
from Server import Server
from copy import deepcopy


class Game(object):

	def __init__(self, host, port, input_file, size, k):
		"""Initialize game"""
		# read file input
		self.file_input, self.dancers = self.__process_input(input_file)
		# setup board
		self.board_size = size
		self.num_color = len(self.dancers)
		self.board = self.__setup_board(self.dancers, size)
		self.stars = list()
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
			return False # one of point outside board
		elif self.board[start_x][start_y] in (0, -1):
			return False # no dancer at this location
		elif start_x == end_x and start_y == end_y:
			return True # no movement
		elif self.board[end_x][end_y] == -1:
			return False # there is a star at end location
		else:
			return True

	def __should_game_terminate(self):
		"""check if the current game is finished"""
		return self.__is_game_finish(self.board, self.dancers)

	def __check_one_direction(self, start_x, start_y, colorset, x_act, y_act, board, dancers):
		cur_x = start_x
		cur_y = start_y
		while board[cur_x][cur_y] not in (0, -1) and board[cur_x][cur_y] not in colorset:
			c = board[cur_x][cur_y]
			colorset.add(c)
			board[cur_x][cur_y] = 0 # unmark
			dancers[c-1].remove((cur_x, cur_y)) # remove from set
			cur_x += x_act
			cur_y += y_act

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
		# copy data for recurrisive calls
		n_dancers = deepcopy(dancers)
		n_board = deepcopy(board)
		s = set()
		# check top first
		self.__check_one_direction(cur_x, cur_y, s, -1, 0, n_board, n_dancers)
		# check bot
		self.__check_one_direction(cur_x+1, cur_y, s, 1, 0, n_board, n_dancers)
		if len(s) != self.num_color:
			# now need to check horizontally
			# create new copies
			n_dancers = deepcopy(dancers)
			n_board = deepcopy(board)
			s = set()
			self.__check_one_direction(cur_x, cur_y, s, 0, -1, n_board, n_dancers) # check left
			self.__check_one_direction(cur_x, cur_y+1, s, 0, 1, n_board, n_dancers) # check right
		if len(s) != self.num_color:
			return False
		else:
			return self.__is_game_finish(n_board, n_dancers)

	def __place_stars(self, stars):
		success = True
		msg = None
		for s in stars:
			if self.__is_star_valid(s[0], s[1]):
				self.stars.append(s)
				self.board[s[0]][s[1]] = -1
			else:
				success = False
				msg = "Spoiler placed an invalid star at: " + str(s[0]) + ", " + str(s[1])
				break
		return success, msg
	
	def __update_dancers(self, moves):
		success = True
		msg = None
		for m in moves:
			x1 = m[0]
			y1 = m[1]
			x2 = m[2]
			y2 = m[3]
			if self.__is_dancer_move_valid(x1, y1, x2, y2):
				# make the move
				c = self.board[x1][y1] # color
				if self.board[x2][y2] == 0:
					self.dancers[c-1].remove((x1, y1))
					self.dancers[c-1].add((x2, y2))
				else: # this is a swap
					t_c = self.board[x2][y2]
					self.dancers[c-1].remove((x1, y1))
					self.dancers[c-1].add((x2, y2))
					self.dancers[t_c-1].remove((x2, y2))
					self.dancers[t_c-1].add((x1, y1))
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
		self.server.send_all(self.file_input)
		# now wait for spoiler to send stars
		start_time = time.time()
		star_data = self.server.receive(1)
		end_time = time.time()
		if time.time() - start_time > 120:
			print("Spoiler exceeds time limit!")
			sys.exit()
		# parse stars
		s_list = star_data.split()
		stars = list()
		for i in range(len(s_list)/2):
			stars.append((int(s_list[i]), int(s_list[i+1])))
		# process stars
		success, msg = self.__place_stars(stars)
		if not success:
			print(msg)
			sys.exit()
		# send stars to choreographer
		self.server.send_to(0, star_data)
		# receive moves from choreographer
		start_time = time.time()
		move_data = self.server.receive(0)
		end_time = time.time()
		if time.time() - start_time > 120:
			print("Choreographer exceeds time limit!")
			sys.exit()
		# parse move data
		m_list = move_data.split()
		moves = list()
		for i in range(len(m_list)/4):
			moves.append([int(m_list[i]), int(m_list[i+1]), int(m_list[i+2]), int(m_list[i+3])])
		# process
		success, msg = self.__update_dancers(moves)
		if not success:
			print(msg)
			sys.exit()
		# now check if the game is finished
		if self.__should_game_terminate():
			print("Game finished!")
			print(self.choreographer + " has taken " + len(moves) + " steps.")
		else:
			print("Choreographer didn't achieve goal.")


if __name__ == "__main__":
	game = Game("localhost", 12345, "./sample_dancedata.txt", 400, 40)