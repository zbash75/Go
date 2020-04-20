import json
from socket import *
import importlib
import pathlib
from referee import Referee
from remote_player import RemotePlayer, RemotePlayerError
from typedefs import MaybeStone, Point
from typing import List
from random import randrange
from constants import MAX_ROW, MAX_COLUMN
# from fake_player import FakePlayer

with open("go.config") as json_file:
    server_info = json.load(json_file)

player = importlib.import_module(pathlib.Path(server_info["default-player"]).stem)

class Admin:
    #todo: wrap
    def __init__(self, connections=[], player1="Josh", player2="Drake"):
        player_holder = []
        for connection in connections:
            player_holder.append(RemotePlayer(connection))

        # Fill in non-connections with local players
        if len(player_holder) == 0:
            player_holder.append(player.Player(name=player1))
            player_holder.append(player.Player(name=player2))
        elif len(player_holder) == 1:
            if player1 != "Josh":
                player_holder.insert(0, player.Player(name=player1))
            elif player2 != "Drake":
                player_holder.append(player.Player(name=player2))

        self.player_holder = player_holder
        self.ref = Referee()

        first_name = self.player_holder[0].get_name()
        self.player_holder[0].set_stone("B")
        self.ref.set_player(stone="B", name=first_name)

        second_name = self.player_holder[1].get_name()
        self.player_holder[1].set_stone("W")
        self.ref.set_player(stone="W", name=second_name)


    def run(self):
        game_over = False
        # while not game_over:

        outcome = 1

        # Make referee, set stones of player
        while not game_over:
            for curr_player in self.player_holder:
                try:
                    move = curr_player.n1play(self.ref.rr.board_hist)
                    # Random move -- comment this out to use real ai
                    move = Point.point_to_string((randrange(0, MAX_ROW), randrange(0, MAX_COLUMN)))
                    # print(move)
                # If player disconnects, force ref to end game
                except (ConnectionError, player.PlayerCommandError) as e:
                    move = "GO has gone crazy!"

                outcome = self.ref.execute_turn(move)
                # print(outcome)
                if isinstance(outcome, list) and isinstance(outcome[0], str):
                    game_over = True
                    break

        try:
            ok1 = self.player_holder[0].end_game()
            # print(ok1)
            # print("Gets past first")
            ok2 = self.player_holder[1].end_game()
            # print(ok2)
        except (ConnectionError, ConnectionRefusedError, ConnectionAbortedError, ConnectionResetError):
            pass
        # try:
        #
        # except ConnectionError:
        #     pass

        return outcome

# Test
"""
server = socket(AF_INET, SOCK_STREAM)
server.bind(('', server_info["port"]))
server.listen(1)
connection, address = server.accept()

test_admin = Admin(connections=[connection], player1="localtest")

test_admin.run()
"""