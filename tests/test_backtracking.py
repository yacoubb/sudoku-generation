import os
import sys
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from sudoku import util, backtracking
import numpy as np
from tqdm import tqdm
import pytest


sudokus = util.load('/'.join(os.path.abspath(__file__).split('/')[:-2]) + '/tests/test-boards.json')

test_guess_count = 34
test_list = sudokus[str(test_guess_count)]
assert len(test_list) == 2000
print(f'{len(test_list)} test boards of with {test_guess_count} guesses each')


def test_backtrack(n=1):
    # testing solved board
    code = sudokus['81'][0]
    solution = backtracking.naiive_backtrack(code)
    assert util.board_is_solved(util.code_to_board(solution))

    # testing unsolveable board
    code = sudokus['81'][0]
    code = '77' + code[2:]
    with pytest.raises(util.InvalidBoardException):
        solution = backtracking.naiive_backtrack(code)

    import random
    for i in tqdm(range(n)):
        code = test_list.pop(np.random.randint(0, len(test_list)))
        solution = backtracking.naiive_backtrack(code)
        assert util.board_is_solved(util.code_to_board(solution))
    print(f'naiive backtrack solved {n} boards')


def test_backtrack_count(n=1):
    # testing solved board
    code = sudokus['81'][0]
    solutions = backtracking.naiive_backtrack_count(code)
    assert solutions == 1

    # testing unsolveable board
    code = sudokus['81'][0]
    code = '77' + code[2:]
    with pytest.raises(util.InvalidBoardException):
        solution = backtracking.naiive_backtrack_count(code)

    import random
    for i in tqdm(range(n)):
        code = test_list.pop(np.random.randint(0, len(test_list)))
        solutions = backtracking.naiive_backtrack_count(code)
        assert solutions == 1
    print(f'backtrack counting solved {n} boards')
