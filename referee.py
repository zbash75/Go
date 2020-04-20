from abc import ABC, abstractmethod
from constants import MAX_ROW, MAX_COLUMN
from typedefs import MaybeStone, Point, Ensure, empty_board
from rulechecker import RuleChecker, RuleCheckerError
from copy import deepcopy


class RefereeInterface(ABC):

    @abstractmethod
    def set_player(self, stone, name):
        raise NotImplementedError

    @abstractmethod
    def execute_turn(self, action):
        raise NotImplementedError

    @abstractmethod
    def end_game(self, name):
        raise NotImplementedError


class RefereeError(Exception):
    """Raised when Referee encounters an error."""
    pass


class RealReferee(RefereeInterface):

    # Class variables
    # current_turn
    # board_hist
    # last_turn_was_pass
    # black_player
    # white_player

    def __init__(self, current_turn = "B", board_hist = [empty_board], last_turn_was_pass = False):
        self.current_turn = current_turn
        self.board_hist = board_hist
        self.last_turn_was_pass = last_turn_was_pass
        self.black_player = None
        self.white_player = None

    def set_player(self, stone, name):
        if stone == "B":
            self.black_player = name
            # return "B"
        elif stone == "W":
            self.white_player = name
            # return "W", deepcopy(self.board_hist)
        else:
            raise RefereeError("Illegal stone in naming")

    def _update_history(self, new_board):
    #Update board history

        self.board_hist.insert(0, new_board)
        if len(self.board_hist) >= 4:
            self.board_hist.pop()
        
        self.current_turn = MaybeStone.flip_stone(self.current_turn)
    
    def execute_turn(self, action):
        # Check for double pass
        if action == "pass":
            if not self.last_turn_was_pass:
                self.last_turn_was_pass = True
                self._update_history(self.board_hist[0])
                return deepcopy(self.board_hist)
                
            elif self.last_turn_was_pass:
                return self.end_game()
        
        elif action == "GO has gone crazy!" or action == "This history makes no sense!":
            if self.current_turn == "B":
                return self.end_game(self.black_player)
            else:
                return self.end_game(self.white_player)

        else:
            self.last_turn_was_pass = False
            action = Point.string_to_point(action)
            try:
                new_board = RuleChecker.check_move(self.current_turn, action, self.board_hist)
            
                self._update_history(new_board)

                return deepcopy(self.board_hist)

            except RuleCheckerError as e:
                if self.current_turn == "B":
                    return self.end_game(self.black_player)
                else:
                    return self.end_game(self.white_player)
    
    def end_game(self, committed_illegal=""):
        # Checks the score using RuleChecker and returns the name(s) of the winner(s)
        
        score = RuleChecker.get_score(self.board_hist[0])
        black_score = score["B"]
        white_score = score["W"]

        # Cheating players: winning player, cheating player, cheating flag
        if committed_illegal == self.black_player:
            return [self.white_player, self.black_player, 2]
        elif committed_illegal == self.white_player:
            return [self.black_player, self.white_player, 2]

        if black_score > white_score:
            return [self.black_player]

        elif white_score > black_score:
            return [self.white_player]

        elif black_score == white_score:
            winners = [self.black_player, self.white_player]
            return winners


class Referee(RefereeInterface):

    def __init__(self):
        self.rr = RealReferee()

    def set_player(self, stone, name):
        Ensure.ensure_stone('Referee.set_player', stone)
        try:
            self.rr.set_player(stone, name)
        except RefereeError as e:
            raise e

    def execute_turn(self, action):
        return self.rr.execute_turn(action)

    def end_game(self, committed_illegal):
        return self.rr.end_game(committed_illegal)
