import sys
from game import Game
import random
import time

class RandomPlayer:

	def __init__(self):
		data = sys.stdin.readline().strip().split()
		self.player = int(data[0]) - 1 # player can have values 0 and 1
		self.n = int(data[1]) # n can have values 5, 6, or 7
		self.time_left = int(data[2])
		self.game = Game(self.n)
		self.RingPos = {}
		self.play()

	def placeRing(self):
		movetype = 'P'
		hexagon = random.randint(0,self.n)
		position = random.randint(0,max(0,6*hexagon-1))
		if hexagon==self.n and position%self.n==0:
			position+=1
		return '{type} {hex} {pos}'.format(type=movetype, hex=hexagon, pos=position), len(self.RingPos), hexagon, position

	def moveRing(self):
		movetype = 'M'
		ring_num = random.randint(0,self.n-1)
		while ring_num not in self.RingPos:
			ring_num = random.randint(0,self.n-1)
		ring = self.RingPos[ring_num]
		hexagon = random.randint(0,self.n)
		position = random.randint(0,max(0,6*hexagon-1))
		if hexagon==self.n and position%self.n==0:
			position+=1
		return '{type} {hexold} {posold} {hex} {pos}'.format(type=movetype, hexold=ring[0], posold=ring[1], hex=hexagon, pos=position), ring_num, hexagon, position

	def removeRing(self):
		movetype = 'R'
		hexagon = random.randint(0,self.n)
		position = random.randint(0,max(0,6*hexagon-1))
		ring_num = random.randint(0,self.n-1)
		while ring_num not in self.RingPos:
			ring_num = random.randint(0,self.n-1)
		ring = self.RingPos[ring_num]
		return '{type} {hex} {pos} {hexold} {posold}'.format(type=movetype, hex=hexagon, pos=position, hexold=ring[0], posold=ring[1]), ring_num

	def play(self):
		if self.player == 1:
			# while self.game.get_current_player()==0:
			move = sys.stdin.readline().strip()
			self.game.execute_move(move)
		while True:
			while True:
				state = self.game.check_player_state()
				if state == 0:
					move, i, hex, pos = self.placeRing()
					success = self.game.execute_move(move)
					if success != 0:
						# time.sleep(1)
						self.RingPos[i] = (hex, pos)
						move = move + '\n'
						sys.stderr.write('Chosen move: ' + move)	
						sys.stdout.write(move)
						sys.stdout.flush()
						break
				elif state == 1 or state == 2:
					move, i, hex, pos = self.moveRing()
					success = self.game.execute_move(move)
					sys.stderr.write('success1/2 is ' + str(success) + '\n')
					if success != 0:
						self.RingPos[i] = (hex, pos)
						state = self.game.check_player_state()
						sys.stderr.write('state is ' + str(state) + '\n')
						while state == 3 and self.game.get_current_player()==self.player:
							sec_move, i = self.removeRing()
							success = self.game.execute_move(sec_move)
							sys.stderr.write('success3 is ' + str(success) + '\n')
							if success != 0:
								del self.RingPos[i]
								state = self.game.check_player_state()
								sys.stderr.write('state is ' + str(state) + '\n')
								if state == 3 and self.game.get_current_player()==self.player:
									move = move + ' ' + sec_move
									continue
								sec_move = sec_move + '\n'
								sys.stderr.write('Chosen move: ' + sec_move)	
								sys.stdout.write(move + ' ' + sec_move)
								sys.stdout.flush()
								sys.stderr.write('Ring Removed!\n')
								sys.stderr.write('player is' + str(self.game.get_current_player()) + '\n')
								break
						else:
							move = move + '\n'
							sys.stderr.write('Chosen move: ' + move)	
							sys.stdout.write(move)
							sys.stdout.flush()
						break
				else:
					move = None
					while state == 3:
						sec_move, i = self.removeRing()
						success = self.game.execute_move(sec_move)
						sys.stderr.write('success3* is ' + str(success) + '\n')
						if success != 0:
							del self.RingPos[i]
							state = self.game.check_player_state()
							sys.stderr.write('state is ' + str(state) + '\n')
							if state == 3 and self.game.get_current_player()==self.player:
								if move:
									move = move + ' ' + sec_move
								else:
									move = sec_move
								continue
							sec_move = sec_move + '\n'
							sys.stderr.write('Chosen move: ' + sec_move)	
							if move:
								sys.stdout.write(move + ' ' + sec_move)
							else:
								sys.stdout.write(sec_move)
							sys.stdout.flush()
							sys.stderr.write('Ring Removed!\n')
							sys.stderr.write('player is' + str(self.game.get_current_player()) + '\n')
							break

			sys.stderr.write('waiting for other player\n')
			# while self.game.get_current_player()!=self.player:
			move = sys.stdin.readline().strip()
			self.game.execute_move(move)

random_player = RandomPlayer()
