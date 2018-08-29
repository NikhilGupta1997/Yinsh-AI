import math
import numpy as np
import os
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
 
def create_index_html(size, rings, rows):
    fname = "Yinsh.html"
    context = {
        'size': size,
        'rings': rings,
        'rows': rows
    }
    with open(fname, 'w') as f:
        html = render_template('index.html', context)
        f.write(html)

class Game:

    def __init__(self, n, mode='CUI', time=120):
        if n in board_sizes:
            self.board_size = board_sizes[n]
            self.display_size = display_size[n]
        else:
            raise AssertionError("Number of rings must be either 5, 6 or 7")
        
        # Setup Driver
        create_index_html(self.display_size, n, self.board_size)
        chrome_options = Options()
        chrome_options.add_argument("--disable-infobars")
        if mode != 'GUI':
            chrome_options.add_argument('headless');
        self.driver = webdriver.Chrome(chrome_options=chrome_options)
        abs_path = os.path.abspath('Yinsh.html')
        self.driver.get("file:" + abs_path)
        self.driver.set_window_size(width=self.display_size, height=(self.display_size+60))

        self.spacing = float(self.display_size)/self.board_size 
        self.centerx = int(self.display_size)/2
        self.centery = int(self.display_size)/2

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

    def check_won(self):
        required_move = self.driver.execute_script('return required_move;')
        return required_move == 5

    def execute_sequence(self, moves):
        success = 1
        move_list = []
        for i, move in enumerate(moves):
            if i % 5 == 4:
                move_list += [move]
                success = success and self.execute_move(' '.join(move_list))
                move_list = []
            else:
                move_list += [move]
        return success

    ## New suggested move types
    # P - Place a ring
    # M - Move a ring
    # R - Remove a ring
    # point in center is hexagon 0 and so on outwards
    # topmost point of hexagon is point 0 and pt number increase clockwise with 6*hexring pts on each hexagon
    def execute_move(self, cmd) :
        moves = cmd.split()
        if len(moves) > 5:
            return self.execute_sequence(moves)
        move_type = moves[0]
        moves = [int(m) for m in moves[1:]]

        success = 1
        string_invalid = False
        if (move_type == 'P') :
            # place your ring
            self.click_at(moves[0], moves[1])
        elif (move_type == 'M') :
            # choose a ring
            self.click_at(moves[0], moves[1])
            # move the ring to a valid location
            self.click_at(moves[2], moves[3])
        elif (move_type == 'R') :
            # remove five continuous markers
            self.click_at(moves[0], moves[1])
            # remove a ring
            self.click_at(moves[2], moves[3])
        else :
            string_invalid = True 
    
        valid = self.check_move_validity()
        won = self.check_won()
        
        if(string_invalid == True or valid == False):
            success = 0
        elif(won == True):
            success = 2

        return success

if __name__ == "__main__":
    game = Game(5, "GUI")
    game.execute_move("P 2 0")
    game.execute_move("P 5 16")
    game.execute_move("P 0 0")
    game.execute_move("P 5 14")
    game.execute_move("P 2 9")
    game.execute_move("P 1 3")
    game.execute_move("P 1 0")
    game.execute_move("P 3 0")
    game.execute_move("P 3 6")
    game.execute_move("P 4 4")
    game.execute_move("M 2 9 5 28")
    game.execute_move("M 1 3 3 14")
    game.execute_move("M 5 28 5 26")
    game.execute_move("M 3 0 3 17")
    game.execute_move("M 0 0 1 2")
    game.execute_move("M 4 4 2 2")
    game.execute_move("M 1 2 3 1")
    game.execute_move("M 5 16 1 4")
    game.execute_move("M 3 1 1 1")
    game.execute_move("M 2 2 4 6")
    game.execute_move("M 1 0 4 3")
    game.execute_move("M 3 14 5 24")
    game.execute_move("M 3 6 3 9")
    game.execute_move("M 4 6 3 4")
    game.execute_move("M 4 3 3 3")
    game.execute_move("M 1 4 2 8")
    game.execute_move("M 5 26 5 27")
    game.execute_move("M 3 17 1 5")
    game.execute_move("M 2 0 2 6")
    game.execute_move("M 3 4 2 7")
    game.execute_move("M 1 1 2 3")
    game.execute_move("M 5 14 4 16")
    game.execute_move("M 2 6 3 5")
    game.execute_move("M 4 16 4 18")
    game.execute_move("M 5 27 5 29")
    game.execute_move("M 4 18 2 10")
    game.execute_move("M 3 9 4 11")
    game.execute_move("M 2 8 3 11")
    # game.execute_move("M 4 11 2 1")
    # game.execute_move("R 0 0 2 10")
    # game.execute_move("M 3 3 0 0")

