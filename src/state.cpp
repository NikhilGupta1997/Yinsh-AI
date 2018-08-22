/**
 * @file state.cpp
 * Function definitions for state manipulation
*/
#include<vector>
#include<iostream>
#include<algorithm>
#include "../include/state.h"

namespace state {

/**
 * North, North-East, North-West, South, South-East, South-West
 */
Point dirs[6] = {{-2, 0 }, {-1, 1}, {-1, -1}, {2, 0}, {1, 1}, {1, -1}};

Point Point::operator+ (const Point& p) {
	Point temp;
	temp.x = x + p.x;
	temp.y = y + p.y;
	return temp;
}

bool Point::operator== (const Point& p) {
	if(x == p.x && y == p.y) {
		return true;
	}
	else {
		return false;
	}
}

bool Board::IsValid(Point p) {
	if(current_board[p.x][p.y] != I &&
	   p.x > -1 && p.x < boardRows &&
	   p.y > -1 && p.y < boardCols) {
		return true;
	}
	else
		return false;
}

Element Board::GetElementAt(int x, int y) {
	//check is valid
	return current_board[x][y];
}

bool Board::AddElementAt(Point p, Element e) {
	// is empty
	if(Board::IsValid(p)) {
		current_board[p.x][p.y] = e;
		return true;
	}
	else
		return false;
}

bool Board::RemoveElementAt(Point p) {
	if(Board::IsValid(p)) {
		current_board[p.x][p.y] = E;
		return true;
	}
	else
		return false;
}

bool Board::MoveElement(Point from, Point to) {
	//from valid
	if(Board::IsValid(to)) {
		current_board[to.x][to.y] = Board::GetElementAt(from.x, from.y);
		current_board[from.x][from.y] = E;
		return true;
	}
	else
		return false;
}

bool Board::FlipMarkers(Point p, Point q, Point dir) {
	if(Board::IsValid(p) && Board::IsValid(q)) {
		
		float x = q.x - p.x;
		float y = q.y - p.y;
		
		if ((x == dir.x || (x / dir.x == int(x / dir.x))) &&
		    (y == dir.y || (y / dir.y == int(y / dir.y)))) {

			if(dir.x != 0 && dir.y != 0) {
				if (x / dir.x != y / dir.y) {
					return false;
				}
			}
			
			for(Point i = p; ; i = i + dir) {
				Element current = Board::GetElementAt(i.x, i.y);
				if(current == B_MARKER) {
					current_board[i.x][i.y] = W_MARKER;
				}
				else if(current == W_MARKER) {
					current_board[i.x][i.y] = B_MARKER;
				}
				if(i == q) {
					break;
				}
			}
			return true;
		}
		else
			return false;
	}
	else
		return false;
}

void GameState::DisplayBoard() {
	for (int i = 0; i <= board.current_board.size(); i++) {
		for (int j = 0; j < board.current_board[0].size(); j++) {
			if (i == 0) {
				if (j == 0) {
					std::cout << "            ";
				}
				std::cout << "    " << j << "    ";
				continue;
			}
			if (j == 0) {
				if (i <= 10) {
					std::cout << " ";
				}
				std::cout << "     " << i - 1 << "     ";
			}
			switch(board.current_board[i-1][j]) {
				case I: 		std::cout << blankFormat;
								break;
				case E: 		std::cout << emptyFormat;
								break;
				case B_RING: 	std::cout << blackRingFormat;
								break;
				case W_RING: 	std::cout << whiteRingFormat;
								break;
				case B_MARKER: 	std::cout << blackMarkerFormat;
								break;
				case W_MARKER: 	std::cout << whiteMarkerFormat;
								break;
			}
		}
		std::cout << "\n\n";
	}
}

bool GameState::AddRing(Point ring_pos, int player_id) {
	if(board.IsValid(ring_pos)) {
		if(player_id == 0 && whiteRings > 0) {
			if(board.GetElementAt(ring_pos.x, ring_pos.y) == E) {
				board.AddElementAt(ring_pos, W_RING);
				whiteRings--;
				return true;
			}
			return false;
		}
		else if(player_id == 1 && blackRings > 0) {
			if(board.GetElementAt(ring_pos.x, ring_pos.y) == E) {
				board.AddElementAt(ring_pos, B_RING);
				blackRings--;
				return true;
			}
			return false;
		}
	}
	return false;
}

bool GameState::MoveRing(Point ring_pos, Point ring_dest, int player_id) {
	Element ring = player_id == 0 ? W_RING : B_RING;
	Element marker = player_id == 0 ? W_MARKER : B_MARKER;
	if(board.IsValid(ring_pos) &&
	   board.GetElementAt(ring_pos.x, ring_pos.y) == ring &&
	   board.GetElementAt(ring_dest.x, ring_dest.y) == E) {

		int dx = ring_dest.x - ring_pos.x;
		int dy = ring_dest.y - ring_pos.y;
		int px = 0, py = 0;
		int dir_index = -1;

		for (int i = 0; i < 6; i++) {
			if(dx != 0 && dirs[i].x != 0 && dx * dirs[i].x > 0) {
				px = dx % dirs[i].x;
			}
			else if ((dx == 0 && dirs[i].x != 0) ||
					 (dx != 0 && dirs[i].x == 0) ||
					 (dx * dirs[i].x < 0)) {
				px = -1;
			}

			if(dy != 0 && dirs[i].y != 0 && dy * dirs[i].y > 0) {
				py = dy % dirs[i].y;
			}
			else if ((dy == 0 && dirs[i].y != 0) ||
					 (dy != 0 && dirs[i].y == 0) ||
					 (dy * dirs[i].y < 0)) {
				py = -1;
			}

			if (px == 0 && py == 0) {
				dir_index = i;
				break;
			}
		}

		if(dir_index == -1) {
			return false;
		}

		std::pair<int, std::vector<Point>> v = ValidPoints(ring_pos, dirs[dir_index]);
		if(std::find(v.second.begin(), v.second.end(), ring_dest) != v.second.end()) {
			AddRing(ring_dest, player_id);
			board.AddElementAt(ring_pos, marker);
			board.FlipMarkers(ring_pos, ring_dest, dirs[dir_index]);
		}
		else {
			return false;
		}
	}
	else {
		return false;
	}
}

bool GameState::IsValidRow(Point row_start, Point row_end, Point dir, int player_id) {
	if(board.IsValid(row_start) &&
	   board.IsValid(row_end)) {
		Element marker = player_id == 0 ? W_MARKER : B_MARKER;
		Point pos = row_start;
		for (int i = 0; i < 5; i++) {
			if(board.GetElementAt(pos.x, pos.y) != marker) {
				return false;
			}
			pos = pos + dir;
		}
		return true;
	}
}

bool GameState::RemoveRowAndRing(Point row_start, Point row_end, Point dir, Point ring_pos, int player_id) {
	if(board.IsValid(row_start) &&
	   board.IsValid(row_end) &&
	   board.IsValid(ring_pos)) {

		Element ring = player_id == 0 ? W_RING : B_RING;
		if(IsValidRow(row_start, row_end, dir, player_id) &&
			board.GetElementAt(ring_pos.x, ring_pos.y) == ring) {
			Point pos = row_start;
			for (int i = 0; i < 5; i++) {
				if(!board.AddElementAt(pos, E)) {
					return false;
				}
				pos = pos + dir;
			}
			if(!board.AddElementAt(ring_pos, E)) {
					return false;
			}
			return true;
		}
		else {
			return false;
		}
	}
	else {
		return false;
	}
}

std::vector<std::pair<int, std::vector<Point>>> GameState::ValidMoves(Point ring_pos) {

	std::vector<std::pair<int, std::vector<Point>>> valid_moves;

	for (int i = 0; i < 6; i++) {
		valid_moves.push_back(ValidPoints(ring_pos, dirs[i]));
	}
	return valid_moves;
}

std::pair<int, std::vector<Point>> GameState::ValidPoints(Point ring_pos, Point dir) {
	if(board.IsValid(ring_pos)) {
		Point i = ring_pos;
		std::vector<Point> valid_points;
		bool first_jump = false;
		bool no_jump = false;
		do {
			i = i + dir;
			if(board.GetElementAt(i.x, i.y) == W_RING ||
		            board.GetElementAt(i.x, i.y) == B_RING) {
				return std::make_pair(0, valid_points);
			}
			else if(board.GetElementAt(i.x, i.y) == E) {
				valid_points.push_back(i);
				if (first_jump) {
					return std::make_pair(1, valid_points);
				}
				else {
					no_jump = true;
				}
			}
			else if(board.GetElementAt(i.x, i.y) == W_MARKER ||
		            board.GetElementAt(i.x, i.y) == B_MARKER) {
				if(no_jump) {
					return std::make_pair(2, valid_points);
				}
				else {
					first_jump = true;
				}
			}

		} while(board.IsValid(i));
	}
}

}

int main() {

	state::GameState G;
	int x, y;
	int player_id = 0;

	clear;
	G.DisplayBoard();

	while(state::whiteRings > 0 || state::blackRings > 0) {
		std::cin >> x >> y;
		state::Point p = {x, y};
		bool check = G.AddRing(p, player_id);
		if(check)
			player_id = !player_id;

		clear;
		G.DisplayBoard();
	}
}
