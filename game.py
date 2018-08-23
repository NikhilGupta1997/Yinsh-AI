from selenium import webdriver
import math
import numpy as np
import os

class Game:

    def __init__(self, n) :
        self.board_size = n
        self.driver = webdriver.Firefox()
        abs_path = os.path.abspath('Yinsh.html')
        self.driver.get("file:" + abs_path)
        self.spacing = 876.0/11
        self.centerx = 438
        self.centery = 438

    def get_corner_coord(self, corner, hexagon) :
        x_mov = self.spacing * hexagon * math.sin(math.radians(corner * 60))
        y_mov = -(self.spacing * hexagon * math.cos(math.radians(corner * 60)))
        return np.array([self.centerx + x_mov, self.centery + y_mov])

    def get_non_corner_coord(self, corner1, corner2, point_num_side, hexagon) :
        corner1_coord = get_corner_coord(corner1, hexagon)
        corner2_coord = get_corner_coord(corner2, hexagon)
        pt_from_first_corner = point % hexagon
        return ((corner1_coord * point_num_side / hexagon) + (corner2_coord * (hexagon - point_num_side) / hexagon))

    def click_at(hexagon, point, action) :
        el = self.driver.find_elements_by_id("PieceLayer")
        action = webdriver.common.action_chains.ActionChains(self.driver)
        if (hexagon == 0) :
                action.move_to_element_with_offset(el[0], 438, 438)
        else :
            if (point % hexagon == 0) :
                pt_coord = get_corner_coord(point / hexagon, hexagon)
                action.move_to_element_with_offset(el[0], pt_coord[0], pt_coord[1])
            else :
                pt_coord = get_non_corner_coord(point // hexagon, point // hexagon + 1, point % hexagon)
                action.move_to_element_with_offset(el[0], pt_coord[0], pt_coord[1])
        action.click()
        action.perform()

    # ! : place ring
    # @ : move ring
    # # : remove 
    # point in center is hexagon 0 and so on outwards
    # topmost point of hexagon is point 0 and pt number increase clockwise with 6*hexring pts on each hexagon
    def execute_move(self, move_cmd) :
        moves = move_cmd.split()

        if (moves[0] == '!') :
            # place your ring
            click_at(moves[1], moves[2])

        elif (moves[0] == '@') :
            # choose a ring
            click_at(moves[1], moves[2])
            # move the ring to a valid location
            click_at(moves[3], moves[4])

        elif (moves[0] == '#') :
            # remove five continuous markers
            click_at(moves[1], moves[2])
            # remove a ring
            click_at(moves[3], moves[4])

        else :
            print ('INVALID MOVE')