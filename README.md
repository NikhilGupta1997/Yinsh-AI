# Yinsh
Simulator supporting smart agents and a user interface for Yinsh, an abstract strategy board game.

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
  > `NC` (optional) - Number of Clients. Default: 2  
  > `TL` (optional) - Time Limit. Default:150  
  > `LOG` (optional) - The Log File.  

## Run Instructions
Here are the sample instructions used to match two random players against each other over the server network.
### Setup Server
`python server.py 10000 -n 5 -NC 2 -TL 150 -LOG server.log`
### Setup Client 1
`python  client.py 0.0.0.0 10000 RandomPlayer.py -mode GUI`
### Setup Client 2
`python  client.py 0.0.0.0 10000 RandomPlayer.py`
