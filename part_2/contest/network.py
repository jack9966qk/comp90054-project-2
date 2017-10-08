import pickle

def receive(conn):
    s = ""
    msgLen = int(conn.recv(10))
    while len(s) < msgLen:
        data = conn.recv(1000000)
        if not data: break
        s += data
    return pickle.loads(s)

def send(socket, object):
    s = pickle.dumps(object)
    msgLen = str((len(s))).zfill(10)
    # print(msgLen)
    socket.sendall(msgLen)
    socket.sendall(s)