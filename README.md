# SocketClient
A client and server for peer communication across different terminals using the python socket API. Allows users to converse in channels. 
Users can create, join, or leave channels. When a user is in a channel, all messages will be relayed to other users currently
in the same channel. Messages are split into 200 bytes and sent to and from the clients and server. Non-blocking sockets will
buffer any excess bytes to send later. All messages must be shorter than 200 bytes. 
