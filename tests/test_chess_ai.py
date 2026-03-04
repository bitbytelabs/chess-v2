from pathlib import Path

import chess
import pytest

from chess_ai.cli import train_model
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


def test_train_model_works_with_sample_data(tmp_path: Path) -> None:
    model_path = tmp_path / "model.json"
    train_model("data/games.pgn", str(model_path))

    loaded = TinyMoveLLM.load(model_path)
    assert loaded.score(["e2e4"], "e7e5") > 0


def test_train_model_fails_with_clear_message_for_missing_pgn(tmp_path: Path) -> None:
    model_path = tmp_path / "model.json"

    with pytest.raises(SystemExit, match="PGN file not found"):
        train_model("data/does-not-exist.pgn", str(model_path))
