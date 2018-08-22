import socket,sys
from subprocess import Popen, PIPE
from nbstreamreader import NonBlockingStreamReader as NBSR
from sys import platform
import os

class Communicator(object):
	def __init__(self): 
		self.Socket = None
		self.ChildProcess = None		

	def setSocket(self,Socket,TIMEOUT=60):
		self.Socket = Socket		
		self.Socket.settimeout(TIMEOUT)
		

	def isSocketNotNone(self):
		if(self.Socket is None):
			return False
		else:
			return True

	def isChildProcessNotNone(self):
		if(self.ChildProcess is None):
			return False
		else:
			return True
	
	def closeSocket(self):
		if(self.isSocketNotNone()):
			# Try in case the connection is already closed by the other process
			try:				
				self.Socket.close()
			except:
				pass
			self.Socket = None

	def SendDataOnSocket(self,data):
		success_flag = False
		if(self.isSocketNotNone()):
			try:
				self.Socket.send(data)
				success_flag = True
			except:
				pass
		return success_flag

	def RecvDataOnSocket(self):
		data = None
		if(self.isSocketNotNone()):			
			while True:
				try:			
					data = self.Socket.recv(1024)
				except:
					data = None
					break
				if(data is None):
					break
				elif(len(data) > 0):
					break
		return data
		

	def CreateChildProcess(self,Execution_Command,Executable_File):	
		if platform == "darwin" or platform == "linux" or platform == "linux2":
			self.ChildProcess = Popen ([Execution_Command, Executable_File], stdin = PIPE, stdout = PIPE, bufsize=0,preexec_fn=os.setsid)	
		else:
			self.ChildProcess = Popen ([Execution_Command, Executable_File], stdin = PIPE, stdout = PIPE, bufsize=0)
		self.ModifiedOutStream = NBSR(self.ChildProcess.stdout)		
		

	def RecvDataOnPipe(self,TIMEOUT):
		data = None
		if(self.isChildProcessNotNone()):
			try:
				data = self.ModifiedOutStream.readline(TIMEOUT)
			except:
				pass
		return data
						
	def SendDataOnPipe(self,data):
		success_flag = False
		if(self.isChildProcessNotNone()):
			try:
				self.ChildProcess.stdin.write(data)
				success_flag = True
			except:
				pass
		return success_flag
	
	def closeChildProcess(self):
		if(self.isChildProcessNotNone()):		
			if platform == "darwin" or platform == "linux" or platform == "linux2":
				try:
				 	os.killpg(os.getpgid(self.ChildProcess.pid), 15)
				except:
					pass
			else:	
				self.ChildProcess.kill()
			self.ChildProcess = None
		

if __name__ == '__main__':
	c = Communicator()
	c.CreateChildProcess('sh','run.sh')
	counter = 1
	try:
		while(counter != 100):
			c.SendDataOnPipe(str(counter) + '\n')
			data = c.RecvDataOnPipe()		
			print "Parent Recieved",data
			data = data.strip()
			counter = int(data)
	except:
		c.closeChildProcess()

	

	
	
	
