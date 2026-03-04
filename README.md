# Chess AI with a Trainable Local "LLM"

This project provides a chess AI that combines:

1. A minimax/negamax chess search engine.
2. A trainable local move-language model (`TinyMoveLLM`) that learns move patterns from PGN games.

## Why "its own LLM"

`TinyMoveLLM` is a lightweight local language model over move tokens (UCI strings). It is fully owned by this repo, trainable on your data, and persisted as JSON.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Train

```bash
python -m chess_ai.cli train --pgn data/games.pgn --output model.json
```

## Play one move from a FEN

```bash
python -m chess_ai.cli play --model model.json --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" --depth 2
```

## Run tests

```bash
python -m pytest
```
