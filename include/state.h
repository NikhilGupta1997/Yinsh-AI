/**
 * @file state.h
 * Function declarations for Yinsh's game state
 */
#ifndef STATE_STATE_H
#define STATE_STATE_H

#include <vector>
#include <utility>

#define clear	std::cout << "\033c\n";

namespace state {

/**
 * @brief      Total number of remaining rings that can be placed on board. When
 *             rings are removed after row is formed, count goes to negative
 */
int whiteRings = 5;
int blackRings = 5;
const int boardRows = 19;
const int boardCols = 11;

/**
 * @brief      Output format for printing different elements
 */
std::string blankFormat			= "         ";
std::string emptyFormat			= "    \033[1;31m*\033[0m    ";
std::string blackRingFormat		= "    \033[1;30;47mR\033[0m    ";
std::string whiteRingFormat		= "    \033[1;37mR\033[0m    ";
std::string blackMarkerFormat	= "    \033[1;37;40mM\033[0m    ";
std::string whiteMarkerFormat	= "    \033[1;37mM\033[0m    ";

/**
 * @brief      A struct for packing the coordinates
 */
struct Point {
	int x;
	int y;

	Point operator+ (const Point& p);
	bool operator== (const Point& p);
};

/**
 * @brief      Enum for different types of elements possible in the board
 * 			   I = Invalid board position
 * 			   E = Empty board position
 * 			   B_RING = Black ring
 * 			   W_RING = White ring
 * 			   B_MARKER = Black marker
 * 			   W_MARKER = White marker
 */
enum Element {
	I, E, B_RING, W_RING, B_MARKER, W_MARKER
};

/**
 * Game board for the simulation
 */
class Board {
public:
	std::vector<std::vector<Element> > current_board = 
	{
		{I, I, I, I, E, I, E, I, I, I, I},
		{I, I, I, E, I, E, I, E, I, I, I},
		{I, I, E, I, E, I, E, I, E, I, I},
		{I, E, I, E, I, E, I, E, I, E, I},
		{I, I, E, I, E, I, E, I, E, I, I},
		{I, E, I, E, I, E, I, E, I, E, I},
		{E, I, E, I, E, I, E, I, E, I, E},
		{I, E, I, E, I, E, I, E, I, E, I},
		{E, I, E, I, E, I, E, I, E, I, E},
		{I, E, I, E, I, E, I, E, I, E, I},
		{E, I, E, I, E, I, E, I, E, I, E},
		{I, E, I, E, I, E, I, E, I, E, I},
		{E, I, E, I, E, I, E, I, E, I, E},
		{I, E, I, E, I, E, I, E, I, E, I},
		{I, I, E, I, E, I, E, I, E, I, I},
		{I, E, I, E, I, E, I, E, I, E, I},
		{I, I, E, I, E, I, E, I, E, I, I},
		{I, I, I, E, I, E, I, E, I, I, I},
		{I, I, I, I, E, I, E, I, I, I, I}
	};

	/**
	 * @brief      Determines if valid board position
	 *
	 * @param[in]  p     Point p
	 *
	 * @return     True if valid position, False otherwise.
	 */
	bool IsValid(Point p);

	/**
	 * @brief      Gets the element at given position
	 *
	 * @param[in]  x     x coordinate
	 * @param[in]  y     y coordinate
	 *
	 * @return     Type of element at given position
	 */
	Element GetElementAt(int x, int y);

	/**
	 * @brief      Adds an element at given position
	 *
	 * @param[in]  p     position to add at
	 * @param[in]  e     type of element to be added
	 *
	 * @return     True if successful, False if invalid board position
	 */
	bool AddElementAt(Point p, Element e);

	/**
	 * @brief      Removes an element at given position
	 *
	 * @param[in]  p     position to remove at
	 *
	 * @return     True if successful, False if invalid board position
	 */
	bool RemoveElementAt(Point p);

	/**
	 * @brief      Move element from a position to another
	 *
	 * @param[in]  from  source position
	 * @param[in]  to    destination position
	 *
	 * @return     True if successful, False if invalid board position
	 */
	bool MoveElement(Point from, Point to);

	/**
	 * @brief      Flips marker type
	 *
	 * @param[in]  p     flipping start position
	 * @param[in]  q     flipping end position
	 * @param[in]  dir   The direction from start to end
	 *
	 * @return     True if successful, False if any point is an invalid board
	 *             position
	 */
	bool FlipMarkers(Point p, Point q, Point dir);
};

class GameState {
	int playerAScore, playerBScore;
	int currentPlayer;
/*	TurnMode turnMode;*/
	Board board;
public:

	/**
	 * @brief      Prints the 11x19 Yinsh gameboard
	 */
	void DisplayBoard();

	/**
	 * @brief      Adds ring at given position (if move valid).
	 *
	 * @param[in]  ring_pos   Position to place ring
	 * @param[in]  player_id  The player identifier
	 *
	 * @return     returns false if move invalid (no rings left, illegal
	 *             position or out of board)
	 */
	bool AddRing(Point ring_pos, int player_id);

	/**
	 * @brief      Moves ring from point A to point B (if move valid).
	 *
	 * @param[in]  ring_pos   Ring's position
	 * @param[in]  ring_dest  Ring's destination
	 * @param[in]  player_id  The player identifier
	 *
	 * @return     returns false if move invalid (illegal position or out of
	 *             board)
	 */
	bool MoveRing(Point ring_pos, Point ring_dest, int player_id);

	/**
	 * @brief      Determines if given points form row.
	 *
	 * @param[in]  row_start  Start of row
	 * @param[in]  row_end    End of row
	 * @param[in]  dir        The direction from start to end
	 * @param[in]  player_id  The player identifier
	 *
	 * @return     True if valid row, False otherwise.
	 */
	bool IsValidRow(Point row_start, Point row_end, Point dir, int player_id);

	/**
	 * @brief      Removes a row of markers from Point A to Point B (if move
	 *             valid)
	 *
	 * @param[in]  row_start  Start of row
	 * @param[in]  row_end    End of row
	 * @param[in]  dir        The direction from start to end
	 * @param[in]  ring_pos   Position of ring to remove
	 * @param[in]  player_id  The player identifier
	 *
	 * @return     returns false if row greater than 5, points doesn't form row,
	 *             if valid row not formed or invalid ring position
	 */
	bool RemoveRowAndRing(Point row_start, Point row_end, Point dir, Point ring_pos, int player_id);

	/**
	 * @brief      Returns all valid points in every direction
	 *
	 * @param[in]  ring_pos  Starting position of ring
	 *
	 * @return     Returns vector of pairs (int, vector<point>) for each direction
	 *             Case 1
	 *             int(0): Blocked by markers followed by ring or just a ring
	 *             Vector<point>: Empty
	 *             Case 2
	 *             int(1): Not immediately blocked by a marker
	 *             Point(x,y): All valid positions from ring to till before the marker
	 *             Case 3
	 *             int(2): Blocked by only a non empty set of markers
	 *             Point(x,y): First position after markers
	 */
	std::vector<std::pair<int, std::vector<Point>>> ValidMoves(Point ring_pos);

	/**
	 * @brief      Returns all valid points in a given direction
	 *
	 * @param[in]  ring_pos  The ring position
	 * @param[in]  dir       The direction
	 *
	 * @return     Returns a pair consisting of an int (case) and a vector of all points
	 *             in a given direction
	 */
	std::pair<int, std::vector<Point>> ValidPoints(Point ring_pos, Point dir);

	/**
	 * @brief      Returns all rows formed for player
	 *
	 * @param[in]  player_id  Player ID
	 *
	 * @return     Returns vector of pairs(start, end) for all rows
	 */
	std::vector<std::pair<Point, Point>> RowsFormed(int player_id);

	/**
	 * @brief      Undo's the given action from the board
	 *
	 * @param[in]  board   The board
	 * @param[in]  action  The action can be either of 3 things: 
	 *                     1. Place ring,
	 *                     2. Place marker and move ring
	 *                     3. Remove row and ring
	 *
	 * @return     returns board's configuration after undo is performed
	 */

	/*Board UndoAction(Board board, Action action);*/
};

}

#endif //STATE_STATE_H
