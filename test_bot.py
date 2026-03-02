from bot import Board, Move, best_move


def test_start_has_20_moves():
    b = Board()
    assert len(b.legal_moves()) == 20


def test_best_move_is_legal():
    b = Board()
    b.set_fen("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/3P4/PPP2PPP/RNBQKBNR w KQkq - 0 1")
    m = best_move(b, 120)
    assert any(m.uci() == lm.uci() for lm in b.legal_moves())


def test_move_applied_from_uci_coords():
    b = Board()
    m = Move(6, 4, 4, 4)
    b.push(m)
    assert b.board[4][4] == "P"
