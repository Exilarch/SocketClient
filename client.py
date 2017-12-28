import sys
import socket
import select

""" A chat client used for communicating with other peers across different channels on a currently running server.
	Usage: python2.7 client.py [name] [address] [port]
"""
class Client(object):

	def __init__(self, name, address, port):
		self.name = name
		self.address = address
		self.port = int(port)
		self.socket = socket.socket()
		self.buffer_list = {}
		self.server_disconnect = "Server {}:{} has disconnected"
		self.prefix = "[Me] "
	def send(self):
		try:
			self.socket.connect((self.address, self.port))
			if len(self.name) < 200:
				self.name = '{:<200}'.format(self.name)
			self.socket.send(self.name)
		except:
			print("Failed connection")			
			sys.exit()
		sys.stdout.write(self.prefix); sys.stdout.flush()
		while 1:
			socket_list = [sys.stdin, self.socket]
			ready_to_read,ready_to_write,in_error = select.select(socket_list, [], [])
			for sock in ready_to_read:             
				if sock == self.socket:
					if socket in self.buffer_list.keys():
						chunks = self.buffer_list[socket][0]
						bytes_recv = self.buffer_list[socket][1]
					else: 
						chunks = []
						self.buffer_list[socket] = (chunks, 0)
						bytes_recv = 0
					if bytes_recv < 200:
						data = sock.recv(min(200 - bytes_recv, 200))
						if not data:
							error_msg = "\r" + self.server_disconnect.format(self.address, self.port)
							print(error_msg)
							sys.exit()
						bytes_recv += len(data)
						chunks.append(data)
					if bytes_recv < 200:
						self.buffer_list[socket] = (chunks, bytes_recv)
						continue
					msg = ''.join(chunks)
					msg = msg.rstrip()
					self.buffer_list[socket] = ([], 0)
					sys.stdout.write(msg)
					sys.stdout.write('\n' + self.prefix); sys.stdout.flush()     
				else:
					msg = sys.stdin.readline()
					if len(msg) < 200:
						msg = '{:<200}'.format(msg)
					self.socket.send(msg)
					sys.stdout.write(self.prefix); sys.stdout.flush() 

args = sys.argv
if len(args) != 4:
	print("Please supply a name, server address and port.")
	sys.exit()
client = Client(args[1], args[2], args[3])
client.send()