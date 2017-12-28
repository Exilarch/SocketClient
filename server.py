import sys
import socket
import select

""" A chat server to communicate with peers across different terminals. 
	Usage: python2.7 server.py [port]
"""
class Server(object): 
	def __init__(self, port):
		self.socket = socket.socket()
		self.socket.bind(("", int(port)))
		self.socket.listen(5)
		self.SOCKET_LIST = []
		self.SOCKET_LIST.append(self.socket)
		self.name_list = {}
		self.channel_list = {}
		self.buffer_list = {}
		self.leave_channel = "{0} left the channel"
		self.join_channel = "{0} joined the channel"
		self.already_exists = "Error, channel {0} already exists."
		self.none_exists = "Error, channel {0} does not exist."
		self.join_argument = "You must name a channel after '/join'."
		self.create_argument = "You must name a channel after '/create'."
		self.admin_error = "Only '/join', '/create', and '/list' are allowed. {0} is not allowed."
		self.channel_error = "You are not in a channel. Please join a channel, or create one if none exist!"
	
	def start(self):
		while 1:
			inputready, outputready, errorready = select.select(self.SOCKET_LIST, [], [], 0)
			for socket in inputready:
				if socket == self.socket:
					(clientsocket, address) = self.socket.accept()
					self.SOCKET_LIST.append(clientsocket)
				else: 
					try: 
						if socket in self.buffer_list.keys():
							chunks = self.buffer_list[socket][0]
							bytes_recv = self.buffer_list[socket][1]
						else: 
							chunks = []
							self.buffer_list[socket] = (chunks, 0)
							bytes_recv = 0
						if bytes_recv < 200:
							msg = socket.recv(min(200 - bytes_recv, 200))
							if not msg:
								if socket in self.SOCKET_LIST:
									self.SOCKET_LIST.remove(socket)
								self.broadcast(socket, "\r" + self.leave_channel.format(self.name_list[socket.getpeername()[1]]))
							bytes_recv += len(msg)
							chunks.append(msg)
						if bytes_recv < 200:
							self.buffer_list[socket] = (chunks, bytes_recv)
							continue
						data = ''.join(chunks)
						data = data.rstrip()
						self.buffer_list[socket] = ([], 0)
						firstChar = ""
						if len(data) > 0:
							firstChar = data[0]
						if socket.getpeername()[1] not in self.name_list.keys():
							self.name_list[socket.getpeername()[1]] = data
						elif len(firstChar) > 0 and firstChar == "/":
							commandList = data.split(" ", 1)
							if commandList[0] == "/create":
								if len(commandList) > 1:
									commandList[1] = commandList[1].rstrip()
									if commandList[1] not in self.channel_list:
										for k, l in self.channel_list.items():
											if self.name_list[socket.getpeername()[1]] in l:
												self.broadcast(socket, "\r" + self.leave_channel.format(self.name_list[socket.getpeername()[1]]))
												l.remove(self.name_list[socket.getpeername()[1]])
										self.channel_list[commandList[1]] = []
										self.channel_list[commandList[1]].append(self.name_list[socket.getpeername()[1]])
									else:
										error_msg = "\r" + self.already_exists.format(commandList[1])
										if len(error_msg) < 200:
											error_msg = '{:<200}'.format(error_msg)
										socket.send(error_msg)
								else:
									error_msg = "\r" + self.create_argument
									if len(error_msg) < 200:
										error_msg = '{:<200}'.format(error_msg)
									socket.send(error_msg)
								
							elif commandList[0] == "/join":
								if len(commandList) > 1:
									commandList[1] = commandList[1].rstrip()
									if commandList[1] in self.channel_list:
										sameChannel = False
										for k, l in self.channel_list.items():
											if self.name_list[socket.getpeername()[1]] in l:
												if k == commandList[1]:
													sameChannel = True
												else:
													self.broadcast(socket, "\r" + self.leave_channel.format(self.name_list[socket.getpeername()[1]]))
													l.remove(self.name_list[socket.getpeername()[1]])
										if not sameChannel:
											self.channel_list[commandList[1]].append(self.name_list[socket.getpeername()[1]])
											self.broadcast(socket, "\r" + self.join_channel.format(self.name_list[socket.getpeername()[1]]))
									else:
										error_msg = "\r" + self.none_exists.format(commandList[1])
										if len(error_msg) < 200:
											error_msg = '{:<200}'.format(error_msg)
										socket.send(error_msg)
								else:
									error_msg = "\r" + self.join_argument
									if len(error_msg) < 200:
										error_msg = '{:<200}'.format(error_msg)
									socket.send(error_msg)
								
							elif commandList[0] == "/list":
								if len(commandList) == 1:
									if len(self.channel_list.keys()) > 0:
										channel_series = "\r    " 
										i = 0
										for channel in self.channel_list:
											if i == 0 or i == len(self.channel_list):
												channel_series += "\r" + channel 
											else:
												channel_series += "\n" + channel
											i += 1
										if len(channel_series) < 200:
											channel_series = '{:<200}'.format(channel_series)
										socket.send(channel_series)
								else:
									error_msg = "\r" + self.admin_error.format(data)
									if len(error_msg) < 200:
										error_msg = '{:<200}'.format(error_msg)
									socket.send(error_msg)	
							else:
								error_msg = "\r" + self.admin_error.format(data)
								if len(error_msg) < 200:
									error_msg = '{:<200}'.format(error_msg)
								socket.send(error_msg)	
						elif data: 
							self.broadcast(socket, "\r" + '[' + str(self.name_list[socket.getpeername()[1]]) + '] ' + data)
					except Exception as e: 
						print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
						continue
	def broadcast(self, sock, message):
		check = False
		for l in self.channel_list.values():
			if self.name_list[sock.getpeername()[1]] in l:
				check = True
		if not check:
			error_msg = "\r" + self.channel_error
			if len(error_msg) < 200:
				error_msg = '{:<200}'.format(error_msg)
			try: 
				sock.send(error_msg)
			except:
				sock.close()
				if sock in self.SOCKET_LIST:
					self.SOCKET_LIST.remove(sock)
		else:	
			for socket in self.SOCKET_LIST:
				if socket != self.socket and socket != sock:
					try:
						for key in self.channel_list:
							if self.name_list[socket.getpeername()[1]] in self.channel_list[key] and self.name_list[sock.getpeername()[1]] in self.channel_list[key]:
								if len(message) < 200:
									message = '{:<200}'.format(message)
								socket.send(message)
					except:
						socket.close()
						if socket in self.SOCKET_LIST:
							self.SOCKET_LIST.remove(socket)
 
args = sys.argv
if len(args) != 2:
	print("Please supply a port.")
	sys.exit()
server = Server(args[1])
server.start()       
