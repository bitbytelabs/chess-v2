# Chess AI with a Trainable Local "LLM"

This project provides a chess AI that combines:

1. A minimax/negamax chess search engine.
2. A trainable local move-language model (`TinyMoveLLM`) that learns move patterns from PGN games.

## Why "its own LLM"

`TinyMoveLLM` is a lightweight local language model over move tokens (UCI strings). It is fully owned by this repo, trainable on your data, and persisted as JSON.

## Install

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\\Scripts\\Activate.ps1

# Windows (Command Prompt)
.venv\\Scripts\\activate.bat

pip install -e .
```

After installation, you can run the CLI either as a Python module or through
the cross-platform `chess-ai` console command.

## Train

```bash
python -m chess_ai.cli train --pgn data/games.pgn --output model.json
# or
chess-ai train --pgn data/games.pgn --output model.json
```

## Play one move from a FEN

```bash
python -m chess_ai.cli play --model model.json --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" --depth 2
# or
chess-ai play --model model.json --fen "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1" --depth 2
```

## Run tests

```bash
python -m pytest
```
