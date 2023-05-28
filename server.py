#server
import threading
import socket

# docs in comments reference to python.org documentation about libraries(socket and threading)

# NOTES:
# Every client probably should have own instance
# Thus class ClientConnection is needed
# Include things like: nickname, ip, socket?, channels[] etc
# ooorrr/and instead each feature is on own thread 

#clients = []
clients = {} #dictionary is now in format 'connection': 'nickname'
channels = {"newbies":[], "pros":[]} # 'channel':['nickname',] 
#not perhaps best idea but by using nickname and not removing it, user can reconnect and
#dont need to join every channel again. This is not usable IRL !

# combine dictionaries? would enable easily user created channels
# smth like this clients = {connection: {nickname: , channels: []}}

def broadcast(clientConnection, text):
    for client in clients:
            if client != clientConnection:
                try:
                    client.sendall(text.encode('utf-8'))
                except:
                    pass

def notifyJoining(clientConnection):
    text = f'*** {clients.get(clientConnection)} connected to the server! ***'
    broadcast(clientConnection, text)

def notifyLeaving(clientConnection):
    text = f'*** {clients.get(clientConnection)} disconnected from the server! ***'
    broadcast(clientConnection, text)

def sendPrivate(sender, receipt, message):
    for client in clients:
                if clients[client] == receipt: #nickname comparison
                    try:
                        client.sendall(f'Psst private message from {clients.get(sender)}: {message}'.encode('utf-8'))
                    except:
                        pass

def joinChannel(clientConnection, channel):
    channelArray = channels.get(channel)
    print(channels)
    channelArray.append(clients.get(clientConnection))
    channels.update({channel: channelArray})
    print(channels)

def sendChannel(sender, receipt, message):
    for channel in channels:
                if channel == receipt: #channel comparison
                    channelArray = channels.get(channel)
                    for nickname in channelArray:
                        # get connection by nickname
                        # https://www.geeksforgeeks.org/python-get-key-from-value-in-dictionary/
                        try:
                            client = list(clients.keys())[list(clients.values()).index(nickname)]
                        except:
                            pass
                        if client != sender:
                            try:
                                client.sendall(f'[{receipt}] {clients.get(sender)}: {message}'.encode('utf-8'))
                            except:
                                pass

def handling(clientConnection):
    while True:
        try:
            message = clientConnection.recv(4096).decode('utf-8')
            if not message:
               break
            splitText = message.split(" ", 2)
            #Sending private message
            if splitText[0] == "/private":
                receipt = splitText[1]
                sendPrivate(clientConnection, receipt, splitText[2])
                continue
            #Joining channel
            if splitText[0] == "/join":
                channel = splitText[1]
                joinChannel(clientConnection, channel)
                continue
            #Sending channel message
            if splitText[0] == "/channel":
                channel = splitText[1]
                sendChannel(clientConnection, channel, splitText[2])
                continue
            if splitText[0] == "/disconnect":
                #confirmation for client so it can stop receiving
                clientConnection.sendall("/disconnect".encode('utf-8')) 
                break

            #Normal message
            for client in clients:
                if client != clientConnection:
                    try:
                        client.sendall(f'{clients.get(clientConnection)}: {message}'.encode('utf-8'))
                    except:
                        pass
        except:
            break 
    #clientConnection.close
    #clients.pop(clientConnection)
    #notifyLeaving(clientConnection)
    notifyLeaving(clientConnection)
    nickname = clients[clientConnection]
    del clients[clientConnection]
    print(f'{nickname} has left the chat.')
    clientConnection.close




def initializeConnection():
    while True:
        clientConnection, clientAddress = serverSocket.accept()
        clientConnection.send('/nickname'.encode('utf-8'))
        nickname = clientConnection.recv(4096).decode('utf-8') # smaller buffer would be fine?
        clientConnection.send(f'*** Welcome {nickname}! *** '.encode('utf-8'))
        print("Connected by", clientAddress)
        clients[clientConnection] = nickname # add address as key and nickname as its value
        clientThread = threading.Thread(target=handling, args=(clientConnection,))
        #clients.append(clientConnection) # or should i add client connection?
        notifyJoining(clientConnection)
        clientThread.start()

#basics
serverAddress = "127.0.0.1" #is 0.0.0.0 or localhost possible/better?
serverPort = 5000

#socket init
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.bind((serverAddress, serverPort))
serverSocket.listen() # int is backlog (connections?) docs howto had 5, docs example had 1
print("Server is running on port " + str(serverPort))
print("Waiting for connections...")
initializeConnection()
