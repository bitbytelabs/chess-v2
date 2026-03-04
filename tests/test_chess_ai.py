from pathlib import Path

import chess

from chess_ai.engine import ChessAI
from chess_ai.llm import TinyMoveLLM


def test_llm_training_prefers_seen_transition() -> None:
    model = TinyMoveLLM()
    model.train([
        ["e2e4", "e7e5", "g1f3"],
        ["e2e4", "c7c5", "g1f3"],
        ["d2d4", "d7d5", "c2c4"],
    ])

    best = model.best_move(["e2e4"], ["e7e5", "c7c5", "e7e6"])
    assert best in {"e7e5", "c7c5"}


def test_llm_save_and_load_roundtrip(tmp_path: Path) -> None:
    model = TinyMoveLLM()
    model.train([["e2e4", "e7e5"]])

    out = tmp_path / "model.json"
    model.save(out)

    loaded = TinyMoveLLM.load(out)
    assert loaded.score(["e2e4"], "e7e5") > 0


def test_ai_chooses_legal_move() -> None:
    board = chess.Board()
    ai = ChessAI(depth=1)

    move = ai.choose_move(board, history=[])
    assert move in board.legal_moves
