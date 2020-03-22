import os
import sys
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from sudoku import util


def generate_guess_list(board):
    guesses = []
    for x in range(9):
        for y in range(9):
            if board[x][y] == 0:
                xy_guesses = []
                for i in range(1, 10):
                    board[x][y] = i
                    if util.position_is_valid(board, x, y):
                        xy_guesses.append(i)
                board[x][y] = 0
                guesses.append({'x': x, 'y': y, 'guesses': xy_guesses})
    return sorted(guesses, key=lambda guess: len(guess['guesses']))


def dfs(board_code):
    """Depth first search of board solutions, selecting branches with fewest possible guesses.
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
    """
    board = util.code_to_board(board_code)

    if util.board_is_solved(board):
        return util.board_to_code(board)

    guesses = generate_guess_list(board)
    result = dfs_recursive(board, guesses)
    if result is False:
        raise util.UnsolvableBoardException
    else:
        return util.board_to_code(result)


def dfs_recursive(board, guesses):
    if len(guesses) == 0:
        if util.board_is_solved(board):
            return board
        else:
            return False
    minimum_guesses = guesses.pop(0)
    for tentative in minimum_guesses['guesses']:
        # for each guess in the minimum guess cell, try it and see if it leads to a solution
        board[minimum_guesses['x']][minimum_guesses['y']] = tentative
        updated_guesses = []
        # to update guesses, iterate over all of the old guesses and see if they have to be changed after inserting the new tentative guess
        for old_guess in guesses:
            new_guess = {'x': old_guess['x'], 'y': old_guess['y'], 'guesses': old_guess['guesses'][:]}  # creating a deep copy of the guess
            if tentative in new_guess['guesses']:
                if new_guess['x'] == minimum_guesses['x'] or new_guess['y'] == minimum_guesses['y'] or (new_guess['x'] // 3 == minimum_guesses['x'] // 3 and new_guess['y'] // 3 == minimum_guesses['y'] // 3):
                    new_guess['guesses'].remove(tentative)
                    # forward checking
                    if len(new_guess['guesses']) == 0:
                        return False
            updated_guesses.append(new_guess)
        updated_guesses = sorted(updated_guesses, key=lambda guess: len(guess['guesses']))
        next_step = dfs_recursive(board, updated_guesses)
        if next_step is False:
            continue
        else:
            return next_step

    return False
