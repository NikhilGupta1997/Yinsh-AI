# Yinsh
Simulator supporting smart agents and a user interface for Yinsh, an abstract strategy board game.

## Details
This is a course assignment for the graduate-level Artificial Intelligence course taught by [**Prof. Mausam**](http://homes.cs.washington.edu/~mausam).  
The assignment documentation can be found [here](statement.pdf)

### Teaching Assistants
+ [Nikhil Gupta](https://github.com/NikhilGupta1997)
+ [Kolluru Sai Keshav](https://github.com/SaiKeshav)
+ [Rishubh Singh](https://github.com/13dexter)

## Rules
The rules of the game can be found [here](http://www.gipf.com/yinsh/rules/rules.html)

## Dependencies
+ Selenium
+ Jinja2
+ Chrome Webdriver

## Main Files
+ `game.py` - This has an instance of the game. It can be run locally to hand play a game of Yinish or re-play a recorded game. Should be run in `GUI` mode to make game board visible.
+ `RandomPlayer.py` - This is an implementation of a random bot. It is a good place to start understanding the flow of the game and the various game states.
+ `client.py` - This will encapsulate your process and help it connect to the game server. 
  > `ip` (mandatory) - The Server IP.  
  > `port` (mandatory) - The Server Port.  
  > `exe` (mandatory) - The Executable.  
  > `mode` (optional) - The View Mode ('GUI' / 'CUI'). Default: 'CUI'  
+ `server.py` - This connects the clients and manages the transfer of information. 
  > `port` (mandatory) - The Server Port.  
  > `ip` (optional) - The Server IP. Default: 0.0.0.0   
  > `n` (optional) - The Board Size. Default: 5  
  > `s` (optional) - Sequence Length. Default: 5  
  > `NC` (optional) - Number of Clients. Default: 2  
  > `TL` (optional) - Time Limit. Default:150  
  > `LOG` (optional) - The Log File.  

## Run Instructions
Here are the sample instructions used to match two random players against each other over the server network.
### Setup Server
`python server.py 10000 -n 5 -s 5 -NC 2 -TL 150 -LOG server.log`
### Setup Client 1
`python  client.py 0.0.0.0 10000 RandomPlayer.py -mode GUI`
### Setup Client 2
`python  client.py 0.0.0.0 10000 RandomPlayer.py`

## Gameplay
The game play consists of the players executing a sequence of moves in a single turn.
A move is a triple: `movetype` `hexagon` `position`.  

### Movetype
+ P - Place a ring
+ S - Select a ring
+ M - Move a ring
+ RS - Remove a row Start
+ RE - Remove a row End
+ X - Remove a ring

### Hexagon
The board is divided into hexagons. The center point is referenced as hexagon 0. It is surrounded by hexagon 1, then 2 and so on.

### Position
For a selected hexagon, the position refers to a particular point on the hexagon. Hexagon h will have 6\*h positions referenced from 0 to 6\*h-1. The topmost point is point 0 with increasing postions following in a clockwise direction. 

### Examples
#### Place a Ring
To place a ring on hexagon 1 and position 2 we will play the move 
`P 1 2`

#### Move a Ring
To move a ring from hexagon 1 and position 2 to hexagon 2 postion 4 we will play the move sequence
`S 1 2 M 2 4`

#### Remove a Row and Ring
To remove a row we have to specify the start of the row using **RS** and the end of the row using **RE** 
`RS 1 2 RE 4 16`.  
This is followed by removing any ring 
`X 3 4`.  
In general a Remove Row will be triggered by a Move Ring move sequence. Hence the overall move sequence will look like 
`S 1 2 M 2 4 RS 1 2 RE 4 16 X 3 4`. 

## Scoring
At the end of a game both players will be given a score.
The game score consists of two parts: 
1) `The Ring Margin` 
2) `The Marker Margin`

### The Ring Margin
This score will be based on the extent of victory. It is calculated as follows:  

| Your Rings Removed | Opponents Rings Removed | Ring Margin Score |  
| ------------- | ------------- | ------------- |
| 3 | 0 | 10 |  
| 3 | 1 | 9 |  
| 3 | 2 | 8 |  
| 2 | 0 | 7 |  
| 2 | 1 | 6 |  
| 1 | 0 | 6 |  
| 2 | 2 | 5 |  
| 1 | 1 | 5 |  
| 0 | 0 | 5 |  
| 0 | 1 | 4 |  
| 1 | 2 | 4 |  
| 0 | 2 | 3 |  
| 2 | 3 | 2 |  
| 1 | 3 | 1 |  
| 0 | 3 | 0 |  

### The Marker Margin
This score directly depends on the number of markers you have left at the end of the game. It is calculated as follows:  
`Marker Margin Score = # Markers Remaining / 1000`

### Final Score
The final score is simply: `Ring Margin Score.Marker Margin Score`
Example. Assume the following:  
Player 1 has removed 3 rings and has 12 markers left on the board.  
Player 2 has removed 1 ring and has 17 markers left on the board.  
Player 1 score will be: **9.012**  
Player 2 score will be: **1.017**  

Note) Incase a player suffers a TIMEOUT or INVALID move, he/she will automatically lose the gane and it will count as a (*x*-3) defeat towards the player and a (3-*x*) win for the opponent, where *x* is the number of rings already picked up by the player.


