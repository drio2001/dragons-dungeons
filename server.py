import sys
import os
import socket
import threading
import json

sys.path.append(os.path.join(os.path.dirname(__file__), "entities"))

from entities import save_entities as s
import game
import protocols as p
import constants as ct
import linked_list as lk
import arguments_manager as am

# *********************************************************************
# *  Daniel Río Alonso, Adrián Cañizares Salgado, Mario Calero López  *
# *********************************************************************


client_threads_running = []
id = 1
finished_games = 0
games = {}
player_games = {}
link = lk.LinkedList()


def get_games():
    global games
    msg = ""
    msg += "***************************************\n"
    msg += "        --- AVAILABLE GAMES ---        \n"
    msg += "***************************************\n"
    for key, value in games.items():
        msg += str(key) + ". Game: " + str(key) + "\n"
    msg += "\n***************************************"
    return msg


def manage_send_welcome(msg, c_s, c_a):
    nickname = msg["nickname"]
    if not link.find(nickname):
        link.add_last(game.Player(nickname, c_a))
        reply = {"protocol": p.MSG_WELCOME, "menu": "1. Create \n2. Join \n3. Load \n4. Exit",
                 "options": [1, 4], "accepted": True}
        print("(WELCOME)", link.find_name(c_a), "joined the server.")
    else:
        reply = {"protocol": p.MSG_WELCOME, "menu": "1. Create \n2. Join \n3. Load \n4. Exit",
                 "options": [1, 4], "accepted": False, "message": "The nickname is already used. "}
    p.send_one_message(c_s, json.dumps(reply).encode())


def manage_send_option(msg, c_s, c_a):
    if msg["options"] == 1:
        character_menu = game.Game.msg_available_character_menu()
        reply = {"protocol": p.MSG_CHARACTER_MENU, "menu": character_menu, "options": [1, 4]}
        p.send_one_message(c_s, json.dumps(reply).encode())
        print("(CREATE)", link.find_name(c_a), "created the game.")
    elif msg["options"] == 2:
        available_games = get_games()
        if len(list(games.keys())) == 0:
            reply = {"protocol": p.SEND_DC_SERVER, "msg": "There no games available."}
            p.send_one_message(c_s, json.dumps(reply).encode())
            link.delete(link.find_name(c_a))
        else:
            reply = {"protocol": p.MSG_LIST_GAMES, "menu": available_games, "options": list(games.keys())}
            p.send_one_message(c_s, json.dumps(reply).encode())
    else:
        reply = {"protocol": p.SEND_DC_SERVER, "msg": "Leaving the game..."}
        p.send_one_message(c_s, json.dumps(reply).encode())
        print("(EXIT)", link.find_name(c_a), "exited the game.")
        link.delete(link.find_name(c_a))


def manage_start_round(g):
    stage_menu = g.msg_current_character_menu() + "\n" + g.msg_current_stage_menu()
    msg = {"protocol": p.MSG_SERVER_MESSAGE, "msg": stage_menu}
    for s in g.sockets:
        p.send_one_message(s, json.dumps(msg).encode())
    other_player = (g.current_turn + 1) % ct.n_players
    msg1 = {"protocol": p.MSG_YOUR_TURN, "options": ["a", "s"]}
    msg2 = {"protocol": p.MSG_SERVER_MESSAGE, "msg": "It's the turn of player " + str(g.current_turn + 1)}
    p.send_one_message(g.sockets[g.current_turn], json.dumps(msg1).encode())
    p.send_one_message(g.sockets[other_player], json.dumps(msg2).encode())


def manage_start_game(g):
    g.create_enemies()
    manage_start_round(g)


# RECEIVE THE NUMBER OF THE GAME (GAMES = []) AND SEND THE AVAILABLE CHARACTERS
def manage_send_game(msg, c_s, c_a):
    global player_games
    global games
    join_game = int(msg["options"])
    g = games[join_game]
    if len(g.sockets) == 1:
        player_games[c_a] = join_game
        print("(JOIN)", link.find_name(c_a), "joined the game.")
        if len(g.current_characters) == 2:
            g.sockets.append(c_s)
            g.nickname.append(link.find_name(c_a))
            manage_start_round(g)
            print("(START)", g.nickname[0], "and", g.nickname[1], "started the game.")
        else:
            character_menu = game.Game.msg_available_character_menu()
            msg = {"protocol": p.MSG_CHARACTER_MENU, "menu": character_menu, "options": [1, 4]}
            p.send_one_message(c_s, json.dumps(msg).encode())
    else:
        msg1 = {"protocol": p.MSG_SERVER_MESSAGE, "msg": "The game is full, please create or load other game."}
        msg2 = {"protocol": p.MSG_WELCOME, "menu": "1. Create \n2. Join \n3. Load \n4. Exit",
                "options": [1, 4], "accepted": True}
        p.send_one_message(c_s, json.dumps(msg1).encode())
        p.send_one_message(c_s, json.dumps(msg2).encode())


def manage_send_character(msg, c_s, c_a):
    global id
    global games
    global player_games
    if c_a in list(player_games.keys()):
        g = games[player_games[c_a]]
        if len(g.current_characters) < 2:
            g.add_character(int(msg["options"]))
            g.sockets.append(c_s)
            g.nickname.append(link.find_name(c_a))
            manage_start_game(g)
            print("(START)", g.nickname[0], "and", g.nickname[1], "started the game.")
        else:
            msg1 = {"protocol": p.MSG_SERVER_MESSAGE, "msg": "The game is full, please create or load other game."}
            msg2 = {"protocol": p.MSG_WELCOME, "menu": "1. Create \n2. Join \n3. Load \n4. Exit",
                    "options": [1, 4], "accepted": True}
            p.send_one_message(c_s, json.dumps(msg1).encode())
            p.send_one_message(c_s, json.dumps(msg2).encode())
    else:
        g = game.Game(msg["n_stages"])
        g.add_character(int(msg["options"]))
        g.sockets.append(c_s)
        g.nickname.append(link.find_name(c_a))
        games[id] = g
        player_games[c_a] = id
        reply = {"protocol": p.MSG_SERVER_MESSAGE, "msg": "Waiting to the other players, to join the game."}
        p.send_one_message(c_s, json.dumps(reply).encode())
        id += 1


def manage_save_game(msg, c_s, c_a):
    global games
    g = games[player_games[c_a]]
    filename = msg["options"]
    message = ""
    if filename == "cancel":
        message += "The game was not saved."
    elif filename.endswith(".txt") or filename.endswith(".json"):
        saved_string = s.saved_json(g.current_characters, g.current_enemies,
                                    g.stages, g.current_stage, g.current_turn)
        with open(filename, "w") as file:
            file.write(saved_string)
        message += "The game has been saved."
    else:
        message += "The format of the filename is incorrect " \
                   "(The filename must end with .txt or .json). " \
                   "Try again: "

    reply = {"protocol": p.MSG_SERVER_MESSAGE, "msg": message}
    p.send_one_message(c_s, json.dumps(reply).encode())

    msg = {"protocol": p.MSG_YOUR_TURN, "options": ["a", "s"]}
    p.send_one_message(c_s, json.dumps(msg).encode())


def manage_load_game(msg, c_s, c_a):
    global id
    global games
    global player_games
    g = game.Game(msg["n_stages"])
    g.load_game(msg["options"])
    g.sockets.append(c_s)
    g.nickname.append(link.find_name(c_a))
    games[id] = g
    player_games[c_a] = id
    reply = {"protocol": p.MSG_SERVER_MESSAGE, "msg": "Waiting to the other players, to join the game."}
    p.send_one_message(c_s, json.dumps(reply).encode())
    id += 1


def players_win(g, c_a):
    global finished_games
    for n in g.nickname:
        link.delete(str(n))
    print("(END)", g.nickname[0], "and", g.nickname[1],
          "ended the game. They won the game.")
    del games[player_games[c_a]]
    finished_games += 1
    msg = {"protocol": p.SEND_END_GAME, "win": True}
    for s in g.sockets:
        p.send_one_message(s, json.dumps(msg).encode())


def players_lose(g, c_a):
    global finished_games
    for n in g.nickname:
        link.delete(str(n))
    print("(END)", g.nickname[0], "and", g.nickname[1],
          "ended the game. They lost the game.")
    del games[player_games[c_a]]
    finished_games += 1
    msg = {"protocol": p.SEND_END_GAME, "win": False}
    for s in g.sockets:
        p.send_one_message(s, json.dumps(msg).encode())


def new_stage(g):
    g.current_turn = 0
    g.current_stage += 1
    g.add_hp_round()
    manage_start_game(g)


def manage_send_command(msg, c_a):
    global games
    global player_games
    g = games[player_games[c_a]]
    option = msg["options"]
    if option == "a":
        reply = g.msg_players_attack(g.current_characters[g.current_turn], g.current_turn)
        msg = {"protocol": p.MSG_SERVER_MESSAGE, "msg": reply}
        for s in g.sockets:
            p.send_one_message(s, json.dumps(msg).encode())
        g.current_turn += 1
        if g.current_turn < 2:
            if not g.all_enemies_dead():
                manage_start_round(g)
            else:
                if g.current_stage == int(g.stages):
                    players_win(g, c_a)
                else:
                    new_stage(g)
        else:
            # IF ENEMIES ALIVE LEFT:
            if not g.all_enemies_dead():
                reply = g.msg_enemies_attack()
                msg = {"protocol": p.MSG_SERVER_MESSAGE, "msg": reply}
                for s in g.sockets:
                    p.send_one_message(s, json.dumps(msg).encode())
                # IF CHARACTERS ALIVE LEFT - START NEXT ROUND
                if not g.all_characters_dead():
                    g.current_turn = 0
                    manage_start_round(g)
                else:
                    players_lose(g, c_a)
            # IF ALL ENEMIES DEAD
            else:
                # IF CHARACTERS ALIVE LEFT:
                if not g.all_characters_dead():
                    if g.current_stage == int(g.stages):
                        players_win(g, c_a)
                    # NEXT STAGE
                    else:
                        new_stage(g)


def manage_disconnect_clients(c_s, c_a):
    global games
    global player_games
    global finished_games
    print("(EXIT)", link.find_name(c_a), "disconnected.")
    if c_a in player_games:
        g = games[player_games[c_a]]
        g.sockets.remove(c_s)
        g.nickname.remove(link.find_name(c_a))
        del games[player_games[c_a]]
        finished_games += 1
        for n in g.nickname:
            link.delete(str(n))
            print("(EXIT)", str(n), "was disconnected.")
            message = {"protocol": p.SEND_DC_SERVER, "msg": str(n) + " has being disconnected."}
            for s in g.sockets:
                p.send_one_message(s, json.dumps(message).encode())
    link.delete(link.find_name(c_a))


class ClientThread(threading.Thread):

    def __init__(self, client_socket, client_address):
        threading.Thread.__init__(self)
        self.c_s = client_socket
        self.c_a = client_address
        self.client_exit = False

    def run(self):
        while not self.client_exit:
            try:
                message = json.loads(p.recv_one_message(self.c_s).decode())
                if message["protocol"] == p.MSG_JOIN:
                    manage_send_welcome(message, self.c_s, self.c_a)
                elif message["protocol"] == p.MSG_SEND_SERVER_OPTION:
                    manage_send_option(message, self.c_s, self.c_a)
                elif message["protocol"] == p.MSG_SEND_CHARACTER:
                    manage_send_character(message, self.c_s, self.c_a)
                elif message["protocol"] == p.MSG_SEND_GAME:
                    manage_send_game(message, self.c_s, self.c_a)
                elif message["protocol"] == p.MSG_SEND_COMMAND:
                    manage_send_command(message, self.c_a)
                elif message["protocol"] == p.MSG_SAVE_GAME:
                    manage_save_game(message, self.c_s, self.c_a)
                elif message["protocol"] == p.MSG_LOAD_GAME:
                    manage_load_game(message, self.c_s, self.c_a)
                elif message["protocol"] == p.SEND_DC_ME:
                    manage_disconnect_clients(self.c_s, self.c_a)
            except ConnectionResetError:
                self.client_exit = True
            except ConnectionAbortedError:
                self.client_exit = True
            except TypeError:
                self.client_exit = True


class ServerThread(threading.Thread):
    def __init__(self, ip, port):
        threading.Thread.__init__(self)
        self.stop = False
        self.s_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s_s.bind((ip, port))
        self.s_s.listen(100)

    @staticmethod
    def close_client_connections():
        global client_threads_running
        for th in client_threads_running:
            th.c_s.close()

    def run(self):
        global client_threads_running
        while not self.stop:
            try:
                c_s, c_a = self.s_s.accept()
                print("Connection from:", c_a)
                client_thread = ClientThread(c_s, c_a)
                client_thread.start()
                client_threads_running.append(client_thread)
            except OSError:
                self.stop = True
                ServerThread.close_client_connections()
        print("Left the server.")


port = am.parse_args_server()
port_ok = am.check_args_server(port)

if port_ok:
    try:
        port = int(port)
        server_thread = ServerThread("127.0.0.1", port)
        server_thread.start()
        exit = False
        while not exit:
            server_input = input("Enter exit to close server: \n").lower()
            if server_input == "exit":
                exit = True
                message = {"protocol": p.SEND_DC_SERVER, "msg": "Server closed. You have been disconnected"}
                for s in client_threads_running:
                    p.send_one_message(s.c_s, json.dumps(message).encode())
            elif server_input == "ngames":
                print("Active games:", len(games.keys()))
                print("Finished games:", finished_games)
            elif server_input == "gamesinfo":
                for keys in games:
                    g = games[keys]
                    print("----- GAME -----")
                    print("Total players:", len(g.current_characters))
                    print("Dead players:", g.dead_players)
                    print("Current stage:", g.current_stage)
                    print("Total stages:", g.stages)
                    print("----------------")
                if len(games) == 0:
                    print("There are not active games yet.")
            elif server_input == "clients":
                print("There are", link.size(), "clients connected to the server:")
                link.print_linked_list()
            elif server_input == "clients.json":
                dictionary = {"clients": link.convert_linked_list()}
                with open('connected_clients.txt', 'w') as file:
                    saved_string = json.dumps(dictionary, indent=0)
                    file.write(saved_string)
                    file.write("\n")
        server_thread.s_s.close()
    except OSError:
        print("The server has been closed.")
    except ConnectionAbortedError:
        print("Connection closed.")
    except ConnectionResetError:
        print("Connection closed.")

else:
    if not port_ok:
        print("The port must be between 0-65535. Finishing program.")
