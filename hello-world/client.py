import socket, sys
import dill
from socket_utils import recvall
SERVER = 'localhost'
PORT = 8889

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((SERVER, PORT))
E = 'utf-8'

while 1:
    msg = input("Command To Send: ")
    lines = msg.split(" ")
    meta, cmd = lines[0], " ".join(lines[1:])
    if meta == "close":
       s.close()
       sys.exit(0)
    if meta == 'local':
        exec(cmd)
    else:
        cmd = " ".join([meta, cmd])
        cmd = cmd.encode(E)
        print(f"Sending {cmd}")
        s.sendall(cmd)
        try:
            data = recvall(s)
            result = dill.loads(data)
            print(f"received {result}")
            globals().update(result)
        except Exception as e:
            print(e)
            print("Could not receive response")


