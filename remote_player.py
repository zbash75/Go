from socket import *
import json
import time
from player import Player, PlayerCommandError

ERROR_MSG = "GO has gone crazy!"
BUFFER_SIZE = 65536

class RemotePlayerError(Exception):
    """Something went wrong in Remote Player"""
    pass

class RemotePlayer():

    def __init__(self, connection):
        self.command_idx = 0
        self.stone_set = False
        self.remote_exists = False
        self.connection = connection
        self.name = None

    def get_name(self):
        command = ["register"]
        self._check_command(command)
        self.name = self._receive()
        return self.name

    def get_player_name(self):
        return self.name

    def set_stone(self, stone):
        command = ["receive-stones", stone]
        self._check_command(command)

    def n1play(self, board_history):
        command = ["make-a-move", board_history]
        self._check_command(command)
        return self._receive()

    def dumb_play(self, board_history):
        command = ["make-a-move", board_history]
        self._check_command(command)
        return self._receive()

    def end_game(self):
        print("Ending game")
        command = ["end-game"]
        self.remote_exists = False
        self._check_command(command)
        return self._receive()

    def _check_command(self, command):
        if command == ["register"]:
            if self.command_idx != 0 or self.remote_exists:
                print("Register error: ", command)
                raise RemotePlayerError
            else:
                output = command
                self.remote_exists = True
        elif command[0] == "receive-stones":
            # print("Got receive stones")
            if self.command_idx != 1 or self.stone_set:
                print("Stones error: ", command)
                raise RemotePlayerError
            else:
                output = command
                self.stone_set = True
        else:
            # print(idx)
            if self.command_idx < 2 and command[0] != "make-a-move" and command[0] != "end-game":
                print("Other error: ", command)
                raise RemotePlayerError
            # print("Other command")
            else:
                output = command
        
        self.command_idx += 1
        # print(command)
        self.connection.send(json.dumps(command).encode())

    def _send(self, command):
        self.connection.send(json.dumps(command).encode())
        if command[0] != "receive-stones":
            return self._receive()

    def _receive(self):
        try:
            output = self.connection.recv(BUFFER_SIZE).decode()
            # print(output)
            output = self._check_output(output)
        except (ConnectionError, RemotePlayerError) as e:
            return ERROR_MSG
        # print(output)
        return output

    def _check_output(self, output):
        if self.command_idx >= 2:
            if "-" in output and len(output.split("-")) == 2:
                try:
                    a = int(output.split("-")[0])
                    b = int(output.split("-")[1])
                except ValueError:
                    raise RemotePlayerError
            elif output not in ["pass", "GO has gone crazy!", "This history makes no sense!", "OK"]:
                raise RemotePlayerError
        else:
            if not isinstance(output, str):
                raise RemotePlayerError
        return output

