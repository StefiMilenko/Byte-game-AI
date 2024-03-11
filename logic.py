from state import *
import numpy as np
import functools as ft

w_score = 60.0
w_stacks = 1.0
w_top = 2.0
w_bot = 1.0


def stack_h(stack:list):
    l = len(stack)
    weight = 0.0
    if l == 0:
        return 0
    top, bot = stack[-1], stack[0]
    if top == BytePiece.Black:
        weight += w_top
    else:
        weight -= w_top
    if bot == BytePiece.Black:
        weight += w_bot
    else:
        weight -= w_bot
    return l * weight


def heuristic(state: ByteBoard) -> float:
    #def calculate_stacks():
    #    total = 0
    #    for i in range(_state.width):
    #        for j in range(_state.width):
    #            if (i + j) % 2 == 0 and _state.board[i, j]:
    #                figure_score = w_stacks * len(_state.board[i, j])
    #                if _state.board[i, j][0] == get_top(_state.board[i, j]):
    #                    figure_score *= w_both * convert_piece(get_top(_state.board[i, j]))
    #                else:
    #                    figure_score += (w_stacks * (len(_state.board[i, j]) * convert_piece(_state.board[i, j][0]) +
    #                                     len(_state.board[i, j]) * convert_piece(get_top(_state.board[i, j])) * w_top))
    #                total += figure_score
    #    return total

    stacks_h = ft.reduce(lambda acc, nxt:
                         acc + nxt,
                         list(map(lambda stack: stack_h(stack), state.board.flatten()[::2])), 0) * w_stacks

    score_h = (state.x_score - state.o_score) * w_score

    h = stacks_h + score_h

    return h


def alpha_beta(state: ByteBoard, alpha: float, beta: float, depth: int) -> float:
    if state.x_score > state.max_score/2:
        return np.inf
    elif state.o_score > state.max_score/2:
        return -np.inf
    if depth == 0:
        return heuristic(state)

    valid_states = state.generate_states()
    best_move = valid_states[0]
    if state.x_turn:
        h = -np.inf
        for s in valid_states:
            h = max(h, alpha_beta(s, alpha, beta, depth - 1))
            if h > alpha:
                alpha = h
                best_move = s
            if h > beta:
                break

    else:
        h = np.inf
        for s in valid_states:
            h = min(h, alpha_beta(s, alpha, beta, depth - 1))
            if h < beta:
                beta = h
                best_move = s
            if h < alpha:
                break
    return h


def ai_play(current_state, depth: int = 3) -> float:
    states = current_state.generate_states()
    best_h = None
    if current_state.x_turn:
        best_h = -numpy.Infinity
    else:
        best_h = numpy.Infinity
    best_state = states[0]
    for state in states:
        h = alpha_beta(state, -10000, 10000, depth)
        if (current_state.x_turn and h > best_h) or (not current_state.x_turn and h < best_h):
            best_state = state
            best_h = h
    current_state.board = copy.deepcopy(best_state.board)
    current_state.board_moved = copy.deepcopy(best_state.board_moved)
    current_state.x_turn = best_state.x_turn
    current_state.x_score = best_state.x_score
    current_state.o_score = best_state.o_score
    current_state.player_turn = best_state.player_turn
    current_state.is_over = best_state.is_over
    return best_h