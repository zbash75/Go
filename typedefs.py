
# PURPOSE
# =======
# This file contains definitions for the "types" used throughout this project, as well as functions for common
# operations on them, functions for ensuring their correctness, and a few helpful constants.

# DEPENDENCIES
# ============
# This file depends on constants.py for information on the size of a board.

from constants import MAX_ROW, MAX_COLUMN

# DEFINITIONS
# ===========
#
# A stone is a string, specifically, either 'B' or 'W'.
#
# An empty is the string ' '.
#
# A maybe_stone is either a stone or an empty.
#
# A board_row is a MAX_COLUMN long list of maybe_stones.
#
# A board is a MAX_ROW long list of board_rows.
#
# A point is a tuple of the form (column, row), where column and row are zero-indexed and refer to points on
# a board.
#
# A play is either a point or the string 'pass'
#
# 
#
# A blob is a set of points that are all adjacent to at least one other point in the blob and are all the same
# type of maybe_stone on a board.

# FUNCTIONS
# =========

class MaybeStone:
    # is_stone returns true is a string is a stone
    def is_stone(string):
        return string == 'B' or string == 'W'
    
    
    # is_empty returns true if is_empty is an empty
    def is_empty(string):
        return string == ' '
    
    
    # flip_stone swaps between stone types
    def flip_stone(stone):
        if MaybeStone.is_stone(stone):
            if stone == 'B':
                return 'W'
            if stone == 'W':
                return 'B'
        else:
            raise TypeError('Cannot flip empty stone')


# empty_board is just a board full of emptys
empty_board = [[' ' for column in range(0, MAX_COLUMN)] for row in range(0, MAX_ROW)]


class Point:
    # Points are commonly read from JSON in the form "column-row"; where column and row are integers.
    # These two functions convert between strings and points.
    
    # string_to_point takes a string of the form "column-row" and converts it to a point
    def string_to_point(string):
        column, row = string.split('-')
        return int(column) - 1, int(row) - 1
    
    # point_to_string takes a point and converts it to a string of the form 
    def point_to_string(point):
        column, row = point
        return str(column + 1) + '-' + str(row + 1)
    
    
    # neighbor_points takes a point and returns the points north, south, east, and west of it, if any
    def neighbor_points(point):
        column, row = point
        neighbors = []
        if row > 0:
            neighbors.append((column, row - 1))
        if row < MAX_ROW - 1:
            neighbors.append((column, row + 1))
        if column > 0:
            neighbors.append((column - 1, row))
        if column < MAX_COLUMN - 1:
            neighbors.append((column + 1, row))
        return neighbors


class Ensure:
    # The following functions provide validity checks for each type passed to functions.
    def ensure_stone(location, stone):
        if type(stone) != str:
            raise TypeError(location + ' expects stone to be a str, given a ' + str(type(stone)))
        elif not (stone == 'W' or stone == 'B'):
            raise ValueError(location + '  expects stone to be "B" or "W", given "' + stone + '"')
    
    
    def ensure_maybe_stone(location, maybe_stone):
        if type(maybe_stone) != str:
            raise TypeError(location + ' expects maybe_stone to be a str, given a ' + str(type(maybe_stone)))
        elif not (maybe_stone == 'W' or maybe_stone == 'B' or maybe_stone == ' '):
            raise ValueError(location + '  expects maybe_stone to be "B", "W", or " ", given "' + maybe_stone + '"')
    
    
    def ensure_point(location, point):
        if type(point) != tuple:
            raise TypeError(location + ' expects point to be a tuple, given a ' + str(type(point)))
        elif len(point) != 2:
            raise ValueError(location + ' expects point to be a tuple of length 2, given  ' + str(point))
        elif (point[0] < 0 or point[0] >= MAX_COLUMN) or (point[1] < 0 or point[1] >= MAX_ROW):
            raise ValueError(location + ' was given an out of bounds point: ' + str(point))
    
    
    def ensure_board(location, board):
        if type(board) != list:
            raise TypeError(location + ' expects board to be a list, given a ' + str(type(board)))
        elif len(board) != MAX_ROW:
            raise ValueError(location + ' expects board to be a ' + str(MAX_ROW) + ' long list, given a ' \
                             + str(len(board)) + ' long list')
        for row in board:
            if type(row) != list:
                raise TypeError(location + ' expects board to be a list of lists: given a list with at least one ' \
                                + str(type(row)))
            elif len(row) != MAX_COLUMN:
                raise ValueError(location + ' expects board to be a list of ' + str(MAX_COLUMN) \
                                 + ' long lists, given a list with at least one ' + str(len(row)) + ' long list')
            for maybe_stone in row:
                Ensure.ensure_maybe_stone(location, maybe_stone)
    
    
    def ensure_board_history(location, board_history):
        if type(board_history) != list:
            raise TypeError(location + ' expects board_history to be a list, given a ' + str(type(board)))
        elif len(board_history) < 1 or len(board_history) > 3:
            raise ValueError(location + ' expects board_history to be a list between 1 and 3 boards long')
        
        for board in board_history:
            Ensure.ensure_board(location, board)
    
    
    def ensure_blob(location, blob):
        if type(blob) != set:
            raise TypeError(location + ' expects blob to be a set, given a ' + str(type(blob)))
        
        for point in blob:
            Ensure.ensure_point(location, point)
