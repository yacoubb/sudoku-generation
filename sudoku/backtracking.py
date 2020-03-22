import os
import sys
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from sudoku import util
import numpy as np


def naiive_backtrack(board_code):
    """Naiive backtracking algorithm used to find the solution to a board with missing clues.
    Parameters
    ----------
    board_code : string
        Board code listed from top left to bottom right.

    Returns
    -------
    string
        Board code for solved board.

    Raises
    ------
    UnsolvableBoardException
        If the board does not have a solution.

    InvalidBoardException
        If the board code is invalid.
    """
    board = util.code_to_board(board_code)
    if not util.board_is_valid(board):
        raise util.InvalidBoardException
    search_board = np.copy(board)

    if util.board_is_solved(board):
        return util.board_to_code(board)

    position = 0
    step = 0
    while True:
        step += 1
        if position == 81:
            if not util.board_is_solved(search_board):
                raise util.InvalidBoardException  # if we got here when solving there must have been an issue with the board code
            print(f'Solved board in {step} steps')
            return util.board_to_code(search_board)

        x = util.to_x(position)
        y = util.to_y(position)

        if board[x][y] != 0:
            position += 1
            continue
        while search_board[x][y] <= 9:
            search_board[x][y] += 1
            if util.position_is_valid(search_board, x, y):
                position += 1
                break

        if search_board[x][y] == 10:
            search_board[x][y] = 0
            position -= 1
            if position < 0:
                raise util.UnsolvableBoardException
            while board[util.to_x(position)][util.to_y(position)] != 0:
                position -= 1
                if position < 0:
                    raise util.UnsolvableBoardException


def naiive_backtrack_count(board_code):
    """Naiive backtracking algorithm used to count solutions to a board with missing clues.
    Parameters
    ----------
    board_code : string
        Board code listed from top left to bottom right.

    Returns
    -------
    int
        The number of unique solutions the board has.
    """
    board = util.code_to_board(board_code)
    search_board = np.copy(board)

    if util.board_is_solved(board):
        return 1

    position = 0
    step = 0
    solutions = 0
    while True:
        step += 1
        if position == 81:
            if not util.board_is_solved(search_board):
                raise util.InvalidBoardException
            solutions += 1
            position -= 1
            while board[util.to_x(position)][util.to_y(position)] != 0:
                position -= 1
                if position < 0:
                    print(f'found {solutions} solutions in {step} steps')
                    return solutions

        x = util.to_x(position)
        y = util.to_y(position)

        if board[x][y] != 0:
            position += 1
            continue
        while search_board[x][y] <= 9:
            search_board[x][y] += 1
            if util.position_is_valid(search_board, x, y):
                position += 1
                break
        if search_board[x][y] == 10:
            search_board[x][y] = 0
            position -= 1
            if position < 0:
                print(f'found {solutions} solutions in {step} steps')
                return solutions
            while board[util.to_x(position)][util.to_y(position)] != 0:
                position -= 1
                if position < 0:
                    print(f'found {solutions} solutions in {step} steps')
                    return solutions
