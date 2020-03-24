import os
import sys
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))
from sudoku import util
from sudoku.util import load, code_to_board, init_guesses, update_guesses, print_board
import numpy as np

# Implementing techniques from https://www.sudokuwiki.org/


def units(x, y):
    #  returns coordinates of cells with similar units to (x,y)
    col = []
    xx = x
    for yy in range(9):
        col.append((xx, yy))
    row = []
    yy = y
    for xx in range(9):
        row.append((xx, yy))
    box = []
    for xx in range((x // 3) * 3, (x // 3) * 3 + 3):
        for yy in range((y // 3) * 3, (y // 3) * 3 + 3):
            box.append((xx, yy))
    return row, col, box

# basic strategies


def naked_single_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) != 1:
                continue
            xy_units = units(x, y)
            removed = False
            candidate = np.argmax(board[x][y])
            for unit in xy_units:
                for (searchX, searchY) in unit:
                    if (searchX, searchY) == (x, y):
                        continue
                    if board[searchX][searchY][candidate] == 1:
                        board[searchX][searchY][candidate] = 0
                        removed = True
            if removed:
                relevant_cells = [(x, y)]
                relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in relevant_cells]
                return (True, relevant_cells, np.array(relevant_candidates))
    return False, None, None


def naked_pairs_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) != 2:
                continue
            xy_units = units(x, y)
            for unit in xy_units:
                found_pair = False
                for (x1, y1) in unit:
                    if (x1, y1) == (x, y):
                        continue
                    if np.array_equal(board[x][y], board[x1][y1]):
                        found_pair = True
                        break

                if found_pair:
                    removed = False
                    for (searchX, searchY) in unit:
                        if (searchX, searchY) == (x, y) or (searchX, searchY) == (x1, y1):
                            continue
                        for zz in range(9):
                            if board[x][y][zz] == 1:
                                if board[searchX][searchY][zz] == 1:
                                    removed = True
                                    board[searchX][searchY][zz] = 0
                    if removed:
                        relevant_cells = [(x, y), (x1, y1)]
                        relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in relevant_cells]
                        return (True, relevant_cells, np.array(relevant_candidates))
    return False, None, None


def naked_triples_scan(board):
    for x in range(9):
        for y in range(9):
            # find 3 cells with a total of 3 numbers
            # every cell has to have at least 2 guesses
            if np.sum(board[x][y]) != 2 and np.sum(board[x][y]) != 3:
                continue
            xy_units = units(x, y)
            for unit in xy_units:
                found_triple = False
                for (x1, y1) in unit:
                    if np.sum(board[x1][y1]) != 2 and np.sum(board[x1][y1]) != 3:
                        continue
                    for (x2, y2) in unit:
                        if np.sum(board[x2][y2]) != 2 and np.sum(board[x2][y2]) != 3:
                            continue
                        if len(set([(x, y), (x1, y1), (x2, y2)])) < 3:
                            # make sure cells are unique
                            continue

                        # found 3 unique cells in this unit with 2-3 guesses
                        intersection = board[x][y] + board[x1][y1] + board[x2][y2]
                        if np.sum(intersection >= 1) == 3:
                            found_triple = True
                            break
                    else:
                        # double loop breaking
                        continue
                    break

                if found_triple:
                    removed = False
                    for (searchX, searchY) in unit:
                        if (searchX, searchY) == (x, y) or (searchX, searchY) == (x1, y1) or (searchX, searchY) == (x2, y2):
                            continue
                        for zz in range(9):
                            if intersection[zz] > 0:
                                if board[searchX][searchY][zz] == 1:
                                    removed = True
                                    board[searchX][searchY][zz] = 0
                    if removed:
                        relevant_cells = [(x, y), (x1, y1), (x2, y2)]
                        relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in relevant_cells]
                        return (True, relevant_cells, np.array(relevant_candidates))

    return False, None, None


def naked_quads_scan(board):
    for x in range(9):
        for y in range(9):
            # find 3 cells with a total of 3 numbers
            # every cell has to have at least 2 guesses
            if np.sum(board[x][y]) not in [2, 3, 4]:
                continue
            xy_units = units(x, y)
            for unit in xy_units:
                found_quad = False
                # TODO get all four-groups of cells that fit criterion?
                # rather than nested looping
                for (x1, y1) in unit:
                    if np.sum(board[x1][y1]) not in [2, 3, 4]:
                        continue
                    for (x2, y2) in unit:
                        if np.sum(board[x2][y2]) not in [2, 3, 4]:
                            continue
                        for (x3, y3) in unit:
                            if np.sum(board[x3][y3]) not in [2, 3, 4]:
                                continue
                            if len(set([(x, y), (x1, y1), (x2, y2), (x3, y3)])) < 4:
                                # make sure cells are unique
                                continue
                            # found 4 unique cells in this unit with 2-4 guesses
                            intersection = board[x][y] + board[x1][y1] + board[x2][y2] + board[x3][y3]
                            if np.sum(intersection >= 1) == 4:
                                found_quad = True
                                break
                        else:
                            # double loop breaking
                            continue
                        break
                    else:
                        # double loop breaking
                        continue
                    break

                if found_quad:
                    removed = False
                    for (searchX, searchY) in unit:
                        if (searchX, searchY) == (x, y) or (searchX, searchY) == (x1, y1) or (searchX, searchY) == (x2, y2) or (searchX, searchY) == (x3, y3):
                            continue
                        for zz in range(9):
                            if intersection[zz] > 0:
                                if board[searchX][searchY][zz] == 1:
                                    removed = True
                                    board[searchX][searchY][zz] = 0
                    if removed:
                        relevant_cells = [(x, y), (x1, y1), (x2, y2), (x3, y3)]
                        relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in relevant_cells]
                        return (True, relevant_cells, np.array(relevant_candidates))

    return False, None, None


def hidden_single_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) == 1:
                continue
            xy_units = units(x, y)
            for z in range(9):
                if board[x][y][z] == 0:
                    continue

                for unit in xy_units:
                    hidden_candidate = True
                    for (searchX, searchY) in unit:
                        if (searchX, searchY) == (x, y):
                            continue
                        if board[searchX][searchY][z] == 1:
                            hidden_candidate = False
                            break

                    if hidden_candidate:
                        board[x][y] = np.zeros((9))
                        board[x][y][z] = 1
                        update_guesses(board, x, y)
                        relevant_cells = [(x, y)]
                        relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in relevant_cells]
                        return (True, relevant_cells, np.array(relevant_candidates))

    return False, None, None


def hidden_pairs_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) < 2:
                continue
            # get all pairs of candidates
            # count the number of cells that have these two candidates in similar units
            # if there's only one other, form a hidden pair
            # TODO

    return False, None, None


def hidden_triples_scan(board):

    return False, None, None


def hidden_quads_scan(board):
    return False, None, None


def intersection_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) == 1:
                continue

            xy_units = units(x, y)
            for z in range(9):
                if board[x][y][z] == 0:
                    continue

                # pointing pairs and triples
                for i in range(3):
                    candidate_coords = []
                    for (x1, y1) in xy_units[i]:
                        if np.sum(board[x1][y1]) == 1:
                            continue
                        if board[x1][y1][z] == 1:
                            candidate_coords.append((x1, y1))

                    if len(candidate_coords) <= 3:
                        removed = False
                        if i == 2:
                            # pointing pairs within the same box
                            # check if the candidates line up on a row or column
                            if all(map(lambda coord: coord in xy_units[0], candidate_coords)):
                                # row lineup
                                for (searchX, searchY) in xy_units[0]:
                                    if not (searchX, searchY) in candidate_coords:
                                        if board[searchX][searchY][z] == 1:
                                            board[searchX][searchY][z] = 0
                                            removed = True
                            elif all(map(lambda coord: coord in xy_units[1], candidate_coords)):
                                # col lineup
                                for (searchX, searchY) in xy_units[1]:
                                    if not (searchX, searchY) in candidate_coords:
                                        if board[searchX][searchY][z] == 1:
                                            board[searchX][searchY][z] = 0
                                            removed = True
                        else:
                            # candidates on a row or column
                            # check if they are in the same box
                            if all(map(lambda coord: coord in xy_units[2], candidate_coords)):
                                for (searchX, searchY) in xy_units[2]:
                                    if not (searchX, searchY) in candidate_coords:
                                        if board[searchX][searchY][z] == 1:
                                            board[searchX][searchY][z] = 0
                                            removed = True
                        if removed:
                            # relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in candidate_coords]
                            return (True, candidate_coords, np.array([[z]]))

    return False, None, None


def x_wing_scan(board):
    for x in range(9):
        for y in range(9):
            for z in range(9):
                if np.sum(board[x][y]) == 1:
                    continue
                if board[x][y][z] == 0:
                    continue

                similar_in_unit = [[], []]
                # [0] contains all cells in the same row with candidate z
                # [1] contains all cells in the same col with candidate z
                xy_units = units(x, y)
                for i in [0, 1]:
                    for (x1, y1) in xy_units[i]:
                        if board[x1][y1][z] == 1:
                            similar_in_unit[i].append((x1, y1))

                if len(similar_in_unit[0]) == 2 and len(similar_in_unit[1]) >= 2:
                     # the two coords in [0] (row) are locked in a pair
                    a = 0
                    b = 1
                elif len(similar_in_unit[1]) == 2 and len(similar_in_unit[0]) >= 2:
                    a = 1
                    b = 0
                else:
                    continue
                opposite_coord = similar_in_unit[a][similar_in_unit[a].index((x, y)) - 1][a]

                # time to look at each coordinate to find another locked pair with the same similar axis
                for (x1, y1) in similar_in_unit[b]:
                    if (x1, y1) != (x, y):
                        other_units = units(x1, y1)
                        other_similar = []
                        for (x2, y2) in other_units[a]:  # looking at this other cell's row
                            if board[x2][y2][z] == 1:
                                other_similar.append((x2, y2))
                        if len(other_similar) == 2:
                            # found another locked pair, time to check if x coordinates match up
                            # we know that one x coordinate will, just have to check if the second one does
                            opposite_corner = other_similar[other_similar.index((x1, y1)) - 1]
                            if opposite_corner[a] == opposite_coord:
                                # found an x wing
                                x_wing = [similar_in_unit[a], other_similar]
                                # go through columns and remove
                                # print('!!!')
                                # print(x_wing, z + 1)
                                removed = False
                                unit_a = units(*x_wing[0][0])[b]
                                unit_b = units(*x_wing[0][1])[b]
                                for (searchX, searchY) in unit_a:
                                    if (searchX, searchY) in x_wing[0] or (searchX, searchY) in x_wing[1]:
                                        continue
                                    if board[searchX][searchY][z] == 1:
                                        removed = True
                                        board[searchX][searchY][z] = 0
                                for (searchX, searchY) in unit_b:
                                    if (searchX, searchY) in x_wing[0] or (searchX, searchY) in x_wing[1]:
                                        continue
                                    if board[searchX][searchY][z] == 1:
                                        removed = True
                                        board[searchX][searchY][z] = 0

                                if removed:
                                    relevant_cells = x_wing[0] + x_wing[1]
                                    relevant_candidates = [np.nonzero(board[a][b])[0] for (a, b) in relevant_cells]
                                    return (True, relevant_cells, np.array(relevant_candidates))

    return False, None, None


def y_wing_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) != 2:
                continue
            [az, bz] = list(np.nonzero(board[x][y])[0])

            xy_units = units(x, y)
            # get all pairs of unit cells
            concatenated_units = sorted(list(set(xy_units[0] + xy_units[1] + xy_units[2])))
            concatenated_units.remove((x, y))
            pairs = []
            for (ax, ay) in concatenated_units:
                for (bx, by) in concatenated_units:
                    if (ax, ay) == (bx, by):
                        continue
                    if np.sum(board[ax][ay]) == 2 and np.sum(board[bx][by]) == 2:
                        if board[ax][ay][az] == 1 and board[bx][by][bz] == 1:
                            union = board[ax][ay] + board[bx][by]
                            if np.sum(union > 0) == 3:
                                if np.argmax(union) != az and np.argmax(union) != bz:
                                    # found a valid pair
                                    pairs.append([(ax, ay), (bx, by), np.argmax(union)])
            if len(pairs) > 0:

                removed = False
                for [(ax, ay), (bx, by), cz] in pairs:
                    units_a = set([cell for unit in units(ax, ay) for cell in unit])
                    units_b = set([cell for unit in units(bx, by) for cell in unit])
                    for (cx, cy) in sorted(list(units_a.intersection(units_b))):
                        if (cx, cy) in [(ax, ay), (bx, by), (x, y)]:
                            continue
                        if board[cx][cy][cz] == 1:
                            board[cx][cy][cz] = 0
                            removed = True
                            if removed:
                                relevant_cells = [(x, y), (ax, ay), (bx, by), (cx, cy)]
                                relevant_candidates = [[cz]]
                                return (True, relevant_cells, np.array(relevant_candidates))

    return False, None, None


def xyz_wing_scan(board):
    for x in range(9):
        for y in range(9):
            if np.sum(board[x][y]) != 3:
                continue
            xyz = np.nonzero(board[x][y])[0]
            xy_units = units(x, y)
            # get all pairs of unit cells

    return False, None, None


# method tuple structure is (method, index, difficulty-factor)
# so methods get executed in order of index and increment difficulty based on difficulty factor
deductive_methods = {
    'naked_single': (naked_single_scan, 1, 1),
    'hidden_single': (hidden_single_scan, 2, 2),
    'intersection': (intersection_scan, 4, 2),
    'naked_pairs': (naked_pairs_scan, 5, 3),
    # 'hidden_pairs': (hidden_pairs_scan, 6, 3),
    'naked_triples': (naked_triples_scan, 7, 3),
    # 'hidden_triples': (hidden_triples_scan, 8, 4),
    'naked_quads': (naked_quads_scan, 9, 4),
    # 'hidden_quads': (hidden_quads_scan, 10, 4),
    'x_wing': (x_wing_scan, 11, 5),
    'y_wing': (y_wing_scan, 12, 5),
    'xyz_wing': (xyz_wing_scan, 13, 6),
    # 'swordfish': (swordfish_scan, 14, 6),
    # 'jellyfish': (jellyfish_scan, 15, 7)
}


def move_string(move_type, coords, affected_candidates):
    alphabet = 'ABCDEFGHIJ'
    string = move_type + ' '
    for coord in coords:
        string += '(' + alphabet[coord[0]] + ', ' + str(coord[1] + 1) + '), '
    print_candidates = np.copy(affected_candidates) + 1
    string += str(list(map(lambda x: list(x), print_candidates)))
    return string


def test_all_boards():
    boards = load('tests/test-boards.json')
    for guess_count in sorted(list(boards.keys()), reverse=True):
        if guess_count == '81':
            continue
        print(guess_count)
        for index in range(len(boards[guess_count])):
            code = boards[guess_count][index]
            # print(code)
            board = code_to_board(code)
            guess_board = init_guesses(board)
            modified = True
            i = 0
            while modified:
                i += 1
                modified = False
                for move_type in deductive_methods:
                    result, _, _ = deductive_methods[move_type][0](guess_board)
                    if result:
                        # print(i, move_type)
                        modified = True
                        break
            if not util.board_is_solved(util.remove_guesses(guess_board)):
                print(code)
    exit()


if __name__ == "__main__":
    # test_all_boards()
    moves = []
    # code = load('tests/test-boards.json')['25'][0]
    code = '000000430100830090602000108001008064020070951000900380080010000703485609040003800'
    print(code)
    board = code_to_board(code)
    # print_board(board)
    guess_board = init_guesses(board)
    print_board(guess_board)
    modified = True
    i = 0
    while modified:
        i += 1
        modified = False
        failed = False
        for x in range(9):
            for y in range(9):
                if np.sum(guess_board[x][y]) == 0:
                    print(x, y)
                    failed = True
                    break
        if failed:
            print('error')
            break
        for key in deductive_methods:
            result, coords, candidates = deductive_methods[key][0](guess_board)
            if result:
                print(i, move_string(key, coords, candidates))
                moves.append((key, coords, candidates))
                modified = True
                print_board(guess_board)
                break
    print_board(guess_board)
    for i, move in enumerate(moves):
        print(i + 1, move_string(*move))
    print(util.board_is_solved(util.remove_guesses(guess_board)))
