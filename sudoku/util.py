import numpy as np


class InvalidBoardException(Exception):
    """Raised when a board is invalid."""
    pass


class UnsolvableBoardException(Exception):
    """Raised when backtracking is used to solve a board with no solutions."""
    pass


def to_x(n):
    """Converts a code index to a board x coordinate.

    Parameters
    ----------
    n : int
        Board code index to be converted.

    Returns
    -------
    int
        x coordinate.
    """
    return int(n % 9)


def to_y(n):
    """Converts a code index to a board y coordinate.

    Parameters
    ----------
    n : int
        Board code index to be converted.

    Returns
    -------
    int
        y coordinate.
    """
    return n // 9


def board_is_valid(board):
    """Checks whether a board array is valid (well constructed, not necessarily solved or solvable).

    Parameters
    ----------
    board : ndarray
        Board array.

    Returns
    -------
    bool
        Whether the board is valid or not.
    """
    if type(board) != np.ndarray:
        return False
    if board.shape != (9, 9):
        return False
    if not ((board >= 0).all() and (board <= 9).all()):
        return False
    return True


def code_to_board(code):
    """Converts a board code to a board array.

    Parameters
    ----------
    code : string
        81 character board code listed from top left to bottom right.
        Empty spaces are represented with zeros.

    Returns
    -------
    ndarray
        Board in array representation.

    Raises
    ------
    InvalidBoardCodeException
        If the board code doesn't represent a sudoku board.
    """
    if type(code) != str:
        raise InvalidBoardException(f'Board code must be a string, got type {type(code)}')
    if(len(code) != 9 * 9):
        raise InvalidBoardException(
            "Board code must be 81 characters long")
    for c in code:
        if not (ord(c) >= 48 and ord(c) <= 57):
            raise InvalidBoardException(
                f"Board code must only contain numbers 0 - 9")
    board = np.zeros((9, 9), np.int8)

    for i in range(9 * 9):
        x = to_x(i)
        y = to_y(i)
        board[x][y] = int(code[i])
    return board.T


def board_to_code(board):
    """Converts a board array to a code-string.

    Parameters
    ----------
    board : ndarray

    Returns
    -------
    string
        81 character board code listed from top left to bottom right.
        Empty spaces are represented with zeros.

    Raises
    ------
    InvalidBoardException
        If the board is invalid.
    """
    if not board_is_valid(board):
        raise InvalidBoardException
    code = ''
    for y in range(9):
        for x in range(9):
            code += str(board.T[x][y])
    return code


def board_is_solved(board):
    """Checks whether a board is solved.

    Parameters
    ----------
    board : ndarray

    Returns
    -------
    bool
        Whether or not the board is solved.
    Raises
    ------
    InvalidBoardException
        If the board is invalid.
    """
    if not board_is_valid(board):
        raise InvalidBoardException
    for x in range(9):
        for y in range(9):
            if(not position_is_valid(board, x, y)):
                return False
    return True


def position_is_valid(board, x, y):
    """Checks whether a specific position on a board is solved.

    Parameters
    ----------
    board : ndarray
    x : int
        x coordinate of the position to be tested.
    y : int
        y coordinate of the position to be tested.

    Returns
    -------
    bool
        Whether or not the board positon is valid.

    Raises
    ------
    IndexError
        If the (x,y) position is out of bounds.
    """

    # if there are guesses in this position
    # if type(board[x][y]) != int:
    #     return False
    if board[x][y] <= 0 or board[x][y] > 9:
        return False
    # rowwise search
    yy = y
    for xx in range(9):
        if xx == x:
            continue
        if board[xx][yy] == board[x][y]:
            return False

    # columnwise search
    xx = x
    for yy in range(9):
        if yy == y:
            continue
        if board[xx][yy] == board[x][y]:
            return False

    # boxwise search
    for xx in range((x // 3) * 3, (x // 3) * 3 + 3):
        for yy in range((y // 3) * 3, (y // 3) * 3 + 3):
            if xx == x and yy == y:
                continue
            if board[xx][yy] == board[x][y]:
                return False

    return True


def print_board(board):
    """Pretty prints a board to console.
    """
    if board.shape == (9, 9):
        for x in range(9):
            line = ''
            for y in range(9):
                line += str(board[x][y] or '_') + ' '
            print(line)
    elif board.shape == (9, 9, 9):
        thic_chars = "┃━┏┓┗┛"
        thic_chars = "║═╔╗╚╝"
        thin_chars = "│─┌┐└┘"
        print_width = (3 * 9 * 2 + 17)
        print(thic_chars[2] + thic_chars[1] * print_width + thic_chars[3])
        for x in range(9):
            lines = [thic_chars[0] + ' ' for i in range(3)]
            for y in range(9):
                if sum(board[x][y]) == 1:
                    # confirmed position
                    lines[0] += ' ' * 6
                    lines[1] += f'\033[1;32m  {np.argmax(board[x][y]) + 1}   \033[0;37m'
                    lines[2] += ' ' * 6
                else:
                    for z in range(9):
                        if board[x][y][z] == 1:
                            lines[z // 3] += '\033[0;34m' + str(z + 1) + ' \033[0;37m'
                        else:
                            lines[z // 3] += '  '
                if (y + 1) % 3 == 0:
                    lines[0] += thic_chars[0] + ' '
                    lines[1] += thic_chars[0] + ' '
                    lines[2] += thic_chars[0] + ' '
                else:
                    lines[0] += thin_chars[0] + ' '
                    lines[1] += thin_chars[0] + ' '
                    lines[2] += thin_chars[0] + ' '
            for line in lines:
                print(line)
            if x == 2 or x == 5:
                print(thic_chars[0] + thic_chars[1] * print_width + thic_chars[0])
            elif x == 8:
                print(thic_chars[4] + thic_chars[1] * print_width + thic_chars[5])
            else:
                print(thic_chars[0] + thin_chars[1] * print_width + thic_chars[0])


def load(json_path):
    import json
    sudokus = {}
    with open(json_path) as json_file:
        sudokus = json.loads(json_file.read())

    return sudokus


def update_guesses(board, x, y):
    """Takes a 3D guess board and cell coordinate and removes guesses from similar columns, rows and boxes.
    Parameters
    ----------
    board : ndarray

    Returns
    -------
    None
    """
    # TODO we should really check that the square contains only one guess?
    assert np.sum(board[x][y]) == 1, 'update_guesses should only be called on a confirmed square'
    for z in range(9):
        if board[x][y][z] == 0:
            continue
        yy = y
        for xx in range(9):
            if xx == x:
                continue
            board[xx][yy][z] = 0
        xx = x
        for yy in range(9):
            if yy == y:
                continue
            board[xx][yy][z] = 0

        for xx in range((x // 3) * 3, (x // 3) * 3 + 3):
            for yy in range((y // 3) * 3, (y // 3) * 3 + 3):
                if xx == x and yy == y:
                    continue
                board[xx][yy][z] = 0


def init_guesses(board):
    """Converts a 2D board to a 3D array with 9 slots for cell guesses.

    Parameters
    ----------
    board : ndarray

    Returns
    -------
    ndarray
        3D board with guesses filled in.

    Raises
    ------
    InvalidBoardException
        If the board is invalid.
    """

    if not board_is_valid(board):
        raise InvalidBoardException

    guess_board = np.full((9, 9, 9), [1, 1, 1, 1, 1, 1, 1, 1, 1])
    for x in range(9):
        for y in range(9):
            if board[x][y] != 0:
                for z in range(9):
                    guess_board[x][y] = 0
                guess_board[x][y][board[x][y] - 1] = 1
                # remove this guess from row, column and box
                update_guesses(guess_board, x, y)

    return guess_board
