"""
Unit tests for the engine.py module.
Includes tests for the go() function from a fen and
a function for generating self-played games from a given opening.
The latter one can be used to test the engine's behaviour during the whole game easily.
It also generates PGN of the game.
"""

import chess
import chess.pgn
import time

from math import inf
from typing import Callable, Literal, Optional


import sys
import os

# Code to be able to import from parent dir
# credited:
# https://www.geeksforgeeks.org/python-import-from-parent-directory/
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from engine import go
from psqt import evaluate


# Michael: I'd love to implement logging with this later:
from icecream import ic

def unit_tests():
    for fen in [chess.STARTING_FEN,
               ]:
        go(chess.Board(fen), mode="t", mode_param=60000, searchmoves=[], eval_function=evaluate, debug=False)


def self_play(mode: Literal["d", "t"], 
              mode_param: int,
              fen: str=chess.STARTING_FEN, 
              eval_function: Callable[[chess.Board, Optional[chess.Move]], float]=evaluate, 
              debug=False
             ) -> chess.pgn.Game:
    """Functionality is clear from the code - create pgn"""
    board = chess.Board(fen)
    
    game = chess.pgn.Game()
    game.setup(board)
    game.headers["Event"] = "Self-play"
    game.headers["Date"] = "2024-02-14"
    game.headers["White"] = "PuffinChess"
    game.headers["White-Elo"] = "Unknown"
    game.headers["Black"] = "PuffinChess"
    game.headers["Black-Elo"] = "Unknown"
    
    node = None
    movetime = []

    while not board.is_game_over():
        try:
            start_local = time.time()
            if node is None:
                node = game.add_variation(go(board, mode, mode_param, [], eval_function, debug))
            else:
                node = node.add_variation(go(board, mode, mode_param, [], eval_function, debug))
            board.push(node.move)
            movetime.append(time.time() - start_local)
            print("Time taken:", time.time() - start_local)
            
        except Exception as e:
            ic(e)
            break
            
    with open("times.txt", mode="a") as times:
        times.write(f"{sum(movetime)/len(movetime)}\n")
        
    game.headers["Result"] = board.result()
    
    return game

board = chess.Board()
board.push(chess.Move.from_uci("e2e4"))
fen = board.fen()
with open("game_pgns/self_play_startpos_depth5_e4.pgn", "w") as file:
    file.write(str(self_play("d", 5, fen=fen)))

board.pop()
board.push(chess.Move.from_uci("d2d4"))
fen = board.fen()
with open("game_pgns/self_play_startpos_depth5_d4.pgn", "w") as file:
    file.write(str(self_play("d", 5, fen=fen)))
    
