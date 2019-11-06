#THIS IS THE BACKEND

import socket
import json

def readJSON(text):
    objs = []
    decoder = json.JSONDecoder()
    s_len = len(text)
    end = 0

    while end != s_len:
        try:
            obj, end = decoder.raw_decode(text, idx=end)
            objs.append(obj)
        except ValueError:
            end += 1

    return objs

file = open('go.config', 'r')
file = file.read()

netData = readJSON(file)
obj = netData[0]

HOST = obj['IP'] # Standard loopback interface address (localhost)
PORT = obj['port']    # Port to listen on (non-privileged ports are > 1023)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)
            print(readJSON(data.decode("utf-8")))



