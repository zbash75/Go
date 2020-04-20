
# DESCRIPTION
# ===========
# board.py provides an implementation of a Go board.

# USAGE
# =====
# To use board.py, you should import Board from board.py and create an instance of it,
# which you can query for information or give commands to change the state of the
# internal board. As an initialization argument, you either give it nothing, in which
# case it will create its own board, or an array of arrays, which should be a MAX_ROW
# by MAX_COLUMN matrix consisting of elements which are either " ", "B", or "W"

# DEPENDENCIES
# ============
# board.py requires the ABC class and the abstractmethod decorator from abc to implement BoardInterface,
# which guarantees the Board class has certain fuctions.
# It requires the constants MAX_ROW and MAX_COLUMN defined in constants.py.
# It requires the type-checking functions from typedefs.py.

#sys.path.append('c:/Users/ctgot/Documents/Northwestern/Sophomore Year/Fall Quarter/CS 393/team8-dev/Deliverables/5/')

from abc import ABC, abstractmethod
from constants import MAX_ROW, MAX_COLUMN
from typedefs import MaybeStone, Point, Ensure

# INTERFACE
# =========
# 
# The Board class is guaranteed to provide the following functions:

class BoardInterface(ABC):

    # Board.occupied(board, point) -> boolean
    # occupied takes a board and a point and returns true if there is a stone at the given
    # point on the given board
    @abstractmethod
    def occupied(board, point):
        raise NotImplementedError

    # Board.occupies(board, stone, point) -> boolean
    # occupies takes a board, a stone, and a point, and returns true if the given board has
    # a stone of the given type at the given point
    @abstractmethod
    def occupies(board, stone, point):
        raise NotImplementedError

    # Board.reachable(board, point, maybe_stone) -> boolean, set
    # reachable takes a board, a point and a maybe_stone, and searches the given board for
    # the given maybe_stone, looking at all maybe_stones adjacent to the given point, and
    # searching all the adjacent points to those if they are of the same type of maybe_stone
    # as the maybe_stone at the given point
    #
    # Effectively, this function finds the group of adjacent maybe_stones at the given point,
    # and returns true if the given maybe_stone is adjacent to any maybe_stone in the group
    # and false otherwise, as well as returning the set of points that were searched
    @abstractmethod
    def reachable(board, point, maybe_stone):
        raise NotImplementedError

    # Board.place(stone, point) -> board
    # place takes a stone and a point, and returns the given board with the given stone
    # placed at the given point. If a stone already occupies the given point, place will
    # raise a BoardStateError
    @abstractmethod
    def place(board, stone, point):
        raise NotImplementedError

    # Board.remove(board, stone, point) -> board
    # remove takes a stone and a point, and returns the given board with the stone
    # at the given point removed. If the maybe_stone at the given point does not equal the given
    # stone, remove will raise a BoardStateError
    @abstractmethod
    def remove(board, stone, point):
        raise NotImplementedError

    # Board.get_points(board, maybe_stone) -> point[]
    # get_points takes a maybe_stone and iterates over the given board, returning a list
    # of the points that are occupied by that maybe_stone
    @abstractmethod
    def get_points(board, maybe_stone):
        raise NotImplementedError

# CUSTOM EXCEPTIONS
# =================
# board.py provides a single custom exception: BoardStateError, which is raised when a
# command isn't valid, given the current state of the board

class BoardStateError(Exception):
    """Raised when a command cannot be executed on the current board."""
    pass

class RealBoard(BoardInterface):
    
    def occupied(board, point):
        column, row = point
        return MaybeStone.is_stone(board[row][column])
    
    
    def occupies(board, stone, point):
        column, row = point
        return board[row][column] == stone
    
    
    # Recursive helper function for reachable
    def _reachable_helper(board, current_point, maybe_stone, searched_points):
        
        column, row = current_point
        
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
        
        current_stone = board[row][column]
        searched_points.add(current_point)
        
        if current_stone == maybe_stone:
            return True
        
        # Helper function for reachable_helper
        def search_if_maybe_stone(point):
            if not point:
                return False
            
            column, row = point
            
            if board[row][column] == maybe_stone:
                return True
            elif board[row][column] == current_stone and point not in searched_points:
                return RealBoard._reachable_helper(board, point, maybe_stone, searched_points)
            else:
                return False
        
        north_point = search_if_maybe_stone(north_point)
        south_point = search_if_maybe_stone(south_point)
        east_point = search_if_maybe_stone(east_point)
        west_point = search_if_maybe_stone(west_point)
        
        return north_point or south_point or east_point or west_point
    
    
    def reachable(board, point, maybe_stone):
        searched_points = set()
        return (RealBoard._reachable_helper(board, point, maybe_stone, searched_points), searched_points)
    
    
    def place(board, stone, point):
        column, row = point
        if not RealBoard.occupied(board, point):
            board[row][column] = stone
        else:
            raise BoardStateError('Cannot place a stone on an occupied point.')    
    
    
    def remove(board, stone, point):
        column, row = point
        if RealBoard.occupies(board, stone, point):
            board[row][column] = ' '
        else:
            raise BoardStateError('Cannot remove a stone that is not there.')
    
    
    def get_points(board, maybe_stone):
        points_list = []
        for row_index, row in enumerate(board):
            for column_index, point in enumerate(row):
                if point == maybe_stone:
                    points_list.append((column_index, row_index))
        return points_list
    
    
    def _blob_walk(board, point, blob_stone, walked_points):
        walked_points.add(point)
        for neighbor_point in Point.neighbor_points(point):
            if neighbor_point not in walked_points and Board.occupies(board, blob_stone, neighbor_point):
                RealBoard._blob_walk(board, neighbor_point, blob_stone, walked_points)
    
    
    def get_blob(board, point):
        column, row = point
        blob_stone = board[row][column]
        walked_points = set()
        RealBoard._blob_walk(board, point, blob_stone, walked_points)
        return walked_points
    
    
    def get_blob_liberties(board, blob):
        blob_liberties = set()
        for point in blob:
            neighbor_points = Point.neighbor_points(point)
            for neighbor_point in neighbor_points:
                if not Board.occupied(board, neighbor_point):
                    blob_liberties.add(neighbor_point)
        return blob_liberties
    
    
    def get_blobs(board, maybe_stone):
        blobs = []
        searched_points = set()
        points_to_search = Board.get_points(board, maybe_stone)
        for point in points_to_search:
            if point not in searched_points:
                new_blob = Board.get_blob(board, point)
                blobs.append(new_blob)
                searched_points = searched_points.union(new_blob)
        return blobs
    
    
    def make_empty_board():
        empty_board = [[' ' for column in range(0, MAX_COLUMN)] for row in range(0, MAX_ROW)]
        return empty_board


# Wrapper class for RealBoards
# This class just ensures the inputs to a RealBoard are valid
class Board(BoardInterface):
    
    def occupied(board, point):
        Ensure.ensure_board('Board.occupied', board)
        Ensure.ensure_point('Board.occupied', point)
        return RealBoard.occupied(board, point)
    
    
    def occupies(board, stone, point):
        Ensure.ensure_board('Board.occupies', board)
        Ensure.ensure_stone('Board.occupies', stone)
        Ensure.ensure_point('Board.occupies', point)
        return RealBoard.occupies(board, stone, point)
    
    
    def reachable(board, point, maybe_stone):
        Ensure.ensure_board('Board.reachable', board)
        Ensure.ensure_point('Board.reachable', point)
        Ensure.ensure_maybe_stone('Board.reachable', maybe_stone)
        return RealBoard.reachable(board, point, maybe_stone)
    
    
    def place(board, stone, point):
        Ensure.ensure_board('Board.place', board)
        Ensure.ensure_stone('Board.place', stone)
        Ensure.ensure_point('Board.place', point)
        return RealBoard.place(board, stone, point)
    
    
    def remove(board, stone, point):
        Ensure.ensure_board('Board.remove', board)
        Ensure.ensure_stone('Board.remove', stone)
        Ensure.ensure_point('Board.remove', point)
        return RealBoard.remove(board, stone, point)
    
    
    def get_points(board, maybe_stone):
        Ensure.ensure_board('Board.get_points', board)
        Ensure.ensure_maybe_stone('Board.get_points', maybe_stone)
        return RealBoard.get_points(board, maybe_stone)
    
    
    def get_blob(board, point):
        Ensure.ensure_board('Board.get_blob', board)
        Ensure.ensure_point('Board.get_blob', point)
        return RealBoard.get_blob(board, point)
    
    
    def get_blob_liberties(board, blob):
        Ensure.ensure_board('Board.get_blob_liberties', board)
        Ensure.ensure_blob('Board.get_blob_liberties', blob)
        return RealBoard.get_blob_liberties(board, blob)
    
    
    def get_blobs(board, maybe_stone):
        Ensure.ensure_board('Board.get_blobs', board)
        Ensure.ensure_maybe_stone('Board.get_blobs', maybe_stone)
        return RealBoard.get_blobs(board, maybe_stone)
    
    
    def make_empty_board():
        return RealBoard.make_empty_board()
