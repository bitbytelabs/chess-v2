# BetterThanStockfish (experimental)

A self-contained Python UCI chess bot with no third-party dependencies.

## What this bot does
- Implements the **UCI protocol** (`uci`, `isready`, `position`, `go`, `quit`) so chess GUIs can communicate with it.
- Generates legal chess moves, including castling, en passant, and queen promotion.
- Chooses a move with iterative deepening + alpha-beta search and a simple material evaluation.
- Supports a lightweight **training mode** that tunes piece weights with self-play and saves them to JSON.

## What this bot does *not* do
- It is **not** stronger than Stockfish.
- It is a lightweight educational engine, useful as a baseline and for testing integrations.

## Is it AI?
Yes—this bot is a basic **game-playing AI**. It uses search (iterative deepening + alpha-beta pruning)
and an evaluation function to pick moves. It is not machine-learning based, and it is far weaker than
modern engines like Stockfish.

## Run (UCI mode)
```bash
python bot.py uci
```

You can still run `python bot.py` and it will default to UCI mode.

## Train
```bash
python bot.py train --weights weights.json --games 40 --max-plies 40 --movetime 15
```

Then run with trained weights:
```bash
python bot.py uci --weights weights.json
```

## Quick UCI demo
```bash
python bot.py uci
# then type:
uci
isready
position startpos
go movetime 200
quit
```

## Test
```bash
python -m pytest -q
```
