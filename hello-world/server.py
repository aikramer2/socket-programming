import socket
import dill
from io import BytesIO
from collections import deque
import struct
from socket_utils import recvall

IPADDR = ''
PORT = 8889
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((IPADDR, PORT))


def split(bytes, chunk_size=1024):
    n_chunks = len(bytes) // chunk_size
    if n_chunks < 2:
        yield bytes
    else:
        for i in range(n_chunks):
            yield bytes[i * chunk_size: (i+1)*chunk_size]



def run_code(code):
    snapshot = locals().copy()
    exec(code)
    updated = locals()

    result = {}
    for key in filter(lambda x: x not in ('snapshot', 'updated'), updated):
        if snapshot.get(key) is updated.get(key):
            pass
        else:
            result[key] = updated[key]
    print(result)

    globals().update(result)
    yield from split(dill.dumps(result))

try:
    while True:
        s.listen(1)
        conn, addr = s.accept()
        print(f"ping from {addr[0]}:{addr[1]}")
        data = recvall(conn).decode('utf-8')

        if not data:
            break

        print(f"Received: {data}, type: {type(data)}")
        try:
            response = run_code(data)
        except Exception as e:
            response = f"Exception {e}, continuing to listen to your bullshit"

        if response:
            try:
                conn.sendall(response)
                for chunk in response:
                    print(f"Sending back {chunk}")
                    conn.send(chunk)
            except Exception as e:
                print(f"Exception {e} observed while sending response")
                conn.send("-1".encode('utf-8'))

finally:
    print("Shutting Down!")
    s.close()
