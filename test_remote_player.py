from socket import *
import json
from jsonparser import json_to_python
from player import Player, PlayerCommandError
from typedefs import Point
import time
from random import randint

BUFFER_SIZE = 65536
NUM_REMOTE = 3
error_msg = "GO has gone crazy!"
with open("go.config") as json_file:
    server_info = json.load(json_file)

class TestRemotePlayer:

    def __init__(self):
        self.client = socket(AF_INET, SOCK_STREAM)
        self.idx = 0
        self.curr_player = None
        self.prev_registered = False
        self.name = "no name"


    def run_and_respond(self):
        self.client.connect((server_info["IP"], server_info["port"]))
        while True:
            command = json.loads(self.client.recv(BUFFER_SIZE).decode())
            # print(command)
            # for idx, command in enumerate(commands):
                # print("Command is ", command)
            output = ""

            if command == ["register"]:
                if self.idx != 0:
                    output = error_msg
                # print("Got register")
                else:
                    if not self.curr_player:
                        if not self.prev_registered:
                            self.curr_player = Player(name="Player " + str(randint(0, 1000)))
                            self.name = self.curr_player.get_name()
                            self.prev_registered = True
                        else:
                            self.curr_player = Player(name=self.name)
                            self.name = self.curr_player.get_name()
                        output = self.name
                    else:
                        output = error_msg
            elif command[0] == "receive-stones":
                # print("Got receive stones")
                if self.idx != 1:
                    output = error_msg
                else:
                    try:
                        self.curr_player.set_stone(command[1])
                        self.idx += 1
                        continue
                    except (PlayerCommandError, TypeError, ValueError) as e:
                        output = error_msg
            elif command == ["end-game"]:
                self.idx = -1
                self.curr_player = None
                output = "OK"
            else:
                # print(idx)
                if self.idx < 2 or command[0] != "make-a-move":
                    output = error_msg
                # print("Other command")
                else:
                    try:
                        output = self.curr_player.n1play(command[1])
                        print(output)
                    except (PlayerCommandError, TypeError, ValueError) as e:
                        print("Something failed")
                        output = error_msg
            self.idx += 1
            time.sleep(0.05)
            if output != "":
                print("Sending ", output)
                self.client.send(output.encode())
            if output == error_msg:
                break
        self.client.close()


if __name__ == "__main__":
    rp = TestRemotePlayer()
    rp.run_and_respond()


# server = socket(AF_INET, SOCK_STREAM)
# server.bind(('', server_info["port"]))
# server.listen(1)
# while True:
#     connection, address = server.accept()
#     input = connection.recv(4096).decode()
#     print(input)
#     if input == ["register"]:
#         if not remote_player:
#             remote_player = Player(n=depth_info["depth"])
#         else:
#             output = error_msg
#     elif input[0] == "receive-stones":
#         try:
#             remote_player.set_stone(input[1])
#         except PlayerCommandError as e:
#             output = error_msg
#     else:
#         try:
#             output = remote_player.n1play(input[1])
#         except PlayerCommandError as e:
#             output = error_msg
#     connection.send(output.encode())
#     connection.close()