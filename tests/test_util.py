import os
import sys
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from sudoku import util
import pytest
import numpy as np
import json

with open('/'.join(os.path.abspath(__file__).split('/')[:-2]) + '/tests/test-boards.json', 'r') as boards_file:
    boards = json.load(boards_file)


def test_coordinate_conversions():
    for i in range(200):
        assert util.to_x(i) == i % 9
        assert util.to_y(i) == i // 9


def test_board_validity():
    board = []
    assert util.board_is_valid(board) == False
    board = np.zeros((6, 9))
    assert util.board_is_valid(board) == False
    board = np.zeros((9, 9))
    board[0][0] = -1
    assert util.board_is_valid(board) == False
    board[0][0] = 10
    assert util.board_is_valid(board) == False
    board = util.code_to_board(boards['24'][0])
    assert util.board_is_valid(board) == True


def test_code_to_board():
    code = 3
    with pytest.raises(util.InvalidBoardException) as err:
        util.code_to_board(code)
    assert f'Board code must be a string, got type {type(3)}' in str(err.value)
    code = '33'
    with pytest.raises(util.InvalidBoardException) as err:
        util.code_to_board(code)
    assert 'Board code must be 81 characters long' in str(err.value)
    code = 'a' * 81
    with pytest.raises(util.InvalidBoardException) as err:
        util.code_to_board(code)
    assert 'Board code must only contain numbers 0 - 9' in str(err.value)

    code = '000304907830000000000600000050080000006250030000000806009000400000000001000023000'
    board = util.code_to_board(code)
    for i in range(9 * 9):
        x = util.to_x(i)
        y = util.to_y(i)
        assert board[x][y] == int(code[i])


def test_board_to_code():
    board = []
    with pytest.raises(util.InvalidBoardException):
        util.board_to_code(board)

    board = util.code_to_board(boards['24'][0])
    assert util.board_to_code(board) == boards['24'][0]


def test_board_is_solved():
    board = util.code_to_board(boards['81'][0])
    board[0][0] = -1
    with pytest.raises(util.InvalidBoardException):
        util.board_is_solved(board)

    board = util.code_to_board(boards['24'][0])
    assert not util.board_is_solved(board)

    board = util.code_to_board(boards['81'][0])
    assert util.board_is_solved(board)


def test_position_is_valid():
    board = util.code_to_board(boards['81'][0])
    board[0][0] = -1
    assert not util.position_is_valid(board, 0, 0)

    board = util.code_to_board(boards['81'][0])
    board[0][4] = board[0][0]
    assert not util.position_is_valid(board, 0, 0)
    assert not util.position_is_valid(board, 0, 4)

    board = util.code_to_board(boards['81'][0])
    board[4][0] = board[0][0]
    assert not util.position_is_valid(board, 0, 0)
    assert not util.position_is_valid(board, 4, 0)

    board = util.code_to_board(boards['81'][0])
    board[1][1] = board[0][0]
    assert not util.position_is_valid(board, 0, 0)
    assert not util.position_is_valid(board, 1, 1)

    board = util.code_to_board(boards['81'][0])
    for i in range(9 * 9):
        x = util.to_x(i)
        y = util.to_y(i)
        assert util.position_is_valid(board, x, y)


def test_print():
    # TODO implement this
    util.print_board(util.code_to_board(boards['81'][0]))


def test_load_json():
    loaded = util.load('/'.join(os.path.abspath(__file__).split('/')[:-2]) + '/tests/test-boards.json')
    for key in boards:
        assert key in loaded
