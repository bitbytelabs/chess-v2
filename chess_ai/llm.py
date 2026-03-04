from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json
from pathlib import Path
from typing import Iterable, Sequence


START_TOKEN = "<START>"


@dataclass
class TinyMoveLLM:
    """A tiny local move language model based on bigram counts.

    This model learns transition probabilities between UCI chess moves.
    It is trainable from PGN game move lists and can score/predict the
    next move among legal candidates.
    """

    transitions: dict[str, Counter[str]] = field(default_factory=lambda: defaultdict(Counter))

    def train(self, games: Iterable[Sequence[str]]) -> None:
        for moves in games:
            prev = START_TOKEN
            for move in moves:
                self.transitions[prev][move] += 1
                prev = move

    def score(self, history: Sequence[str], candidate_move: str) -> float:
        prev = history[-1] if history else START_TOKEN
        counts = self.transitions.get(prev)
        if not counts:
            return 0.0
        total = sum(counts.values())
        if total == 0:
            return 0.0
        return counts.get(candidate_move, 0) / total

    def best_move(self, history: Sequence[str], legal_moves: Sequence[str]) -> str | None:
        if not legal_moves:
            return None
        scored = [(self.score(history, mv), mv) for mv in legal_moves]
        scored.sort(key=lambda item: item[0], reverse=True)
        return scored[0][1]

    def save(self, path: str | Path) -> None:
        serialized = {k: dict(v) for k, v in self.transitions.items()}
        Path(path).write_text(json.dumps(serialized, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "TinyMoveLLM":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        model = cls()
        model.transitions = defaultdict(Counter, {k: Counter(v) for k, v in raw.items()})
        return model
