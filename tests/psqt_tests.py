import chess
from psqt import evaluate


for i in ["rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
     "rnbqkb1r/ppp2Qpp/3p1n2/4p3/2B1P3/8/PPPP1PPP/RNB1K1NR b KQkq - 0 1",
     "rnbqkb1r/ppp2ppp/3p1n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 0 1",
     "r1bqkb1r/1ppp1ppp/p1n2n2/4p3/B3P3/5N2/PPPP1PPP/RNBQ1RK1 w kq - 0 1",
     "r2q1rk1/pppb1ppp/2nbpn2/3p4/2PP4/2NBPNB1/PP3PPP/R2Q1RK1 w - - 0 1",
     "1R2b2k/8/6Q1/p2p4/P2K4/8/8/8 b - - 0 1"
     ]:
    print(evaluate(chess.Board(i)))
