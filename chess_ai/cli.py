from __future__ import annotations

import argparse

import chess

from .engine import ChessAI
from .llm import TinyMoveLLM
from .training import parse_pgn_moves


def train_model(pgn_path: str, output_path: str) -> None:
    model = TinyMoveLLM()
    model.train(parse_pgn_moves(pgn_path))
    model.save(output_path)
    print(f"Saved model to {output_path}")


def play_from_fen(model_path: str, fen: str, depth: int) -> None:
    model = TinyMoveLLM.load(model_path)
    ai = ChessAI(depth=depth, llm=model)
    board = chess.Board(fen)
    move = ai.choose_move(board)
    print(move.uci())


def main() -> None:
    parser = argparse.ArgumentParser(description="Trainable chess AI with a local tiny LLM")
    sub = parser.add_subparsers(dest="command", required=True)

    train_parser = sub.add_parser("train", help="Train move model from PGN")
    train_parser.add_argument("--pgn", required=True)
    train_parser.add_argument("--output", required=True)

    play_parser = sub.add_parser("play", help="Choose a move from a FEN")
    play_parser.add_argument("--model", required=True)
    play_parser.add_argument("--fen", default=chess.STARTING_FEN)
    play_parser.add_argument("--depth", type=int, default=2)

    args = parser.parse_args()

    if args.command == "train":
        train_model(args.pgn, args.output)
    elif args.command == "play":
        play_from_fen(args.model, args.fen, args.depth)


if __name__ == "__main__":
    main()
