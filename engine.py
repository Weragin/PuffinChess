#!../venv/bin/python
"""
This is the enigine. It prints "bestmove {the best move in long format}". 
"""

import chess
import signal
import sys

from psqt import evaluate
from minimax import minimax

from math import inf
from time import time
from typing import Callable, Dict, Literal, Protocol, List

# Michael: I'd love to implement logging with this later:
# from icecream import ic


def exit(signum, frame):
    """Engine termination handler"""
    global bestmove, score, fen
    if bestmove == "0000":
        board = chess.Board(fen)
        bestmove = sorted(board.legal_moves, key=lambda move: evaluate(board, move))[0]
        score = evaluate(board, bestmove)
    print("info score", score)
    print("bestmove", bestmove)
    sys.exit(0)

signal.signal(signal.SIGTERM, exit)
signal.signal(signal.SIGINT, exit)


def go(board: chess.Board,
       mode: Literal["d", "t"],
       mode_param: int,
       searchmoves: List[chess.Move],
       eval_function: Callable,
       debug: bool
      ):
    """
    Initializes minimax search with given mode and mode parameter.

    :param board: current board position
    :param mode: the search mode - "t" for time, "d" for depth
    :param mode_param: the search mode parameter - ms for time, depth for depth
    :param searchmoves: list of moves to search left empty if we want to analyse all moves
    :param debug: If True, minimax will run in debug mode, logging debug information about every move checked
    :param eval_function: the function used to evaluate board position
    """
    global bestmove, score
    maximizingPlayer = board.turn == chess.WHITE
    if mode == "d":
        bestmove, score = minimax(board, mode_param, -inf, inf, maximizingPlayer, searchmoves, eval_function, debug, True)[0]
        print("score", score)
        print("bestmove", bestmove)
        return chess.Move.from_uci(bestmove)
        
    if mode == "t":
        start = time() * 1000
        depth = 1

        while time() * 1000 - start < mode_param:
            print("info depth", depth)
            moves_from_search = minimax(board, depth, -inf, inf, maximizingPlayer, searchmoves, eval_function, debug, True)
            searchmoves = [chess.Move.from_uci(x[0]) for x in moves_from_search]
            bestmove, score = moves_from_search[0]
            print("info bestmove", bestmove, "score", score)
            depth += 1
        print("info score", score)
        print("bestmove", bestmove)
        return chess.Move.from_uci(str(bestmove))

if __name__ == "__main__":
    fen = sys.argv[1]
    board = chess.Board(fen)
    mode = sys.argv[2]
    mode_param = int(sys.argv[3])
    debug = sys.argv[4] == "on"
    if len(sys.argv) > 5:
        searchmoves = [chess.Move.from_uci(move) for move in sys.argv[5:]]
    else:
        searchmoves = []
    
    bestmove = "0000"
    score = 0
    
    go(board, mode, mode_param, searchmoves, evaluate, debug)
    
    """
    fen = chess.STARTING_FEN
    go(chess.Board(fen), mode="t", mode_param=999999999, searchmoves=[], eval_function=evaluate, debug=False)
    """
