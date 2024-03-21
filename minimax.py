import chess

from math import inf
from typing import Callable, List, Tuple


def minimax(board: chess.Board,
        depth: int,
        alpha: float,
        beta: float,
        maximizingPlayer: bool,
        searchmoves: List[chess.Move],
        eval_function: Callable,
        debug: bool = False,
        is_root: bool = False
       ) -> float|List[Tuple[str, float]]:
    """
    Finds best move for the current player using minimax and alpha-beta pruning.
    
    :param board: current board position
    :param depth: depth to go
    :param alpha: alpha value
    :param beta: beta value
    :param maximizingPlayer: True if current player is maximizing, False otherwise
    :param eval_function: the function used to evaluate board position
    :param debug: If True, prints debug information about every move checked
    :param is_root: True signifies that this is the root node
    
    :returns: Either evaluation, or moves ordered from worst to best, in the case of root node
    """
    if depth == 0 or board.is_checkmate() or board.is_stalemate() or board.is_insufficient_material():
        return eval_function(board)
        
    if maximizingPlayer:
        value = -inf
        if is_root:
            moves: List[Tuple[str, float]] = []
        try:
            for move in searchmoves or sorted(board.legal_moves, key=lambda move: eval_function(board, move), reverse=True):

                if debug:
                    print(f"Checking {move}...")
                    print(f"Current board position: {board.fen()}")
                    print(f"Other params: alpha={alpha}, beta={beta}, depth={depth}, maximizingPlayer={maximizingPlayer}, searchmoves={searchmoves}, eval_function={eval_function}, debug={debug}, is_root={is_root}")
                    
                board.push(move)
                if is_root:
                    print("info root currmove", move)
                    moves.append((move.uci(), minimax(board, depth - 1, alpha, beta, False, [], eval_function, debug)))
                    alpha = max(alpha, moves[-1][1])
                else:
                    value = max(value,
                                minimax(board, depth - 1, alpha, beta, False, [], eval_function, debug)
                               )
                    alpha = max(alpha, value)
                board.pop()
                
                if beta <= alpha:
                    break
                    
            if is_root:
                if debug: print(f"returning sorted({moves})")
                return sorted(moves, key=lambda x: x[1] or -inf, reverse=True)# + [(str(x), -inf) for x in board.legal_moves if x not in  [move[0] for move in moves]]
    
            return value
        except Exception as e:
            print(f"board {board.fen}, move {move}")
            print(e)
        
    else:
        value = inf
        if is_root:
            moves: List[Tuple[str, float]] = []
        try:
            for move in searchmoves or sorted(board.legal_moves, key=lambda move: eval_function(board, move)):
                
                if debug:
                    print(f"Checking {move}...")
                    print(f"Current board position: {board.fen()}")
                    print(f"Other params: alpha={alpha}, beta={beta}, depth={depth}, maximizingPlayer={maximizingPlayer}, searchmoves={searchmoves}, eval_function={eval_function}, debug={debug}, is_root={is_root}")
                
                board.push(move)
                if is_root:
                    print("info root currmove", move)
                    moves.append((move.uci(), minimax(board, depth - 1, alpha, beta, True, [], eval_function, debug)))
                    beta = min(beta, moves[-1][1])
                else:
                    value = min(value,
                            minimax(board, depth - 1, alpha, beta, True, [], eval_function, debug)
                            )
                    beta = min(beta, value)
                board.pop()
                
                if beta <= alpha:
                    break
    
            if is_root:
                if debug: print(f"returning sorted({moves})")
                return sorted(moves, key=lambda x: x[1]) #+ [(str(x), inf) for x in board.legal_moves if x not in  [move[0] for move in moves]]
                
            return value
        except Exception as e:
            print(f"board {board.fen}, move {move}")
            print(e)