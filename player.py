
from abc import ABC, abstractmethod
from constants import MAX_ROW, MAX_COLUMN
from rulechecker import RuleChecker, IllegalMoveError, ImproperHistoryError
from typedefs import MaybeStone, Ensure, Point
from board import Board, BoardStateError
from random import randint
import copy

class PlayerInterface(ABC):
    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    @abstractmethod
    def set_stone(self, stone):
        raise NotImplementedError

    @abstractmethod
    def n1play(self, board_history):
        raise NotImplementedError

    @abstractmethod
    def dumb_play(self, board_history):
        raise NotImplementedError

class PlayerCommandError(Exception):
    """Player Error"""
    pass

class RealPlayer(PlayerInterface):
    
    def __init__(self, strategy="random", name="no name"):
        self.stone = None
        self.strategy = strategy
        self.name = name

    def get_name(self):
        return self.name

    def get_player_name(self):
        return self.name
    
    def set_stone(self, stone):
        if self.stone == None:
            self.stone = stone
        else:
            raise PlayerCommandError('You cannot change the type of stone a player is using.')



    def play(self, strategy, board_history):
        if self.strategy == "random":
            rand_1 = randint(0,MAX_ROW)
            rand_2 = randint(0,MAX_COLUMN)
            return Point.point_to_string((rand_1, rand_2))
        
        elif self.strategy == "n1":
            return self.n1play(board_history)

        elif self.strategy == "dumb":
            return self.dumb_play(board_history)
        
        else:
            raise PlayerCommandError("Undefined Strategy")
    

    def check_for_adjacent_stones(self, stone, point, board):
        column, row = point
        if row == 0:
            north_point = False
        else:
            north_point = column, row - 1
        
        if row == MAX_COLUMN - 1:
            south_point = False
        else:
            south_point = column, row + 1
        
        if column == MAX_ROW - 1:
            east_point = False
        else:
            east_point = column + 1, row
        
        if column == 0:
            west_point = False
        else:
            west_point = column - 1, row
        
        allpoints = [north_point, south_point, east_point, west_point]

        adj_found = False
        for adj_point in allpoints:
            if adj_point:
                adj_col, adj_row = adj_point
                if board[adj_row][adj_col] == stone:
                    # print("adj found", adj_point)
                    return True

        return False


    def n1play(self, board_history):
        if self.stone == None:
            raise PlayerCommandError('You need to set the stone before you can play.')

        current_board = copy.deepcopy(board_history[0])
        opponent_point = MaybeStone.flip_stone(self.stone)

        for column_index in range(MAX_COLUMN):
            for row_index in range(MAX_ROW):
                if self.check_for_adjacent_stones(opponent_point, (column_index,row_index), current_board):
                    try:
                        # Try putting a stone in the current position
                        new_board = RuleChecker.check_move(self.stone, (column_index, row_index), board_history)
                        try:
                            Board.place(current_board, self.stone, (column_index, row_index))
                            # See if capture occurred by comparing with just placing
                            if current_board != new_board:
                                return Point.point_to_string((column_index, row_index))
                            else:
                                Board.remove(current_board, self.stone, (column_index, row_index))
                        except BoardStateError as e:
                            pass
                    except IllegalMoveError as e:
                        pass
                    except ImproperHistoryError as e:
                        # raise PlayerCommandError('Invalid history') from e
                        return 'This history makes no sense!'

        return self.dumb_play(board_history)

    def dumb_play(self, board_history):
        if self.stone == None:
            raise PlayerCommandError('You need to set the stone before you can play.')
        
        current_board = board_history[0]
        for column, maybe_stones in enumerate(current_board):
            for row, maybe_stone in enumerate(current_board):
                try:
                    RuleChecker.check_move(self.stone, (column, row), board_history)
                    return Point.point_to_string((column, row))
                except IllegalMoveError:
                    pass
                except ImproperHistoryError as e:
                    # raise PlayerCommandError('Invalid history') from e
                    return 'This history makes no sense!'
        
        return 'pass'
    
    def beta_play(self, board_history):
# work in progress 
        current_board = board_history[0]
        opponent_point = MaybeStone.flip_stone(self.stone)
        all_opponent_connections = []
        for point in Board.get_points(current_board, opponent_point):
            all_opponent_connections.append(get_blob(current_board, point))
        
        all_opponent_liberties = []
        for connection in all_opponent_connections:
            all_opponent_liberties.append(get_blob_liberties(current_board, connection))
        
        connections_with_one_liberty = set()
        for liberties_set in all_opponent_liberties:
            if len(liberties_set) == 1:
                connections_with_one_liberty.union(liberties_set)
        
        for row, maybe_stones in enumerate(current_board):
            for column, maybe_stone in enumerate(current_board):
                if (column, row) in connections_with_one_liberty:
                    try:
                        RuleChecker.check_move(self.stone, (column, row), board_history)
                        return Point.point_to_string((column, row))
                    except IllegalMoveError:
                        pass
                    except ImproperHistoryError as e:
                        # raise PlayerCommandError('Invalid history') from e
                        return 'This history makes no sense!'
        
        return 'pass'

class Player():
    def __init__(self, n=1, name="no name"):
        self.real_player = RealPlayer(n, name)

    def get_name(self):
        return self.real_player.get_name()

    def get_player_name(self):
        return self.real_player.get_player_name()

    def set_stone(self, stone):
        Ensure.ensure_stone('Player.set_stone', stone)
        return self.real_player.set_stone(stone)
    
    def n1play(self, board_history):
        Ensure.ensure_board_history('Player.play', board_history)
        return self.real_player.n1play(board_history)
    
    def dumb_play(self, board_history):
        Ensure.ensure_board_history('Player.dumb_play', board_history)
        return self.real_player.dumb_play(board_history)

    def end_game(self):
        return "OK"

"""
testplayer = Player()
testplayer.set_stone("B")

testinput1 = [
[[" ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," ","B"," "," "],
 ["W"," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 [" ","W"," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "],
 ["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","W"," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "]],
[[" ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," ","B"," "," "],
 ["W"," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "],
 ["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","W"," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "]],
[[" ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "," "," "],
 ["B","B","B","B","B","B","B","B","B","B","B","B","B","B","B","W"," "," "," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "," "],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"," "],
 ["W"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," ","W"],
 ["B"," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "," "]]
]

testoutput = testplayer.n1play(testinput1)
"""