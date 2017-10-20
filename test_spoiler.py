import socket
import time
import sys
import random

if len(sys.argv) < 5:
	print "python test_spoiler.py <string:dancer_locations> <int:port_number> <int:board_size> <int:number_of_stars>"
	exit()
	
HOST = 'localhost'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, int(sys.argv[2])))

board_size = int(sys.argv[3])
red = []
blue = []

def parse_input(filename):
	global red
	global blue

	fh = open(filename)
	file_contents = fh.readlines()
	
	adding_red = True
	
	for line in file_contents:
		fields = []
		line = line.rstrip('\r\n')

		if line == "Red dancer positions (start at 0)":
			continue
		
		if line == "Blue dancer positions (start at 0)":
			adding_red = False
			continue
		if line == "    ":
			continue

		fields = line.split(' ')

		if adding_red:
			red.append([int(fields[0]), int(fields[1])])
		else:
			blue.append([int(fields[0]), int(fields[1])])

###################################


parse_input(sys.argv[1])

data = s.recv(1024)
while not data == '^':
	data = s.recv(1024)

stars = []
for i in range(int(sys.argv[4])):
	stars.append([random.randint(0, board_size-1), random.randint(0, board_size-1)])

star_output = ""
for star in stars:
	print "Picking star at", star[0], star[1]
	star_output += str(star[0]) + " " + str(star[1]) + " "

s.sendall('{}'.format(star_output))
#s.sendall("10 2")
s.close()

