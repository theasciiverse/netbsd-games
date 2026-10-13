"""canfield preview: a game of Canfield played from the board on screen.

The driver reads the board at canfield's own positions (canfield.c: the
title at row 0, column 30; foundations on row 3; stock at row 8 and talon
at row 13, column 2; the four tableau piles from row 8 down in columns
11, 18, 25 and 32), placed by the title, wherever centring put it. It
makes only legal moves, in this order: any card to a foundation, the
stock onto the tableau, the talon onto the tableau, a whole pile onto
another when that empties a pile, and otherwise deals the hand to the
talon. After about 40 seconds it gives up the game, declines another and
the program ends.

    python3 asciiverse/record/canfield.py
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

TITLE = "=-> CANFIELD <-="
RANKS = {"A": 1, "J": 11, "Q": 12, "K": 13}
PILES = (11, 18, 25, 32)


def origin(r):
    for y, line in enumerate(r.rows()):
        x = line.find(TITLE)
        if x >= 0:
            return y, x - 30
    return None


def card(r, oy, ox, row, col):
    """The card canfield prints at (row, col), as (rank, suit), or None."""
    text = r.rows()[oy + row][ox + col:ox + col + 3].strip()
    if len(text) < 2 or text[-1] not in "shdc":
        return None
    rank = text[:-1]
    rank = RANKS.get(rank, int(rank) if rank.isdigit() else 0)
    return (rank, text[-1]) if rank else None


def red(c):
    return c[1] in "hd"


def above(c, under):
    """True when c may go on under: one rank lower, the other colour."""
    lower = c[0] + 1 == under[0] or (c[0] == 13 and under[0] == 1)
    return lower and red(c) != red(under)


def onto_found(c, found):
    return any(f and f[1] == c[1] and (c[0] == f[0] + 1 or (f[0] == 13 and c[0] == 1)) for f in found)


def board(r):
    oy, ox = origin(r)
    found = [card(r, oy, ox, 3, col) for col in PILES]
    stock = card(r, oy, ox, 8, 2)
    talon = card(r, oy, ox, 13, 2)
    tab = []
    for col in PILES:
        pile, row = [], 8
        while True:
            c = card(r, oy, ox, row, col)
            if c is None:
                break
            pile.append(c)
            row += 1
        tab.append(pile)
    return found, stock, talon, tab


def choose(found, stock, talon, tab):
    if talon and onto_found(talon, found):
        return "tf"
    if stock and onto_found(stock, found):
        return "sf"
    for i, pile in enumerate(tab):
        if pile and onto_found(pile[-1], found):
            return f"{i + 1}f"
    for i, pile in enumerate(tab):
        if stock and (not pile or above(stock, pile[-1])):
            return f"s{i + 1}"
    for i, pile in enumerate(tab):
        if talon and pile and above(talon, pile[-1]):
            return f"t{i + 1}"
    for i, src in enumerate(tab):
        for j, dst in enumerate(tab):
            if i != j and src and dst and above(src[0], dst[-1]):
                return f"{i + 1}{j + 1}"
    return "ht"


def move(r, cmd):
    for ch in cmd:
        r.key(ch, 0.12)
    r.key(rec.ENTER, 0.6)
    for q in ("Buy game?", "Inspect game?"):
        if q in r.text():
            r.key("y", 0.1)
            r.key(rec.ENTER, 0.6)


def main():
    r = rec.Rec("canfield", "Canfield")
    r.wait_for("y or n?")
    r.pump(0.8)
    r.key("n", 0.1)
    r.key(rec.ENTER, 0.3)
    r.wait_for(TITLE)
    r.pump(1.5)
    while r.elapsed() < 42:
        move(r, choose(*board(r)))
        r.pump(0.3)
    r.pump(1.0)
    move(r, "q")
    r.wait_for("y or n", 3)
    r.pump(1.0)
    r.key("n", 0.1)
    r.finish(rec.ENTER)


main()
