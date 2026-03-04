from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import chess

from .llm import TinyMoveLLM


PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


@dataclass
class ChessAI:
    depth: int = 2
    llm_weight: float = 150.0
    llm: TinyMoveLLM = field(default_factory=TinyMoveLLM)

    def choose_move(self, board: chess.Board, history: Sequence[str] | None = None) -> chess.Move:
        history = history or []
        best_score = float("-inf")
        best_move = None

        for move in board.legal_moves:
            board.push(move)
            score = -self._negamax(board, self.depth - 1, float("-inf"), float("inf"))
            board.pop()

            llm_bonus = self.llm.score(history, move.uci()) * self.llm_weight
            score += llm_bonus

            if score > best_score:
                best_score = score
                best_move = move

        if best_move is None:
            raise ValueError("No legal move available")
        return best_move

    def _evaluate(self, board: chess.Board) -> float:
        if board.is_checkmate():
            return -100000 if board.turn else 100000
        if board.is_stalemate() or board.is_insufficient_material():
            return 0

        score = 0
        for piece_type, value in PIECE_VALUES.items():
            score += len(board.pieces(piece_type, chess.WHITE)) * value
            score -= len(board.pieces(piece_type, chess.BLACK)) * value

        return score if board.turn == chess.WHITE else -score

    def _negamax(self, board: chess.Board, depth: int, alpha: float, beta: float) -> float:
        if depth == 0 or board.is_game_over():
            return self._evaluate(board)

        best = float("-inf")
        for move in board.legal_moves:
            board.push(move)
            score = -self._negamax(board, depth - 1, -beta, -alpha)
            board.pop()

            best = max(best, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break

        return best
