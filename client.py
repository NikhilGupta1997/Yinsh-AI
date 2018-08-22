from Communicator import Communicator
import socket,sys,json,os,time,pdb
import math
from Game import Game
from Board import Board
import argparse

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
			print 'ERROR : THIS CLIENT STOPPED UNEXPECTEDLY OR TIMED OUT'
			super(Client,self).closeChildProcess()			
			retData = {'meta':'UNEXPECTED STOP','action':'KILLPROC','data':''}
		else:			
			# 1 Milli Second Default
			time_delta = max(1,int((end_time - start_time) * 1000))
			self.GAME_TIMER -= time_delta
			if(self.GAME_TIMER > 0):
				retData = {'meta':'','action':'NORMAL','data':data}
			else:
				retData = {'meta':'TIMEOUT','action':'KILLPROC','data':''}
				print 'ERROR : THIS CLIENT STOPPED UNEXPECTEDLY OR TIMED OUT'			
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

def game_loop(game, args):
	client = Client()
	if args.exe.endswith('.py'):
		client.CreateChildProcess('python', args.exe)
	elif args.exe.endswith('.sh'):
		client.CreateChildProcess('sh', args.exe)
	else:
		client.CreateChildProcess('sh', args.exe)
	client.Connect2Server(args.ip, args.port)
	server_string = client.RecvDataFromServer()
	if(server_string is None):
		print 'ERROR IN SETTING UP CONNECTIONS. SORRY'
		sys.exit(0)
	server_string_list = server_string.strip().split()
	player_id = server_string_list[0]
	board_size = int(server_string_list[1])
	game_timer = int(server_string_list[2])
	client.setGameTimer(game_timer)
	print 'You are player ' + str(player_id)
	print 'You are alloted a time of ' + str(game_timer) + 's\n'
	client.SendData2Process(server_string)
	if args.mode == 'GUI':
		game.render_board.render(game)
	elif args.mode == 'CUI':
		game.render()
	if player_id == '2':
		move = client.RecvDataFromServer()
		if move:
			move = move.strip()
			print "The other player played " + move
			success = game.execute_move(move)			
			client.SendData2Process(move)
		else:
			sys.exit(0)	
	while(True):			
		move = client.RecvDataFromProcess()						
		if move['action'] == 'KILLPROC':
			move['meta'] = move['meta'] + ' BY PLAYER ' + player_id
			client.SendData2Server(move)
			break
		move['data'] = move['data'].strip()
		print "You played " + move['data']
		success = game.execute_move(move['data'])
		message = {}
		if success == 0:
			# TODO : DECIDE THE SCORING FOR THIS CASE
			message['data'] = ''
			message['action'] = 'KILLPROC'
			message['meta'] = 'INVALID MOVE BY PLAYER ' + player_id
			print 'INVALID MOVE ON THIS CLIENT'
		elif success == 2 or success == 3 or success == 4:
			# 2 : Player 1 wins
			# 3 : Player 2 wins
			# 4 : Game Drawn
			score = "(" + str(game.calculate_score(0) ) + "," + str(game.calculate_score(1) ) + ")"
			message['action'] = 'FINISH'
			message['data'] = move['data']
			if success == 2:
				message['meta'] = '1 wins WITH SCORE : '+score
				if(player_id == '1'):
					print 'YOU WIN!'
				else:
					print 'YOU LOSE :('
			elif success == 3:
				message['meta'] = '2 wins WITH SCORE : '+score
				if(player_id == '2'):
					print 'YOU WIN!'
				else:
					print 'YOU LOSE :('
			else:
				message['meta'] = 'Game Drawn WITH SCORE : '+score
				print 'GAME DRAWN'
		elif success == 1:
			message = move
		client.SendData2Server(message)
		if message['action'] == 'FINISH' or message['action'] == 'KILLPROC':
			break
		move = client.RecvDataFromServer()
		if move:
			move = move.strip()
			print "The other player played " + move
			success = game.execute_move(move)
			if success == 2 or success == 3 or success == 4:
				# 2 : Player 1 wins
				# 3 : Player 2 wins
				# 4 : Game Drawn
				if success == 2:						
					if(player_id == '1'):
						print 'YOU WIN!'
					else:
						print 'YOU LOSE :('
				elif success == 3:						
					if(player_id == '2'):
						print 'YOU WIN!'
					else:
						print 'YOU LOSE :('
				else :
					print 'GAME DRAWN'
				break
			else:					
				client.SendData2Process(move)
		else:
			break
	client.closeChildProcess()
	client.closeSocket()

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description = 'Tak client')
	parser.add_argument('ip', metavar = '0.0.0.0', type = str, help = 'Server IP')
	parser.add_argument('port', metavar = '10000', type = int, help = 'Server port')
	parser.add_argument('exe', metavar = 'run.sh', type = str, help = 'Your executable')
	parser.add_argument('-n', dest = 'n', metavar = 'N', type = int, default = 5, help = 'Tak board size')
	parser.add_argument('-mode', dest = 'mode', type = str, default = 'GUI', help = 'How to render')
	args = parser.parse_args()
	game = Game(args.n, args.mode)
	if args.mode != 'GUI':
		game_loop(game, args)
	else:
		from threading import Thread
		Th = Thread(target = lambda : game_loop(game, args))
		Th.start()
		game.init_display()
		game.display.mainloop()
