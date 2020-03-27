import os
import sys
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from sudoku import util, dfs, deductive
import numpy as np
from tqdm import tqdm


def fill_board():
    code = '0' * 81
    board = util.code_to_board(code)

    guesses = util.generate_guess_list(board)
    np.random.shuffle(guesses)
    for cell in guesses:
        np.random.shuffle(cell['guesses'])
    # print(guesses)

    pbar = tqdm(total=81)
    while(len(guesses)):
        pbar.update(1)
        # while there are empty cells
        random_cell = guesses.pop(0)
        for tentative in random_cell['guesses']:
            forward_valid = True
            # for each guess in the cell, try it and see if it leads to a solution
            board[random_cell['x']][random_cell['y']] = tentative
            updated_guesses = []
            # to update guesses, iterate over all of the old guesses and see if they have to be changed after inserting the new tentative guess
            for old_guess in guesses:
                new_guess = {'x': old_guess['x'], 'y': old_guess['y'], 'guesses': old_guess['guesses'][:]}  # creating a deep copy of the guess
                if tentative in new_guess['guesses']:
                    if new_guess['x'] == random_cell['x'] or new_guess['y'] == random_cell['y'] or (new_guess['x'] // 3 == random_cell['x'] // 3 and new_guess['y'] // 3 == random_cell['y'] // 3):
                        new_guess['guesses'].remove(tentative)
                        # forward checking
                        if len(new_guess['guesses']) == 0:
                            forward_valid = False
                            break
                updated_guesses.append(new_guess)

            if forward_valid:
                try:
                    solution = dfs.dfs_from_board(np.copy(board))
                    guesses = updated_guesses
                    break  # break out of this tentative testing loop
                except util.UnsolvableBoardException:
                    board[random_cell['x']][random_cell['y']] = 0
            else:
                board[random_cell['x']][random_cell['y']] = 0
    pbar.close()

    assert util.board_is_solved(board)
    return board


def generate(filled_board):
    positions = [(util.to_x(i), util.to_y(i)) for i in range(81)]
    np.random.shuffle(positions)
    board = np.copy(filled_board)
    for x, y in tqdm(positions):
        temp = board[x][y]
        board[x][y] = 0
        if dfs.test_unique(np.copy(board)):
            continue
        else:
            board[x][y] = temp
    return board


if __name__ == "__main__":
    filled = fill_board()
    print(util.board_to_code(filled))
    board = generate(filled)
    util.print_board(board)
    print(util.board_to_code(board))
