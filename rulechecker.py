

# DEPENDENCIES
# ============
# rulechecker.py requires the ABC class and abstractmethod decorator from abc to implement the
# RuleCheckerInterface class, which guarantees the RuleChecker class has certain functions.
# It requires the constants MAX_ROW and MAX_COLUMN defined in constants.py.
# It requires the type-checking functions from typedefs.
# It needs the functions given by board.py.
# It requires deepcopy to fully copy boards.

#sys.path.append('c:/Users/ctgot/Documents/Northwestern/Sophomore Year/Fall Quarter/CS 393/team8-dev/Deliverables/4/')

from abc import ABC, abstractmethod
from constants import MAX_ROW, MAX_COLUMN
from typedefs import MaybeStone, Point, Ensure
from board import Board, BoardStateError
from copy import deepcopy

# INTERFACE
# =========

# The RuleChecker class is guaranteed to provide the following functions:

class RuleCheckerInterface(ABC):

    # RuleChecker.check_move(stone, point, board_history) ->
    # check_move takes a stone, a point, and a list of boards of length 1-3, representing the previous boards
    # in the game. If trying to place the given stone at the given point would result in a violation of the
    # rules of Go, check_move raises an exception. If the given board history is inconsistent with the rules of
    # Go, check_move also raises an exception.
    @abstractmethod
    def check_move(stone, point, board_history):
        raise NotImplementedError

    # RuleChecker.get_score(board) -> dict
    # get_score takes a board and returns a dict with two keys - 'B' and 'W' - which correspond to the score
    # of each player if that board represents the board at the end of the game.
    @abstractmethod
    def get_score(board):
        raise NotImplementedError

# CUSTOM EXCEPTIONS
# =================
# rulechecker.py provides three custom exceptions: the generic RuleCheckerError, which the other two
# exceptions are subclasses of, IllegalMoveError, which is raised when the move given to check_move would violate
# the rules of Go, and ImproperHistoryError, which is raised when the board history given to check_move is
# inconsistent with the rules of Go.

class RuleCheckerError(Exception):
    """Raised when RuleChecker raises an error."""
    pass

class IllegalMoveError(RuleCheckerError):
    """Raised when a move violates the rules of Go."""
    pass

class ImproperHistoryError(RuleCheckerError):
    """Raised when board history violates the rules of Go."""
    pass

# IMPLEMENTATION
# ==============
# The following class contains the actual implementation of the methods described in RuleCheckerInterface

class RealRuleChecker(RuleCheckerInterface):
    
    def _copy_board(board):
        new_board = deepcopy(board)
        return new_board
    
    
    # Removes opponent stones with no liberties
    def _update_board(stone, board):
        other_player = MaybeStone.flip_stone(stone)
        
        other_player_points = Board.get_points(board, other_player)
        points_for_removal = set()
        
        for point in other_player_points:
            if point not in points_for_removal:
                has_liberties, searched_points = Board.reachable(board, point, " ")
                if not has_liberties:
                    points_for_removal = points_for_removal.union(searched_points)
        
        for point in points_for_removal:
            Board.remove(board, other_player, point)
    
    
    def _find_captured_stones(board):
        board = RealRuleChecker._copy_board(board)
        black_points = Board.get_points(board, "B")
        white_points = Board.get_points(board, "W")
        searched_set = set()
        
        for point in black_points:
            if point not in searched_set:
                has_liberties, searched_points = Board.reachable(board, point, " ")
                searched_set = searched_set.union(searched_points)
                if not has_liberties:
                    return False
                
        searched_set = set()
        
        for point in white_points:
             if point not in searched_set:
                has_liberties, searched_points = Board.reachable(board, point, " ")
                if not has_liberties:
                    return False
        return True
    
    
    def _check_self_capture(point, board):
        if not Board.reachable(board, point, " ")[0]:
            raise IllegalMoveError("Move would cause self-capture")
    
    
    # Makes sure that no more than one stone was placed between boards, returns (stone, point)
    def _board_difference(new_board, old_board):
        placed_points = []
        for row in range(0, MAX_ROW):
            for column in range(0, MAX_COLUMN):
                point = column, row
                if not Board.occupied(old_board, point) and Board.occupied(new_board, point):
                    placed_points.append((new_board[row][column], point))
        
        if len(placed_points) == 0:
            return "pass", "pass"
        elif len(placed_points) == 1:
            # Return (stone, point)
            return placed_points[0]
        else:
            raise ImproperHistoryError("More than one stone was placed in a single turn")
    
    
    # Verifies that the correct player went and that the play updated the board correctly
    def _verify_move(new_board, old_board, should_be_stone):
        played_stone, point = RealRuleChecker._board_difference(new_board, old_board)
        
        # Check turn order
        if played_stone == "pass":
            return "pass"
        elif played_stone != should_be_stone:
            raise ImproperHistoryError("Someone went out of turn")
        
        # Make test board, simulate move on test board
        test_board = RealRuleChecker._copy_board(old_board)
        Board.place(test_board, played_stone, point)
        RealRuleChecker._update_board(played_stone, test_board)
        
        if test_board != new_board:
            raise ImproperHistoryError("History contains bad Go")
        RealRuleChecker._check_self_capture(point, test_board)
        
        return (played_stone, point)
    
    
    def check_move(stone, point, board_history_orig):
        board_history = deepcopy(board_history_orig)
        new_board = RealRuleChecker._copy_board(board_history[0])
        try:
            Board.place(new_board, stone, point)
        except BoardStateError as e:
            raise IllegalMoveError from e
        
        RealRuleChecker._update_board(stone, new_board)
        board_history.insert(0, new_board)
        
        num_boards = len(board_history)
        future_moves = []

        empty_board = Board.make_empty_board()
        # If less than 4 history boards, ensure oldest is empty board.
        if num_boards < 4:
            if board_history[-1] != empty_board:
                raise ImproperHistoryError("Initial board is not empty")
            # Ensure that current turn is correct given start of game
            if num_boards == 2 and stone != "B":
                raise ImproperHistoryError("Black should have gone first")
            elif num_boards == 3 and stone != "W":
                raise ImproperHistoryError("It should be White's turn")
        
        elif num_boards == 4:
            # Ensure that oldest board is valid
            if not RealRuleChecker._find_captured_stones(board_history[3]):
                raise ImproperHistoryError("Oldest board is invalid")
            # Check Ko
            if board_history[0] == board_history[2]:
                raise IllegalMoveError("Move causes Ko")
            if board_history[1] == board_history[3]:
                raise ImproperHistoryError("Ko found in history")
        
        next_stone = stone
        
        for i, board in enumerate(board_history[:-1]):
            if i != 0:
                next_stone = MaybeStone.flip_stone(next_stone)
            move = RealRuleChecker._verify_move(board_history[i], board_history[i+1], next_stone)
            future_moves.append(move)
                
        if num_boards == 4:
            if future_moves[-2:] == ['pass', 'pass']:
                raise IllegalMoveError('The game is over')
            temp_moves = [future_moves[0]]
            for move_index, move in enumerate(future_moves[1:]):
                if move == 'pass':
                    temp_moves.append((MaybeStone.flip_stone(future_moves[move_index-1][0]), 'pass'))
                else:
                    temp_moves.append(move)

            empty_board = Board.make_empty_board()
            if board_history[-1] == empty_board and board_history[-2] == empty_board:
                if temp_moves[-2][0] != 'W':
                    raise ImproperHistoryError('If Black passed the first move, White should go next.')
        
        # most_recent_board = board_history[0]
        # del board_history[0]
        return board_history[0]
    
    
    def get_score(board):
        score_board = RealRuleChecker._copy_board(board)
        empty_points = Board.get_points(score_board, " ")
        white_territory = set()
        black_territory = set()
        neutral_territory = set()
        
        for empty_point in empty_points:
            if empty_point not in neutral_territory.union(black_territory.union(white_territory)):
                reachable_white, connection = Board.reachable(score_board, empty_point, "W")
                
                reachable_black, _ = Board.reachable(score_board, empty_point, "B")
                
                if reachable_white and not reachable_black:
                     white_territory = white_territory.union(connection)
                elif reachable_black and not reachable_white:
                    black_territory = black_territory.union(connection)
                else:
                    neutral_territory = neutral_territory.union(connection)
        
        black_points = len(black_territory) + len(Board.get_points(score_board, "B"))
        white_points = len(white_territory) + len(Board.get_points(score_board, "W"))
        
        return {"B": black_points, "W": white_points}

# WRAPPER CLASS
# =============
# The following class is a wrapper for RealRuleChecker that ensures the correctness of its inputs.

class RuleChecker(RuleCheckerInterface):
    
    def check_move(stone, point, board_history):
        Ensure.ensure_stone('RuleChecker.check_move', stone)
        Ensure.ensure_point('RuleChecker.check_move', point)
        Ensure.ensure_board_history('Rulechecker.check_move', board_history)
        # if type(board_history) != list:
        #     raise TypeError('RuleChecker.check_move expects board_history to be a list')
        # if len(board_history) > 3 or len(board_history) < 1:
        #     raise ValueError('RuleChecker.check_move expects a board history between 1 and 3 boards')
        # for board in board_history:
        #     Ensure.ensure_board('RuleChecker.check_move', board)
        
        try:
            return RealRuleChecker.check_move(stone, point, board_history)
        except RuleCheckerError as e:
            raise e
    
    def get_score(board):
        Ensure.ensure_board('RuleChecker.get_score', board)
        
        return RealRuleChecker.get_score(board)
