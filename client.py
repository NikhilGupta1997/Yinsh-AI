import argparse
import math
import socket,sys,json,os,time,pdb

from Communicator import Communicator
from game import Game

class Client(Communicator):
	def __init__(self):
		self.GAME_TIMER = 100000 # in Milli Seconds
		self.NETWORK_TIMER = 150
		super(Client,self).__init__()
		pass    
	
	def setNetworkTimer(self,Time_in_Seconds):
		self.NETWORK_TIMER = Time_in_Seconds
	
	def getNetworkTimer(self):
		return self.NETWORK_TIMER

	def getGameTimer(self):
		return self.GAME_TIMER // 1000
	
	def setGameTimer(self,Time_in_Seconds):
		self.GAME_TIMER = Time_in_Seconds * 1000

	def CheckExeFile(self,Execution_Command,Executable_File):
		""" Checks the Existance of the Executable File and
				if the extension of the file matches the command used to run it
		Args:
				Execution_Command : Command used to execute the Executable File (sh, python ./ etc)
				Executable_File : The Executable File
		Returns: 
				None                    
		 """
		Extension = Executable_File.split('.')
		if(len(Extension) == 1):
			return False
		Extension = Extension[-1]
		if(os.path.isfile(Executable_File)):
			if(Execution_Command == './' or Execution_Command == 'sh'):
				if(Extension == 'sh' or Extension == 'o'):
					return True
				else:
					return False
			elif(Execution_Command == 'java'):
				if(Extension == 'java'):
					return True
				else:
					return False
			elif(Execution_Command == 'python'):
				if(Extension == 'py'):
					return True
				else:
					return False
		else:
			return False
	
	def CreateChildProcess(self,Execution_Command,Executable_File):
		""" Creates a Process, with which the client communicates.
				Checks the existance of the Executable_File and some basic
				checks for whether the Execution_Command used to run the code
				matches the extension of the Executable File
				Prints if error is found
		Args:
				Execution_Command : Command used to execute the Executable File (sh, python ./ etc)
				Executable_File : The Executable File
		Returns: 
				None
		"""
		if(self.CheckExeFile(Execution_Command,Executable_File)):
			super(Client,self).CreateChildProcess(Execution_Command,Executable_File)
		else:
			print 'ERROR : EITHER FILE ', Executable_File,' DOES NOT EXIST',
			print 'OR THE EXECUTION COMMAND TO RUN THE FILE ',Execution_Command,' IS INCORRECT'                     

	def Connect2Server(self,server_address,port_no):
		"""Connects to server with given IP Address and Port No. 
		Args: 
				server_address : IP Address
				Port No : Port Number
		Returns: 
				None
		"""                             
		self.clientSocket = socket.socket()
		self.clientSocket.connect((server_address,port_no))             
		super(Client,self).setSocket(self.clientSocket,self.NETWORK_TIMER)
			
	def SendData2Server(self,data):         
		""" Sends data (a dictionary) to the Server as a json object
		In case action == 'FINISH', closes the pipe on this end
		Args:
				data : a dictionary of the following format:
				{
						meta : The meta data in case of an error ( UNEXPECTED STOP, WRONG MOVE etc.), otherwise ''      
						action : The action to be taken (KILLPROC, NORMAL, FINISH, INIT)
						data : Move String or '' in case of an Error
				}
		Returns:                        
				success_flag : True if successful in sending, False otherwise
		"""                             
		if((data['action'] == 'KILLPROC') or (data['action'] == 'FINISH')):
			super(Client,self).closeChildProcess()          
		
		sendData = json.dumps(data)
		success_flag =  super(Client,self).SendDataOnSocket(sendData)
		if(not success_flag):
			print 'ERROR : FAILED TO SEND DATA TO SERVER'
			super(Client,self).closeSocket()
		elif((data['action'] == 'KILLPROC') or (data['action'] == 'FINISH')):
			super(Client,self).closeSocket()
		return success_flag

	
	def RecvDataFromServer(self):
		""" Receives data from the Server as a string, and Returns the Move.
				Uses self.NETWORK_TIMER to decide how long to wait for input from Server
				In case of an error, prints the error, and closes the pipe process
				In case the last move is made by other client, closes the pipe process and 
				returns the data
		Args:
				None
		Returns:
				retData : String (Move) in case there are no errors, otherwise None
		"""             
		data = super(Client,self).RecvDataOnSocket()            
		retData = None
		if(data == None):                       
			print 'ERROR : TIMEOUT ON SERVER END'
			super(Client,self).closeChildProcess()
			super(Client,self).closeSocket()
		else:
			data = json.loads(data)
			if(data['action'] == 'NORMAL' or data['action'] == 'INIT'):
					retData = data['data']                  
			elif(data['action'] == 'KILLPROC'):
					print 'ERROR : ' + data['meta'] + ' ,ON OTHER CLIENT'
					super(Client,self).closeChildProcess()
					super(Client,self).closeSocket()                                
			elif(data['action'] == 'FINISH'):
					super(Client,self).closeChildProcess()                          
					super(Client,self).closeSocket()
					retData = data['data']
		return retData
	
	def RecvDataFromProcess(self):
		"""Receives Data from the process. This does not implement checks 
				on the validity of game moves. Hence, the retData from here is not final
				, i.e, it may be different than what is sent to the server.
				Note: The Action 'FINISH' is set internally by game, not by the network
				Handles Errors like Exceptions thrown by process. 
				However, In case of a timeout, 'FINISH' may be thrown
				Uses self.GAME_TIMER to decide how long to wait for a timeout.
				For both the above cases, prints the error msg and closes the connection to 
				the process. 
		Args:
				None
		Returns:
				retData : dictionary of the nature : 
								  {
												meta : '' / MetaData in case of an Error
												action : 'NORMAL' / 'KILLPROC' in case of an Error
												data : 'DATA' / '' in case of an Error 
										}
								  None in case of an error
		"""             
		start_time = time.time()
		BUFFER_TIMER = int(math.ceil(self.GAME_TIMER / 1000.0))
		print 'Time remaining is: ' + str(BUFFER_TIMER) + 's'
		data = super(Client,self).RecvDataOnPipe(BUFFER_TIMER)
		end_time = time.time()
		retData = None          
		if(data == None):                                                               
			# 1 Milli Second Default
			time_delta = max(1,int((end_time - start_time) * 1000))
			self.GAME_TIMER -= time_delta
			if(self.GAME_TIMER > 0):
				print 'ERROR : THIS CLIENT STOPPED UNEXPECTEDLY OR TIMED OUT'
				super(Client,self).closeChildProcess()                  
				retData = {'meta':'UNEXPECTED STOP','action':'KILLPROC','data':''}
			else:
				retData = {'meta':'TIMEOUT','action':'FINISH','data':''}
				print 'ERROR : THIS CLIENT RAN OUT OF TIME!' 
		else:                   
			# 1 Milli Second Default
			time_delta = max(1,int((end_time - start_time) * 1000))
			self.GAME_TIMER -= time_delta
			if(self.GAME_TIMER > 0):
				retData = {'meta':'','action':'NORMAL','data':data}
			else:
				retData = {'meta':'TIMEOUT','action':'FINISH','data':''}
				print 'ERROR : THIS CLIENT RAN OUT OF TIME!'                   
		return retData
	
	
	def SendData2Process(self,data):
		""" Sends Data (Move) to the process. Handles the case if the process being communicated with has closed.
		Args: 
				data : string data, to send the process (a game move)
		Returns:
				success_flag : A boolean flag to denote the data transfer to the process was successful or not.
		"""             
		if(data[-1] != '\n'):
			data = data + '\n'
		success_flag = super(Client, self).SendDataOnPipe(data)         
		if(success_flag == False):
			print 'ERROR : FAILED TO SEND DATA TO PROCESS'
			super(Client,self).closeChildProcess()                                  
		return success_flag

def game_loop(args):
	## Create Client Process
	client = Client()
	if args.exe.endswith('.py'):
		client.CreateChildProcess('python', args.exe)
	elif args.exe.endswith('.sh'):
		client.CreateChildProcess('sh', args.exe)
	else:
		client.CreateChildProcess('sh', args.exe)
	
	## Connect Client with Server
	client.Connect2Server(args.ip, args.port)
	server_string = client.RecvDataFromServer()
	if(server_string is None):
		print 'ERROR IN SETTING UP CONNECTIONS. SORRY'
		sys.exit(0)
	
	## Initialize Client
	server_string_list = server_string.strip().split()
	player_id = server_string_list[0]
	board_size = int(server_string_list[1])
	game_timer = int(server_string_list[2])
	seq_length = int(server_string_list[3])
	client.setGameTimer(game_timer)
	print '***********************************\n'
	print '-> You are player ' + str(player_id)
	print '-> You are alloted a time of ' + str(game_timer) + 's\n'
	print '***********************************\n'
	game = Game(board_size, seq_length, args.mode, game_timer)        

	client.SendData2Process(server_string) ## Initialize Process

	''' Execute Game Moves '''
	if player_id == '2':
		move = client.RecvDataFromServer()
		if move:
			move = move.strip()
			print "Player 1 played : " + move
			success = game.execute_move(move)                       
			client.SendData2Process(move)
		else:
			sys.exit(0)     
	
	while(True):
		### Execute Current Player's Move
		move = client.RecvDataFromProcess()                                             
		if move['action'] == 'KILLPROC':
			move['meta'] = move['meta'] + ' BY PLAYER ' + player_id + \
							' : Player ' +  str(player_id) + ' SCORE : ' + str(game.get_score(player_id, player_id)) +  \
							' : Player ' +  str(int(player_id)%2+1) + ' SCORE : ' + str(game.get_score(int(player_id)%2+1, player_id))
			client.SendData2Server(move)
			break
		if move['action'] == 'FINISH': # TIMEOUT
			move['meta'] = move['meta'] + ' BY PLAYER ' + player_id + \
							' : Player ' +  str(player_id) + ' SCORE : ' + str(game.get_score(player_id, player_id)) +  \
							' : Player ' +  str(int(player_id)%2+1) + ' SCORE : ' + str(game.get_score(int(player_id)%2+1, player_id))
			client.SendData2Server(move)
			break
		move['data'] = move['data'].strip()
		print "You played : " + move['data']
		success = game.execute_move(move['data'])
		message = {}
		
		### Success
		# 0: Invalid State
		# 1: Normal State
		# 2: Game Over (Someone Wins) Note) Even Drawn State Will result in Game Over
		if success == 0:
			message['data'] = ''
			message['action'] = 'KILLPROC'
			message['meta'] = 'INVALID MOVE BY PLAYER ' + player_id + \
								' : Player ' +  str(player_id) + ' SCORE : ' + str(game.get_score(player_id, player_id)) +  \
								' : Player ' +  str(int(player_id)%2+1) + ' SCORE : ' + str(game.get_score(int(player_id)%2+1, player_id))
			print 'INVALID MOVE ON THIS CLIENT'
		elif success == 1:
			message = move
		elif success == 2:
			message['action'] = 'FINISH'
			message['data'] = move['data']
			message['meta'] = 'Player ' +  str(player_id) + ' SCORE : ' + str(game.get_score(player_id)) +  \
							' : Player ' +  str(int(player_id)%2+1) + ' SCORE : ' + str(game.get_score(int(player_id)%2+1))
			print 'YOU WIN!'
			if player_id == '1':
				print 'Your Score : ' + str(game.get_score(1))
				print 'Opponent\'s Score : ' + str(game.get_score(2))
			else:
				print 'Your Score : ' + str(game.get_score(2))
				print 'Opponent\'s Score : ' + str(game.get_score(1))

		client.SendData2Server(message)
		if message['action'] == 'FINISH' or message['action'] == 'KILLPROC':
			break
		
		## Listen to Other Player's Move
		move = client.RecvDataFromServer()
		if move:
			move = move.strip()
			if player_id == '1':
				print "Player 2 played : " + move
			else:
				print "Player 1 played : " + move
			success = game.execute_move(move)
			if success == 2:
				print 'OTHER PLAYER WINS!'
				if player_id == '1':
					print 'Your Score : ' + str(game.get_score(1))
					print 'Opponent\'s Score : ' + str(game.get_score(2))
				else:
					print 'Your Score : ' + str(game.get_score(2))
					print 'Opponent\'s Score : ' + str(game.get_score(1))
				break
			else:                                   
				client.SendData2Process(move)
		else:
			break
	client.closeChildProcess()
	client.closeSocket()

if __name__ == '__main__':
		parser = argparse.ArgumentParser(description = 'Yinsh client')
		parser.add_argument('ip', metavar = '0.0.0.0', type = str, help = 'Server IP')
		parser.add_argument('port', metavar = '10000', type = int, help = 'Server port')
		parser.add_argument('exe', metavar = 'run.sh', type = str, help = 'Your executable')
		parser.add_argument('-mode', dest = 'mode', type = str, default = 'CUI', help = 'How to render. Set to "GUI" mode to render, else set to "CUI"')
		args = parser.parse_args()
		game_loop(args)
