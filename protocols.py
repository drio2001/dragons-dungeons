import struct

MSG_JOIN = "JOIN"
MSG_WELCOME = "WELCOME"
MSG_LIST_GAMES = "LIST_GAMES"
MSG_SEND_SERVER_OPTION = "SEND_OPTION"
MSG_SEND_COMMAND = "SEND_COMMAND"
MSG_SEND_GAME = "SEND_GAME"
MSG_SEND_CHARACTER = "CHOOSE_CHARACTER"
MSG_CHARACTER_MENU = "CHARACTER_MENU"
MSG_YOUR_TURN = "YOUR_TURN"
MSG_SAVE_GAME = "SAVE_GAME"
MSG_LOAD_GAME = "LOAD_GAME"
MSG_EXIT_GAME = "EXIT_GAME"
SEND_END_GAME = "END_GAME"
SEND_DC_ME = "DC_ME"
SEND_DC_SERVER = "DC_SERVER"
MSG_SERVER_MESSAGE = "SERVER_MESSAGE"


def recv_all(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf:
            return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)


def recv_one_message(sock):
    lengthbuf = recv_all(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recv_all(sock, length)
