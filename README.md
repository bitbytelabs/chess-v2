# BetterThanStockfish (experimental)

A self-contained Python UCI chess bot with no third-party dependencies.

## What this bot does
- Implements the **UCI protocol** (`uci`, `isready`, `position`, `go`, `quit`) so chess GUIs can communicate with it.
- Generates legal chess moves, including castling, en passant, and queen promotion.
- Chooses a move with iterative deepening + alpha-beta search and a simple material evaluation.

## What this bot does *not* do
- It is **not** stronger than Stockfish.
- It is a lightweight educational engine, useful as a baseline and for testing integrations.

## Run
```bash
python bot.py
```

## Quick UCI demo
```bash
python bot.py
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
