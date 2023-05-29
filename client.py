import socket
import threading
import sys




# Notes:
# Client doesn't probably need own instances?
# as each client is probably the one instance
# We could still make own class for setting nickname, connecting server by IP address
#   not sure
# Threading could be useful to receiving and sending messages same time 

#give nickname
def setNickname():
    nickname = input("Give a name: ")
    return nickname

#give server address
def getAddress():
    address = input("Give the server's ip-address: ")
    return address

def disconnectServer(connection, message):
    connection.send(message.encode('utf-8'))
    connection.close()
    sys.exit()


def receiveMessages(connection, nickname):
    while True:
        try:
            message = connection.recv(4096).decode('utf-8') #bufsize value 4096 is given as example in documentation
             #Check does message contain command from server
            #When creating new connection server will ask nickname
            if message == "/disconnect":
                break
            elif message == "/nickname":
                connection.send(nickname.encode('utf-8'))
            else:
                print(message)
        except:
            print("Error on receiving messages")
            connection.close()
            break

def sendMessages(connection):
    while True:
        message = input("")
        #disconnection initiation
        if message == "/disconnect":
            disconnectServer(connection, message)
            break
        else:
            connection.send(message.encode('utf-8'))
        # f"{nickname}: {message}" # not need as server add nickname to message

#def joinChannel(channels):
#    return channels

nickname = setNickname()
while True:
    address = getAddress()
    if address == "/quit":
        break
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #SOCK_DGRAM is udp and _STREAM tcp 
    port = 5000
    server.connect((address, port))

    #creating thread to receive messages from server
    receiveThread = threading.Thread(target=receiveMessages, args=(server, nickname))
    receiveThread.start()

    #creating thread to send messages to server
    sendThread = threading.Thread(target=sendMessages, args=(server,))
    sendThread.start()

    sendThread.join()
    receiveThread.join()

print("Ending chat program. Thank you!")