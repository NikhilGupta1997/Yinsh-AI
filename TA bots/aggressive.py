from __future__ import print_function 

from game import Game
import math
import random
import sys
import time

class RandomPlayer:

    def __init__(self):
        data = sys.stdin.readline().strip().split() # Initialize Environment
        self.player = int(data[0]) - 1 # player can have values 0 and 1
        self.n = int(data[1]) # n can have values 5, 6, or 7
        self.time_left = int(data[2])
        self.seq = int(data[3])
        self.game = Game(self.n, self.seq)
        self.RingPos = {}
        self.play()

    def isValid(self, move):
        return self.game.is_move_valid(move[0], move[1], move[2], move[3])

    def placeRing(self):
        movetype = 'P'
        hexagon = random.randint(0,self.n)
        position = random.randint(0,max(0,6*hexagon-1))
        if hexagon==self.n and position%self.n==0:
            position+=1
        return '{type} {hex} {pos}'.format(type=movetype, hex=hexagon, pos=position), len(self.RingPos), hexagon, position

    def selectRing(self):
        movetype = 'S'
        ring_num = random.randint(0,self.n-1)
        while ring_num not in self.RingPos:
            ring_num = random.randint(0,self.n-1)
        ring = self.RingPos[ring_num]
        return '{type} {hex} {pos}'.format(type=movetype, hex=ring[0], pos=ring[1]), ring_num

    def moveRing(self):
        movetype = 'M'
        hexagon = random.randint(0,self.n)
        position = random.randint(0,max(0,6*hexagon-1))
        if hexagon==self.n and position%self.n==0:
            position+=1
        return '{type} {hex} {pos}'.format(type=movetype, hex=hexagon, pos=position), hexagon, position

    def aggression(self, move, player, movesMap) :
        max_len, num_markers = self.game.get_best_row_state(move, player, movesMap)
        # print('Move: %s Max Len: %d, Num Markers: %d'%(move, max_len, num_markers), file=sys.stderr)
        return (max_len*1.0 + num_markers*0.001)

    def selectAndMoveRing(self):
        selectType = 'S'
        moveType = 'M'

        move_ring_num = -1
        hexagon = -1
        position = -1

        movesMap = self.game.boardToHexMap(self.n)
        validMoves = self.game.getAllValidMoves(self.RingPos)
        maxAggress = -1
        for move in validMoves:
            move_aggression = self.aggression(move, self.player, movesMap)
            if (maxAggress < move_aggression) : # and the move has a higher aggression than any previous valid moves
                src_ring = movesMap[(move[0], move[1])]
                dst_ring = movesMap[(move[2], move[3])]
                # print("Moves %d %d %d %d"%(move[0], move[1], move[2], move[3]), file=sys.stderr)
                # print("Source Ring: "+str(src_ring), file=sys.stderr)
                maxAggress = move_aggression # update move and aggression score

        for move_ring_num in self.RingPos:
            if(src_ring == self.RingPos[move_ring_num]):
                break
        # print('Ring Pos '+str(self.RingPos[move_ring_num]), file=sys.stderr)

        return '{type} {hex} {pos}'.format(type=selectType, hex=src_ring[0], pos=src_ring[1]), move_ring_num, '{type} {hex} {pos}'.format(type=moveType, hex=dst_ring[0], pos=dst_ring[1]), dst_ring[0], dst_ring[1] 



    def removeRowStart(self):
        movetype = 'RS'
        hexagon = random.randint(0,self.n)
        position = random.randint(0,max(0,6*hexagon-1))
        if hexagon==self.n and position%self.n==0:
            position+=1
        return '{type} {hex} {pos}'.format(type=movetype, hex=hexagon, pos=position)

    def removeRowEnd(self):
        movetype = 'RE'
        hexagon = random.randint(0,self.n)
        position = random.randint(0,max(0,6*hexagon-1))
        if hexagon==self.n and position%self.n==0:
            position+=1
        return '{type} {hex} {pos}'.format(type=movetype, hex=hexagon, pos=position)

    def removeRing(self):
        movetype = 'X'
        ring_num = random.randint(0,self.n-1)
        while ring_num not in self.RingPos:
            ring_num = random.randint(0,self.n-1)
        ring = self.RingPos[ring_num]
        return '{type} {hex} {pos}'.format(type=movetype, hex=ring[0], pos=ring[1]), ring_num

    def play_move_seq(self, move_seq):
        moves = ' '.join(move_seq) + '\n'
        sys.stdout.write(moves)
        sys.stdout.flush()

    def play(self):
        if self.player == 1:
            move = sys.stdin.readline().strip()
            self.game.execute_move(move)
        while True: # Keep playing moves till game is over
            move_seq = []
            while True: # Loop till valid move sequence is found
                state = self.game.check_player_state()
                if state == 0: ## Place Rings
                    moveP, i, hex, pos = self.placeRing()
                    success = self.game.execute_move(moveP)
                    if success != 0:
                        self.RingPos[i] = (hex, pos)
                        move_seq.append(moveP)
                        break
                elif state == 1: ## Select a Ring and the Move to Valid Postion
                    moveS, i, moveM, hex, pos = self.selectAndMoveRing()
                    # print('Ending '+str(self.RingPos[i])+" "+str(hex)+" "+str(pos), file=sys.stderr)
                    # print('moveS '+str(moveS)+' moveM '+str(moveM), file=sys.stderr)
                    self.game.execute_move(moveS)
                    state = self.game.check_player_state()
                    success = self.game.execute_move(moveM)
                    if success != 0:
                        self.RingPos[i] = (hex, pos)
                        state = self.game.check_player_state()
                        move_seq.append(moveS); move_seq.append(moveM)
                        if state != 3:
                            break
                elif state == 2:
                    raise AssertionError("The player state cannot be 2 after a sequence of valid moves")
                elif state == 3 or state == 6: ## Select Row to Remove (State 6 if other players your row)
                    move_start = self.removeRowStart()
                    success = self.game.execute_move(move_start)
                    if success != 0:
                        while True:
                            move_end = self.removeRowEnd()
                            success = self.game.execute_move(move_end)
                            if success != 0:
                                break
                        state = self.game.check_player_state()
                        move_seq.append(move_start); move_seq.append(move_end)
                elif state == 4 or state == 7: ## Select Ring to Remove (State 7 if other players your row)
                    move, i = self.removeRing()
                    del self.RingPos[i]
                    self.game.execute_move(move)
                    move_seq.append(move)
                    if state == 7:
                        continue
                    state = self.game.check_player_state()
                    if state != 3:
                        break
            self.play_move_seq(move_seq)
            
            ## Execute Other Player Move Sequence
            move = sys.stdin.readline().strip()
            self.game.execute_move(move)

random.seed(1)
random_player = RandomPlayer()