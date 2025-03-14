import sys
import getopt

def parse_args_client():
    stages = 1
    nick = ""
    ip = "127.0.0.1"
    port = 7123
    opts, args = getopt.getopt(sys.argv[1:], "s:n:i:p:", ["stages=", "nick=", "ip=", "port="])
    for o, arg in opts:
        if o in ("-s", "--stages"):
            stages = arg
        elif o in ("-n", "--nick"):
            nick = arg
        elif o in ("-i", "--ip"):
            ip = arg
        elif o in ("-p", "--port"):
            port = arg
    return stages, nick, ip, port


def parse_args_server():
    port = 7123
    opts, arg = getopt.getopt(sys.argv[1:], "p:", ["port="])
    for o, arg in opts:
        if o in ("-p", "--port"):
            port = arg
    return port


def check_args_client(stages, port):
    stages_ok = False
    port_ok = False
    try:
        stages = int(stages)
        if 1 <= stages <= 10:
            stages_ok = True
    except ValueError:
        stages_ok = False
    try:
        port = int(port)
        if 0 <= port <= 65535:
            port_ok = True
    except ValueError:
        port_ok = False
    return stages_ok, port_ok


def check_args_server(port):
    port_ok = False
    try:
        port = int(port)
        if 0 <= port <= 65535:
            port_ok = True
    except ValueError:
        port_ok = False
    return port_ok
