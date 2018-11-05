from __future__ import print_function 

import copy
import json
import math
from multiset import Multiset
import numpy as np
import os
import sys
import time

from jinja2 import Environment, FileSystemLoader
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

board_sizes = { 5 : 11, 6 : 13, 7 : 15 } # Rings : Board Size
display_size = { 5 : 650, 6 : 750, 7 : 850 } # Rings : Pixels

PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_ENVIRONMENT = Environment(
	autoescape=False,
	loader=FileSystemLoader(os.path.join(PATH, 'templates')),
	trim_blocks=False)
 
def render_template(template_filename, context):
	return TEMPLATE_ENVIRONMENT.get_template(template_filename).render(context)
 
def create_index_html(size, rings, rows, seq):
	fname = "Yinsh.html"
	context = {
		'size': size,
		'rings': rings,
		'rows': rows,
		'seq': seq
	}
	with open(fname, 'w') as f:
		html = render_template('index.html', context)
		f.write(html)

class Game:

	def __init__(self, n, seq, mode='CUI', time=120):
		if n in board_sizes:
			self.rings = int(n)
			self.board_size = board_sizes[n]
			self.display_size = display_size[n]
		else:
			raise AssertionError("Number of rings must be either 5, 6 or 7")
		
		# Setup Driver
		create_index_html(self.display_size, n, self.board_size, seq)
		chrome_options = Options()
		chrome_options.add_argument("--disable-infobars")
		if mode != 'GUI':
			chrome_options.add_argument('headless');
		self.driver = webdriver.Chrome(chrome_options=chrome_options)
		abs_path = os.path.abspath('Yinsh.html')
		self.driver.get("file:" + abs_path)
		self.driver.set_window_size(width=self.display_size, height=(self.display_size+60))

		self.spacing = float(self.display_size)/self.board_size
		self.altitude = self.spacing * math.sqrt(3)/2 
		self.centerx = int(self.display_size)/2
		self.centery = int(self.display_size)/2
		self.rows = self.board_size

		self.timer = time # Useful to optimise bot strategy

	def get_corner_coord(self, corner, hexagon) :
		x_mov = self.spacing * hexagon * math.sin(math.radians(corner * 60))
		y_mov = -(self.spacing * hexagon * math.cos(math.radians(corner * 60)))
		return np.array([self.centerx + x_mov, self.centery + y_mov])

	def get_non_corner_coord(self, corner1, corner2, point_num_side, hexagon) :
		corner1_coord = self.get_corner_coord(corner1, hexagon)
		corner2_coord = self.get_corner_coord(corner2, hexagon)
		return ((corner1_coord * (hexagon - point_num_side) / hexagon) + (corner2_coord * point_num_side / hexagon))

	def click_at(self, hexagon, point) :
		el = self.driver.find_elements_by_id("PieceLayer")
		action = webdriver.common.action_chains.ActionChains(self.driver)
		if (hexagon == 0) :
				action.move_to_element_with_offset(el[0], self.centerx, self.centery)
		else :
			if (point % hexagon == 0) :
				pt_coord = self.get_corner_coord(point / hexagon, hexagon)
				action.move_to_element_with_offset(el[0], pt_coord[0], pt_coord[1])
			else :
				pt_coord = self.get_non_corner_coord(point // hexagon, point // hexagon + 1, point % hexagon, hexagon)
				action.move_to_element_with_offset(el[0], pt_coord[0], pt_coord[1])
		action.click()
		action.perform()

	def check_move_validity(self):
		return self.driver.execute_script('return is_valid;')

	def check_player_state(self):
		return self.driver.execute_script('return required_move;')

	def get_current_player(self):
		return self.driver.execute_script('return current_player;')

	def validMovesDir(self,xcoord, ycoord, asign, bsign):
		validMoves = set()
		positions = list(self.driver.execute_script('return positions;'))
		token_line = 0
		a = asign
		b = bsign
		while(xcoord+a>=0 and xcoord+a<self.rows and ycoord+b>=0 and ycoord+b<self.rows and abs(positions[xcoord+a][ycoord+b]['piece'])!=2 and positions[xcoord+a][ycoord+b]['x']!=-1):
			if(positions[xcoord+a][ycoord+b]['piece']!=0):
				token_line = 1
				a += asign
				b += bsign
				continue

			validMoves.add((xcoord, ycoord, xcoord+a, ycoord+b))

			if(token_line == 1):
				break

			a += asign
			b += bsign
	
		return validMoves

	def getAllValidMoves(self, ringPos):
		validMoves = set()

		for ring_num in ringPos:
			# print('Ring Num: '+str(ring_num), file=sys.stderr)
			ring = ringPos[ring_num]
			board_ring_x, board_ring_y = self.hexpos2pos_coord(ring[0], ring[1])
			validMoves = validMoves.union(self.validMoveRing(board_ring_x, board_ring_y))

		return validMoves

	def boardToHexMap(self, n):
		m = dict()
		for i in range(n+1):
			num_points_x = max(1, i*6)
			for j in range(num_points_x):
				pos = self.hexpos2pos_coord(i,j)        
				if(pos == None):
					continue
				x, y = pos
				m[(x,y)] = i, j

		return m

	def validMoveRing(self, ringx, ringy):
		## These must be board coordinates
		validMoves = set()
		v1 = self.validMovesDir(ringx, ringy, 1,1)
		v2 = self.validMovesDir(ringx, ringy, -1,-1)
		v3 = self.validMovesDir(ringx, ringy, 0,1)
		v4 = self.validMovesDir(ringx, ringy, 1,0)
		v5 = self.validMovesDir(ringx, ringy, 0,-1)
		v6 = self.validMovesDir(ringx, ringy, -1,0)

		return validMoves.union(v1).union(v2).union(v3).union(v4).union(v5).union(v6)

	def hexpos2boardcoord(self, hexagon, point) :
		if (hexagon == 0) :
				return np.array([self.centerx, self.centery])
		else :
			if (point % hexagon == 0) :
				return self.get_corner_coord(point / hexagon, hexagon)
			else :
				return self.get_non_corner_coord(point // hexagon, point // hexagon + 1, point % hexagon, hexagon)

	def board2pos_coord(self, xcoord, ycoord) :
		positions = list(self.driver.execute_script('return positions;'))
		for i in range(self.rows): #(var i=0;i<rows;i++){
			for j in range(self.rows): #(var j=0;j<rows;j++)
				if(positions[i][j]['x'] == -1):
					continue
				if(positions[i][j]['x'] - self.altitude/2 < xcoord and positions[i][j]['x'] + self.altitude/2 > xcoord and positions[i][j]['y'] - self.altitude/2 < ycoord and positions[i][j]['y'] + self.altitude/2 > ycoord):
					return (i,j)

	def hexpos2pos_coord(self, hex, pos):
		board_coord = self.hexpos2boardcoord(hex, pos)
		return self.board2pos_coord(board_coord[0], board_coord[1])

	### Score Class
	# 3-0: 10
	# 3-1: 9
	# 3-2: 8
	# 2-0: 7
	# 2-1: 6
	# 1-0: 6
	# x-x: 5
	# 0-1: 4
	# 1-2: 4
	# 0-2: 3
	# 2-3: 2
	# 1-3: 1
	# 0-3: 0

	def calculate_score(self, rA, rB, mA, mB, Error_state):
		if Error_state == '1':
			rB = 3
		elif Error_state == '2':
			rA = 3

		if rB == 5:
			rB = 0
		if rA == 5:
			rA = 0

		if rA == 3:
			scoreA = 10 - rB; scoreB = rB
		elif rB == 3:
			scoreA = rA; scoreB = 10-rA
		elif rB == rA:
			scoreA = 5; scoreB = 5
		elif rA - rB == 2:
			scoreA = 7; scoreB = 3
		elif rB - rA == 2:
			scoreA = 3; scoreB = 7
		elif rA > rB:
			scoreA = 6; scoreB = 4
		elif rB > rA:
			scoreA = 4; scoreB = 6
		else:
			AssertionError("Cannot Calculate Score")
		scoreA = scoreA + float(mA) / 1000.0
		scoreB = scoreB + float(mB) / 1000.0
		return [scoreA, scoreB]

	def get_score(self, player_id, Error_state=0):
		rings_A = 0
		rings_B = 0
		markers_A = 0
		markers_B = 0
		positions = list(self.driver.execute_script('return positions;'))
		for row in positions:
			for place in row:
				piece = dict(place)['piece']
				if piece == 2:
					rings_A+=1
				elif piece == 1:
					markers_A+=1
				elif piece == -1:
					markers_B+=1
				elif piece == -2:
					rings_B+=1
		return self.calculate_score(self.rings-rings_A, self.rings-rings_B, markers_A, markers_B, Error_state)[int(player_id)-1]

	def check_won(self):
		required_move = self.driver.execute_script('return required_move;')
		return required_move == 5

	def execute_sequence(self, moves):
		success = 1
		move_list = []
		player_id = self.get_current_player()
		for i, move in enumerate(moves):
			if i % 3 == 2:
				move_list += [move]
				move_success = self.execute_move(' '.join(move_list))
				if move_success == 0:
					return 0
				success = success and move_success
				move_list = []
			else:
				move_list += [move]
		player = self.get_current_player()
		if player_id == player:
			return 0
		return success

	def sign(self, x):
		if(x == 0):
			return 0
		else:
			return x / abs(x)

	def updatePositions(self, positions, move, current_player):
		rows = self.rows
		xring, yring, destx, desty = move
		asign = self.sign(destx-xring)
		bsign = self.sign(desty-yring)
		a = int(asign)
		b = int(bsign)
		xring = int(xring); yring = int(yring)
		flip = 1
		while (xring+a >= 0 and xring+a < rows and yring+b >= 0 and yring+b < rows and abs(positions[int(xring+a)][int(yring+b)]['piece'] != 2 and positions[int(xring+a)][int(yring+b)] != -1)):
			if(positions[int(xring+a)][int(yring+b)]['piece'] == 0):
				if(xring+a == destx and yring+b == desty):
					positions[xring][yring]['piece'] = 1 if(current_player == 0) else -1
					positions[destx][desty]['piece'] = 2 if(current_player == 0) else -2
					flip = 0
		
			if (flip == 1 and abs(positions[int(xring+a)][int(yring+b)]['piece']) == 1):
				positions[int(xring+a)][int(yring+b)]['piece'] *= -1
			
			a += asign
			b += bsign

		return positions

	def get_len_around(self, i, j, marker_val, ring_val, a_, b_, rows, positions):
		a = a_
		b = b_
		c = 0

		while (i+a >= 0 and i+a < rows and j+b >= 0 and j+b < rows):
			if (positions[i+a][j+b]['piece'] != marker_val and positions[i+a][j+b] != ring_val):
				break
			a += a_
			b += b_
			c += 1

		return c

	def get_max_length_created(self, positions, rows, rings, marker_val, ring_val, xring, yring, destx, desty, asign, bsign, m):
		a = 0
		b = 0
		wrong_changes = 0
		correct_changes = 0
		max_len = 0
		while (xring+a >= 0 and xring+a < rows and yring+b >= 0 and yring+b < rows and positions[int(xring+a)][int(yring+b)] != -1):
			i = int(xring+a)
			j = int(yring+b)
			
			if (positions[i][j]['piece'] == marker_val or positions[i][j]['piece'] == ring_val):
				len1 = self.get_len_around(i, j, marker_val, ring_val, 1, 1, rows, positions)
				len2 = self.get_len_around(i, j, marker_val, ring_val, -1, -1, rows, positions)
				len3 = self.get_len_around(i, j, marker_val, ring_val, 0, 1, rows, positions)
				len4 = self.get_len_around(i, j, marker_val, ring_val, 0, -1, rows, positions)
				len5 = self.get_len_around(i, j, marker_val, ring_val, 1, 0, rows, positions)
				len6 = self.get_len_around(i, j, marker_val, ring_val, -1, 0, rows, positions)
				max_len = max(max_len, len1+len2+1, len3+len4+1, len5+len6+1)
				correct_changes += 1
				# print('Position %s %d'%(str(m[(i, j)]), positions[i][j]['piece']), file=sys.stderr)
				# print('Lengths created %d %d %d %d %d %d %d'%(len1, len2, len3, len4, len5, len6, max_len), file=sys.stderr)
			else :
				# print('Position %s %d'%(str(m[(i, j)]), positions[i][j]['piece']), file=sys.stderr)
				wrong_changes += 1


			if (i == destx and j == desty):
				break
			
			a += asign
			b += bsign

		return max_len, wrong_changes, correct_changes

	def get_best_row_state(self, move, current_player, m):
		marker_val = 1 if (current_player == 0) else -1
		ring_val = 2 * marker_val 

		rows = self.rows
		rings = self.rings
		ringx, ringy, destx, desty = move
		asign = self.sign(destx-ringx)
		bsign = self.sign(desty-ringy)
		positions = list(self.driver.execute_script('return positions;'))
		# print('Positions before', file=sys.stderr)
		max_len_b, w_b, r_b = self.get_max_length_created(positions, rows, rings, marker_val, ring_val, ringx, ringy, destx, desty, asign, bsign, m)
		positions_after = self.updatePositions(copy.deepcopy(positions), move, current_player)
		# print('postions after', file=sys.stderr)
		max_len, wrong, right = self.get_max_length_created(positions_after, rows, rings, marker_val, ring_val, ringx, ringy, destx, desty, asign, bsign, m)

		# print('Move %s %s'%(str(m[(ringx, ringy)]), str(m[(destx, desty)])), file=sys.stderr)
		# print('Max len : %d, max len b : %d'%(max_len, max_len_b), file=sys.stderr)

		if(max_len < max_len_b):
			max_len = -1
				
		return max_len, right-wrong

	def get_opponent_worst_state(self, move, current_player, m):
		opp_marker = -1 if (current_player == 0) else 1
		opp_ring = 2 * opp_marker

		rows = self.rows
		rings = self.rings
		ringx, ringy, destx, desty = move
		asign = self.sign(destx-ringx)
		bsign = self.sign(desty-ringy)

		positions = list(self.driver.execute_script('return positions;'))
		# print('Positions before', file=sys.stderr)
		max_len_b, w_b, r_b = self.get_max_length_created(positions, rows, rings, opp_marker, opp_ring, ringx, ringy, destx, desty, asign, bsign, m)

		positions_after = self.updatePositions(copy.deepcopy(positions), move, current_player)
		# print('postions after', file=sys.stderr)
		max_len, wrong, right = self.get_max_length_created(positions_after, rows, rings, opp_marker, opp_ring, ringx, ringy, destx, desty, asign, bsign, m)

		# print('Move %s %s'%(str(m[(ringx, ringy)]), str(m[(destx, desty)])), file=sys.stderr)
		# print('Max len : %d, max len b : %d'%(max_len, max_len_b), file=sys.stderr)

		if(max_len > max_len_b):
			max_len = rings * 2
		
		return max_len-max_len_b, max_len_b, wrong-right # changes to our markers are good

	'''
	## New suggested move types
	# P - Place a ring
	# S - Select a ring
	# M - Move a ring
	# R - Remove a row
	# X - Remove a ring

	## Grid Positions
	# point in center is hexagon 0 and so on outwards
	# topmost point of hexagon is point 0 and pt number increase clockwise with 6*hexring pts on each hexagon
	'''
	def execute_move(self, cmd) :
		moves = cmd.split()
		if len(moves) > 3:
			return self.execute_sequence(moves)
		move_type = moves[0]
		hexagon = int(moves[1])
		position = int(moves[2])

		success = 1
		string_invalid = False

		if (move_type == 'P'): # Place your ring
			self.click_at(hexagon, position)
		elif (move_type == 'S'): # Select a ring
			self.click_at(hexagon, position)
		elif (move_type == 'M'): # Move a ring
			self.click_at(hexagon, position)
		elif (move_type == 'RS'): # Remove a row start
			self.click_at(hexagon, position)
		elif (move_type == 'RE'): # Remove a row end
			self.click_at(hexagon, position)
		elif (move_type == 'X'): # Remove a ring
			self.click_at(hexagon, position)
		else:
			string_invalid = True 
	
		valid = self.check_move_validity()
		won = self.check_won()
		
		if(string_invalid == True or valid == False):
			success = 0
		elif(won == True):
			success = 2
		return success

	def simulate(self, filename):
		with open(filename) as f:
			for line in f.readlines():
				parts = line.split('}')
				part = parts[0] + '}'
				out = json.loads(part)
				exec("self.execute_move(\"" + out['data'] + "\")")

if __name__ == "__main__":
	game = Game(6, 5, 'GUI')
	game.simulate(sys.argv[1])

