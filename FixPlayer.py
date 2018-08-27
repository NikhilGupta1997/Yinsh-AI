import sys

class RandomPlayer:

	def __init__(self):
		data = sys.stdin.readline().strip().split()
		self.player = int(data[0]) - 1
		self.n = int(data[1])
		self.time_left = int(data[2])
		# self.game = Game(self.n)
		self.play()

	def play(self):
                player1_moves = ["! 0 0", "! 4 4", "! 4 6", "! 4 22", "! 4 20", "@ 0 0 3 9"]
                player2_moves = ["! 4 18", "! 4 16", "! 4 14", "! 4 12", "! 4 9", "@ 4 16 1 1"]
		if self.player == 1:
			move = sys.stdin.readline().strip()
			# self.game.execute_move(move)
                cnt = 0
		while True:
			# all_moves = self.game.generate_all_moves(self.player)
			# move = all_moves[random.randint(0, len(all_moves)-1)]
			# self.game.execute_move(move)
                        if(self.player == 0):
                            move = player1_moves[cnt]
                        elif(self.player == 1):
                            move = player2_moves[cnt]
                        move = move + '\n'
                        cnt = cnt + 1
                        # sys.stderr.write('Possible moves: ' + str(all_moves) + '\n')
			sys.stderr.write('Chosen move: ' + move)	
			sys.stdout.write(move)
			sys.stdout.flush()
			move = sys.stdin.readline().strip()
			# self.game.execute_move(move)

random_player = RandomPlayer()
