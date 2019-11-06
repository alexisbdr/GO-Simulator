from frontend import frontend
import socket
import sys

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8080       # The port used by the server



def main(): 
    #frontend()
    file = sys.stdin.read()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(str.encode(file))
        data = s.recv(1024)

    print('Received', repr(data))

if __name__ == "__main__":
    main()