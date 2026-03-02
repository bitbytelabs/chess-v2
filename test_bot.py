import json
import subprocess
import sys

from bot import Board, Move, best_move, load_weights, save_weights, train


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


def test_uci_handshake_and_bestmove_output():
    proc = subprocess.run(
        [sys.executable, "bot.py", "uci"],
        input="uci\nisready\nposition startpos\ngo movetime 50\nquit\n",
        text=True,
        capture_output=True,
        check=True,
    )
    out = proc.stdout
    assert "uciok" in out
    assert "readyok" in out
    assert "bestmove " in out


def test_train_command_creates_weights_file(tmp_path):
    out_file = tmp_path / "weights.json"
    proc = subprocess.run(
        [
            sys.executable,
            "bot.py",
            "train",
            "--weights",
            str(out_file),
            "--games",
            "2",
            "--max-plies",
            "6",
            "--movetime",
            "5",
        ],
        text=True,
        capture_output=True,
        check=True,
    )
    assert "trained weights saved" in proc.stdout
    assert out_file.exists()
    loaded = json.loads(out_file.read_text())
    for piece in ["p", "n", "b", "r", "q", "k"]:
        assert piece in loaded


def test_save_and_load_weights_round_trip(tmp_path):
    path = tmp_path / "vals.json"
    weights = {"p": 101, "n": 322, "b": 333, "r": 505, "q": 911, "k": 0}
    save_weights(str(path), weights)
    loaded = load_weights(str(path))
    assert loaded == weights


def test_train_returns_king_zero():
    tuned = train(load_weights(None), games=1, max_plies=4, movetime_ms=2, mutation=5)
    assert tuned["k"] == 0
