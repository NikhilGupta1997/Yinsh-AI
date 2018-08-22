import sys
import pdb
import time
import random

class Game:

	class Player:

		def __init__(self, flats, capstones):
			self.flats = flats
			self.capstones = capstones

	def __init__(self, n):
		self.n = n
		self.total_squares = n * n
		self.board = [[] for i in xrange(self.total_squares)]
		self.turn = 0
		if n == 5:
			self.max_flats = 21
			self.max_capstones = 1
		elif n == 6:
			self.max_flats = 30
			self.max_capstones = 1
		elif n == 7:
			self.max_flats = 40
			self.max_capstones = 1
		self.max_movable = n
		self.max_down = 1
		self.max_up = n
		self.max_left = 'a'
		self.max_right = chr(ord('a') + n - 1)
		self.moves = 0
		self.players = []
		self.players.append(Game.Player(self.max_flats, self.max_capstones))
		self.players.append(Game.Player(self.max_flats, self.max_capstones))
		self.all_squares = [self.square_to_string(i) for i in xrange(self.total_squares)]

	def square_to_num(self, square_string):
		''' Return -1 if square_string is invalid
		'''
		
		if len(square_string) != 2:
			return -1
		if not square_string[0].isalpha() or not square_string[0].islower() or not square_string[1].isdigit():
			return -1
		row = ord(square_string[0]) - 96
		col = int(square_string[1])
		if row < 1 or row > self.n or col < 1 or col > self.n:
			return -1
		return self.n * (col - 1) + (row - 1)

	def square_to_string(self, square):
		'''Convert square number to string
		'''
		if square < 0 or square >= self.total_squares:
			return ''
		row = square % self.n
		col = square / self.n
		return chr(row + 97) + str(col + 1)

	def execute_move(self, move_string):
		'''Execute move
		'''

		if self.turn == 0:
			self.moves += 1
		if self.moves != 1:
			current_piece = self.turn
		else:
			current_piece = 1 - self.turn
		if move_string[0].isalpha():
			square = self.square_to_num(move_string[1:])
			if move_string[0] == 'F' or move_string[0] == 'S':
				self.board[square].append((current_piece, move_string[0]))
				self.players[current_piece].flats -= 1
			elif move_string[0] == 'C':
				self.board[square].append((current_piece, move_string[0]))
				self.players[current_piece].capstones -= 1
		elif move_string[0].isdigit():
			count = int(move_string[0])
			square = self.square_to_num(move_string[1:3])
			direction = move_string[3]
			if direction == '+':
				change = self.n
			elif direction == '-':
				change = -self.n
			elif direction == '>':
				change = 1
			elif direction == '<':
				change = -1
			prev_square = square
			for i in xrange(4, len(move_string)):
				next_count = int(move_string[i])
				next_square = prev_square + change				
				if (len(self.board[next_square]) > 0) and (self.board[next_square][-1][1] == 'S'):
					self.board[next_square][-1] = (self.board[next_square][-1][0], 'F')
				if next_count - count == 0:
					self.board[next_square] += self.board[square][-count:]
				else:
					self.board[next_square] += self.board[square][-count:-count+next_count]
				prev_square = next_square
				count -= next_count
			count = int(move_string[0])
			self.board[square] = self.board[square][:-count]
		self.turn = 1 - self.turn

	def partition(self, n):
		'''Generates all permutations of all partitions
		of n
		'''

		part_list = []
		part_list.append([n])
		for x in xrange(1, n):
			for y in self.partition(n - x):
				part_list.append([x] + y)
		return part_list

	def check_valid(self, square, direction, partition):
		'''For given movement (partition), check if stack on
		square can be moved in direction. Assumes active player
		is topmost color
		'''
		if direction == '+':
			change = self.n
		elif direction == '-':
			change = -self.n
		elif direction == '>':
			change = 1
		elif direction == '<':
			change = -1
		for i in xrange(len(partition)):
			next_square = square + change * (i + 1)
			if len(self.board[next_square]) > 0 and self.board[next_square][-1][1] == 'C':
				return False
			if len(self.board[next_square]) > 0 and self.board[next_square][-1][1] == 'S' and i != len(partition) - 1:
				return False
			if i == len(partition) - 1 and len(self.board[next_square]) > 0 and self.board[next_square][-1][1] == 'S' and partition[i] > 1:
				return False
			if i == len(partition) - 1 and len(self.board[next_square]) > 0 and self.board[next_square][-1][1] == 'S' and self.board[square][-1][1] != 'C':
				return False
		return True

	def generate_stack_moves(self, square):
		'''Generate stack moves from square
		Assumes active player is topmost color
		'''

		all_moves = []
		r = square % self.n
		c = square / self.n
		size = len(self.board[square])
		dirs = ['+', '-', '<', '>']
		up = self.n - 1 - c
		down = c
		right = self.n - 1 - r
		left = r
		rem_squares = [up, down, left, right]
		for num in xrange(min(size, self.n)):
			part_list = self.partition(num + 1)
			for di in range(4):
				part_dir = [part for part in part_list if len(part) <= rem_squares[di]]
				# sys.stderr.write(self.all_squares[square] + ' ' + dirs[di] + ' ' + str(part_dir) + '\n')
				for part in part_dir:
					if self.check_valid(square, dirs[di], part):
						part_string = ''.join([str(i) for i in part])
						all_moves.append(str(sum(part)) + self.all_squares[square] + dirs[di] + part_string)
		return all_moves

	def generate_all_moves(self, player):
		'''Generate all possible moves for player
		Returns a list of move strings
		'''
		all_moves = []
		for i in xrange(len(self.board)):
			if len(self.board[i]) == 0:
				if self.players[player].flats > 0:
					all_moves.append('F' + self.all_squares[i])
				if self.moves != player and self.players[player].flats > 0:
					all_moves.append('S' + self.all_squares[i])
				if self.moves != player and self.players[player].capstones > 0:
					all_moves.append('C' + self.all_squares[i])
		for i in xrange(len(self.board)):
			if len(self.board[i]) > 0 and self.board[i][-1][0] == player and self.moves != player:
				all_moves += self.generate_stack_moves(i)
		return all_moves

class RandomPlayer:

	def __init__(self):
		data = sys.stdin.readline().strip().split()
		self.player = int(data[0]) - 1
		self.n = int(data[1])
		self.time_left = int(data[2])
		self.game = Game(self.n)
		self.play()

	def play(self):
		if self.player == 1:
			move = sys.stdin.readline().strip()
			self.game.execute_move(move)
		while True:
			all_moves = self.game.generate_all_moves(self.player)
			move = all_moves[random.randint(0, len(all_moves)-1)]
			self.game.execute_move(move)
			move = move + '\n'
			sys.stderr.write('Possible moves: ' + str(all_moves) + '\n')
			sys.stderr.write('Chosen move: ' + move)	
			sys.stdout.write(move)
			sys.stdout.flush()
			move = sys.stdin.readline().strip()
			self.game.execute_move(move)

random_player = RandomPlayer()
