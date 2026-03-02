#!/usr/bin/env python3
from __future__ import annotations

import random
import sys
import time
from dataclasses import dataclass
from typing import List, Optional, Tuple

FILES = "abcdefgh"
RANKS = "12345678"
PIECE_VAL = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 0}


def in_bounds(r: int, c: int) -> bool:
    return 0 <= r < 8 and 0 <= c < 8


def square_to_idx(s: str) -> Tuple[int, int]:
    return 8 - int(s[1]), FILES.index(s[0])


def idx_to_square(r: int, c: int) -> str:
    return f"{FILES[c]}{8-r}"


@dataclass
class Move:
    fr: int
    fc: int
    tr: int
    tc: int
    promo: Optional[str] = None

    def uci(self) -> str:
        u = idx_to_square(self.fr, self.fc) + idx_to_square(self.tr, self.tc)
        return u + self.promo if self.promo else u


class Board:
    def __init__(self) -> None:
        self.set_fen("startpos")

    def clone(self) -> "Board":
        b = Board()
        b.board = [row[:] for row in self.board]
        b.turn = self.turn
        b.castling = self.castling
        b.ep = self.ep
        return b

    def set_fen(self, fen: str) -> None:
        if fen == "startpos":
            fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        parts = fen.split()
        rows = parts[0].split("/")
        self.board = []
        for row in rows:
            out = []
            for ch in row:
                if ch.isdigit():
                    out.extend("." * int(ch))
                else:
                    out.append(ch)
            self.board.append(out)
        self.turn = parts[1]
        self.castling = parts[2]
        self.ep = None if parts[3] == "-" else square_to_idx(parts[3])

    def piece(self, r: int, c: int) -> str:
        return self.board[r][c]

    def color(self, p: str) -> Optional[str]:
        if p == ".":
            return None
        return "w" if p.isupper() else "b"

    def attacked_by(self, side: str, r: int, c: int) -> bool:
        # pawns
        dr = -1 if side == "w" else 1
        for dc in (-1, 1):
            rr, cc = r - dr, c - dc
            if in_bounds(rr, cc):
                p = self.piece(rr, cc)
                if p.lower() == "p" and self.color(p) == side:
                    return True
        # knights
        for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
            rr, cc = r+dr, c+dc
            if in_bounds(rr, cc):
                p = self.piece(rr, cc)
                if p.lower() == "n" and self.color(p) == side:
                    return True
        # king
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr == dc == 0:
                    continue
                rr, cc = r+dr, c+dc
                if in_bounds(rr, cc):
                    p = self.piece(rr, cc)
                    if p.lower() == "k" and self.color(p) == side:
                        return True
        # sliders
        for dirs, kinds in [([(-1,0),(1,0),(0,-1),(0,1)], {"r","q"}), ([(-1,-1),(-1,1),(1,-1),(1,1)], {"b","q"})]:
            for dr, dc in dirs:
                rr, cc = r+dr, c+dc
                while in_bounds(rr, cc):
                    p = self.piece(rr, cc)
                    if p != ".":
                        if self.color(p) == side and p.lower() in kinds:
                            return True
                        break
                    rr += dr
                    cc += dc
        return False

    def king_pos(self, side: str) -> Tuple[int, int]:
        k = "K" if side == "w" else "k"
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == k:
                    return r, c
        return -1, -1

    def in_check(self, side: str) -> bool:
        r, c = self.king_pos(side)
        return self.attacked_by("b" if side == "w" else "w", r, c)

    def push(self, m: Move) -> Tuple[str, Optional[Tuple[int,int]], str]:
        p = self.board[m.fr][m.fc]
        captured = self.board[m.tr][m.tc]
        old_ep = self.ep
        old_castling = self.castling
        self.ep = None
        # en passant capture
        if p.lower() == "p" and old_ep and (m.tr, m.tc) == old_ep and captured == ".":
            cap_r = m.tr + (1 if p.isupper() else -1)
            captured = self.board[cap_r][m.tc]
            self.board[cap_r][m.tc] = "."
        self.board[m.fr][m.fc] = "."
        if m.promo:
            self.board[m.tr][m.tc] = m.promo.upper() if p.isupper() else m.promo
        else:
            self.board[m.tr][m.tc] = p
        # castling move rook
        if p.lower() == "k" and abs(m.tc - m.fc) == 2:
            if m.tc == 6:
                self.board[m.tr][5] = self.board[m.tr][7]
                self.board[m.tr][7] = "."
            else:
                self.board[m.tr][3] = self.board[m.tr][0]
                self.board[m.tr][0] = "."
        # set en passant square
        if p.lower() == "p" and abs(m.tr - m.fr) == 2:
            self.ep = ((m.fr + m.tr)//2, m.fc)
        # castling rights update
        rights = set(self.castling)
        if p == "K": rights -= {"K","Q"}
        if p == "k": rights -= {"k","q"}
        if (m.fr,m.fc) == (7,0) or (m.tr,m.tc) == (7,0): rights.discard("Q")
        if (m.fr,m.fc) == (7,7) or (m.tr,m.tc) == (7,7): rights.discard("K")
        if (m.fr,m.fc) == (0,0) or (m.tr,m.tc) == (0,0): rights.discard("q")
        if (m.fr,m.fc) == (0,7) or (m.tr,m.tc) == (0,7): rights.discard("k")
        self.castling = "".join(ch for ch in "KQkq" if ch in rights) or "-"
        self.turn = "b" if self.turn == "w" else "w"
        return captured, old_ep, old_castling

    def pop(self, m: Move, state: Tuple[str, Optional[Tuple[int,int]], str]) -> None:
        captured, old_ep, old_castling = state
        self.turn = "b" if self.turn == "w" else "w"
        p = self.board[m.tr][m.tc]
        # undo castle rook
        if p.lower() == "k" and abs(m.tc - m.fc) == 2:
            if m.tc == 6:
                self.board[m.tr][7] = self.board[m.tr][5]
                self.board[m.tr][5] = "."
            else:
                self.board[m.tr][0] = self.board[m.tr][3]
                self.board[m.tr][3] = "."
        self.board[m.fr][m.fc] = ("P" if self.turn == "w" else "p") if m.promo else p
        self.board[m.tr][m.tc] = captured
        # restore en passant capture
        if self.board[m.fr][m.fc].lower() == "p" and old_ep and (m.tr,m.tc) == old_ep and captured.lower() == "p" and m.fc != m.tc:
            self.board[m.tr][m.tc] = "."
            cap_r = m.tr + (1 if self.turn == "w" else -1)
            self.board[cap_r][m.tc] = captured
        self.ep = old_ep
        self.castling = old_castling

    def legal_moves(self) -> List[Move]:
        side = self.turn
        out: List[Move] = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p == "." or self.color(p) != side:
                    continue
                out.extend(self._piece_moves(r, c, p))
        legal = []
        for m in out:
            st = self.push(m)
            if not self.in_check("b" if self.turn == "w" else "w"):
                legal.append(m)
            self.pop(m, st)
        return legal

    def _piece_moves(self, r: int, c: int, p: str) -> List[Move]:
        side = self.color(p)
        opp = "b" if side == "w" else "w"
        res = []
        t = p.lower()
        if t == "p":
            d = -1 if side == "w" else 1
            start = 6 if side == "w" else 1
            promote_row = 0 if side == "w" else 7
            if in_bounds(r+d, c) and self.piece(r+d, c) == ".":
                if r+d == promote_row:
                    res.append(Move(r,c,r+d,c,"q"))
                else:
                    res.append(Move(r,c,r+d,c))
                if r == start and self.piece(r+2*d, c) == ".":
                    res.append(Move(r,c,r+2*d,c))
            for dc in (-1,1):
                rr, cc = r+d, c+dc
                if in_bounds(rr, cc):
                    target = self.piece(rr, cc)
                    if target != "." and self.color(target) == opp:
                        res.append(Move(r,c,rr,cc,"q" if rr == promote_row else None))
                    if self.ep == (rr, cc):
                        res.append(Move(r,c,rr,cc))
        elif t == "n":
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                rr, cc = r+dr, c+dc
                if in_bounds(rr, cc) and self.color(self.piece(rr, cc)) != side:
                    res.append(Move(r,c,rr,cc))
        elif t in ("b", "r", "q"):
            dirs = []
            if t in ("b", "q"): dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
            if t in ("r", "q"): dirs += [(-1,0),(1,0),(0,-1),(0,1)]
            for dr, dc in dirs:
                rr, cc = r+dr, c+dc
                while in_bounds(rr, cc):
                    if self.piece(rr, cc) == ".":
                        res.append(Move(r,c,rr,cc))
                    else:
                        if self.color(self.piece(rr,cc)) != side:
                            res.append(Move(r,c,rr,cc))
                        break
                    rr += dr
                    cc += dc
        elif t == "k":
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr == dc == 0: continue
                    rr, cc = r+dr, c+dc
                    if in_bounds(rr, cc) and self.color(self.piece(rr, cc)) != side:
                        res.append(Move(r,c,rr,cc))
            # castling
            if side == "w" and r == 7 and c == 4 and not self.in_check("w"):
                if "K" in self.castling and self.piece(7,5)==self.piece(7,6)=="." and not self.attacked_by("b",7,5) and not self.attacked_by("b",7,6):
                    res.append(Move(7,4,7,6))
                if "Q" in self.castling and self.piece(7,1)==self.piece(7,2)==self.piece(7,3)=="." and not self.attacked_by("b",7,3) and not self.attacked_by("b",7,2):
                    res.append(Move(7,4,7,2))
            if side == "b" and r == 0 and c == 4 and not self.in_check("b"):
                if "k" in self.castling and self.piece(0,5)==self.piece(0,6)=="." and not self.attacked_by("w",0,5) and not self.attacked_by("w",0,6):
                    res.append(Move(0,4,0,6))
                if "q" in self.castling and self.piece(0,1)==self.piece(0,2)==self.piece(0,3)=="." and not self.attacked_by("w",0,3) and not self.attacked_by("w",0,2):
                    res.append(Move(0,4,0,2))
        return res


def evaluate(board: Board) -> int:
    score = 0
    for r in range(8):
        for c in range(8):
            p = board.board[r][c]
            if p == ".":
                continue
            v = PIECE_VAL[p.lower()]
            score += v if p.isupper() else -v
    return score if board.turn == "w" else -score


def search(board: Board, depth: int, alpha: int, beta: int) -> int:
    moves = board.legal_moves()
    if depth == 0 or not moves:
        if not moves and board.in_check(board.turn):
            return -99999 + (3-depth)
        return evaluate(board)
    best = -10**9
    for m in moves:
        st = board.push(m)
        sc = -search(board, depth-1, -beta, -alpha)
        board.pop(m, st)
        if sc > best:
            best = sc
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def best_move(board: Board, movetime_ms: int) -> Move:
    start = time.time()
    legal = board.legal_moves()
    if not legal:
        raise RuntimeError("No legal moves")
    random.shuffle(legal)
    chosen = legal[0]
    depth = 1
    while time.time() - start < movetime_ms / 1000 and depth <= 4:
        local_best = None
        local_score = -10**9
        for m in legal:
            st = board.push(m)
            sc = -search(board, depth-1, -10**9, 10**9)
            board.pop(m, st)
            if sc > local_score:
                local_score = sc
                local_best = m
        if local_best:
            chosen = local_best
        depth += 1
    return chosen


def main() -> None:
    b = Board()
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        cmd = line.strip().split()
        if not cmd:
            continue
        if cmd[0] == "uci":
            print("id name BetterThanStockfish")
            print("id author Codex")
            print("uciok", flush=True)
        elif cmd[0] == "isready":
            print("readyok", flush=True)
        elif cmd[0] == "ucinewgame":
            b = Board()
        elif cmd[0] == "position":
            if cmd[1] == "startpos":
                b.set_fen("startpos")
                i = 2
            else:
                i = cmd.index("fen") + 1
                j = cmd.index("moves") if "moves" in cmd else len(cmd)
                b.set_fen(" ".join(cmd[i:j]))
                i = j
            if i < len(cmd) and cmd[i] == "moves":
                for u in cmd[i+1:]:
                    fr, fc = square_to_idx(u[:2])
                    tr, tc = square_to_idx(u[2:4])
                    promo = u[4] if len(u) == 5 else None
                    m = Move(fr, fc, tr, tc, promo)
                    b.push(m)
        elif cmd[0] == "go":
            movetime = 300
            if "movetime" in cmd:
                movetime = int(cmd[cmd.index("movetime")+1])
            m = best_move(b, movetime)
            print(f"bestmove {m.uci()}", flush=True)
        elif cmd[0] == "quit":
            break


if __name__ == "__main__":
    main()
