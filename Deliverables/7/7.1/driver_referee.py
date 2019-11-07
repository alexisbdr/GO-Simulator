
import socket
import sys
from json_reader import readJSON
import selectors

def main():
    
    
    file = open('go.config', 'r')
    file = file.read()
    netData = readJSON(file)
    netData = netData[0]
    HOST = netData['IP']
    PORT = netData['port']
    
    

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    started = False

    print("Listening for client . . .")
    conn, addr = server_socket.accept()
    print("Connected to client at ", addr)
    while True:
        output = conn.recv(131072)
        started = True
        if output.strip() == b"starting" and started:
            conn.send(str.encode(sys.stdin.read()))
        elif output.strip() == b"Disconnecting":
            conn.close()
            sys.exit("Received disconnect message. Shutting down")
            conn.send("dack")
        elif output:
            print("Message recieved from client:")
            print(output.decode('utf-8'))
            conn.send(b"end")


if __name__ == "__main__":
    main()

