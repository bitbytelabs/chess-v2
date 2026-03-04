from __future__ import annotations

from pathlib import Path
from typing import Iterable

import chess.pgn


def parse_pgn_moves(path: str | Path) -> Iterable[list[str]]:
    pgn_path = Path(path)
    with pgn_path.open("r", encoding="utf-8") as handle:
        while True:
            game = chess.pgn.read_game(handle)
            if game is None:
                break
            moves = [move.uci() for move in game.mainline_moves()]
            if moves:
                yield moves
