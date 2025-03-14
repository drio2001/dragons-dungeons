import socket
import json

import protocols as p
import arguments_manager as am


# *********************************************************************
# *  Daniel Río Alonso, Adrián Cañizares Salgado, Mario Calero López  *
# *********************************************************************


def manage_option_menu(msg, c_s, n_stages):
    print(msg["menu"])
    exit = False
    while not exit:
        try:
            o = int(input("Please, choose an option: "))
            if msg["options"][1] >= o >= msg["options"][0]:
                if o == 3:
                    correct_input = False
                    while not correct_input:
                        f = input("What is the name of the game?"
                                  " (The filename must end with .txt or .json): ").lower()
                        if f == "cancel":
                            correct_input = True
                            print("The game was not loaded.")
                        elif f.endswith(".txt") or f.endswith(".json"):
                            correct_input = True
                            exit = True
                            message = {"protocol": p.MSG_LOAD_GAME, "options": f, "n_stages": n_stages}
                            p.send_one_message(c_s, json.dumps(message).encode())
                        else:
                            print("The format of the filename is incorrect"
                                  "(The filename must end with .txt or .json). "
                                  "Try again: ")
                else:
                    exit = True
                    message = {"protocol": p.MSG_SEND_SERVER_OPTION, "options": o}
                    p.send_one_message(c_s, json.dumps(message).encode())
            else:
                print("You didn't enter an available option [1 - 4]. Try again:")
        except ValueError:
            print("The option is not a number. Try again:")


def manage_character_menu(msg, c_s, n_stages):
    print(msg["menu"])
    exit = False
    while not exit:
        try:
            o = int(input("Please, choose a character: "))
            if msg["options"][1] >= o >= msg["options"][0]:
                exit = True
                message = {"protocol": p.MSG_SEND_CHARACTER, "options": o, "n_stages": n_stages}
                p.send_one_message(c_s, json.dumps(message).encode())
            else:
                print("You didn't enter an available character [1 - 4]. Try again:")
        except ValueError:
            print("The option is not a number. Try again:")


def manage_list_games(msg, c_s):
    print(msg["menu"])
    print(msg["options"])
    exit = False
    while not exit:
        try:
            o = int(input("Please, choose a number of the game you want to join: "))
            if o in msg["options"]:
                exit = True
                message = {"protocol": p.MSG_SEND_GAME, "options": o}
                p.send_one_message(c_s, json.dumps(message).encode())
            else:
                print("You didn't enter an available game. Try again:")
        except ValueError:
            print("The option is not a number. Try again:")


def manage_your_turn(msg, c_s):
    exit = False
    while not exit:
        o = input("Where do you want to do [a, s]: ").lower()
        if o in msg["options"]:
            if o == "s":
                exit = True
                f = input("Where do you want to save the game? "
                          "(The filename must end with .txt or json): ").lower()
                message = {"protocol": p.MSG_SAVE_GAME, "options": f}
                p.send_one_message(c_s, json.dumps(message).encode())
            else:
                exit = True
                message = {"protocol": p.MSG_SEND_COMMAND, "options": o}
                p.send_one_message(c_s, json.dumps(message).encode())
        else:
            print("You didn't enter [a] for attack or [s] for save. Try again:")


n_stages, nickname, ip, port = am.parse_args_client()
stages_ok, port_ok = am.check_args_client(n_stages, port)
c_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

if stages_ok and port_ok:
    try:
        port = int(port)
        c_s.connect((ip, port))
        exit = False
        message = {"protocol": p.MSG_JOIN, "nickname": nickname}
        p.send_one_message(c_s, json.dumps(message).encode())
        while not exit:
            server_msg = json.loads(p.recv_one_message(c_s).decode())
            if server_msg["protocol"] == p.MSG_WELCOME:
                if server_msg["accepted"]:
                    manage_option_menu(server_msg, c_s, n_stages)
                else:
                    exit = True
                    print(server_msg["message"])
            elif server_msg["protocol"] == p.MSG_CHARACTER_MENU:
                manage_character_menu(server_msg, c_s, n_stages)
            elif server_msg["protocol"] == p.MSG_LIST_GAMES:
                manage_list_games(server_msg, c_s)
            elif server_msg["protocol"] == p.MSG_YOUR_TURN:
                manage_your_turn(server_msg, c_s)
            elif server_msg["protocol"] == p.SEND_END_GAME:
                exit = True
                if server_msg["win"]:
                    print("All the stages have been cleared. You won the game.")
                else:
                    print("All characters have been defeated. Try again.")
            elif server_msg["protocol"] == p.SEND_DC_SERVER:
                exit = True
                print(server_msg["msg"])
            elif server_msg["protocol"] == p.MSG_SERVER_MESSAGE:
                print(server_msg["msg"])
    except ConnectionResetError:
        exit = True
        print("The server has been closed.")
    except ConnectionRefusedError:
        exit = True
        print("Could not connect to the server. You must provide a correct ip and port.")
    except KeyboardInterrupt:
        exit = True
        message = {"protocol": p.SEND_DC_ME}
        p.send_one_message(c_s, json.dumps(message).encode())
        print("Execution interrupted by user.")
else:
    if not stages_ok:
        print("The number of stages must be between 1 and 10. Finishing program.")
    if not port_ok:
        print("The port must be between 0-65535. Finishing program.")

c_s.close()
