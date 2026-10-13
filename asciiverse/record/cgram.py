"""cgram preview: one cryptogram solved at a person's pace.

The driver works out which of the bundled maxims is on screen by matching
the cipher's letter pattern against asciiverse/cgram/maxims, then decodes
it the way a person would: the most frequent letters first, one swap at a
time (typing a letter swaps it with the letter under the cursor all
through the text), moving the cursor to a letter it decodes. Then it
lingers on the solved text and quits with ~.

    python3 asciiverse/record/cgram.py
"""
import os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

HELP = "~ to quit"
MAXIMS = os.path.join(rec.ROOT, "asciiverse", "cgram", "maxims")


def maxims():
    with open(MAXIMS) as f:
        return [e.strip("\n").split("\n") for e in f.read().split("%\n") if e.strip()]


def fits(cipher, plain):
    """True when plain encrypts to cipher under one consistent key."""
    if len(cipher) != len(plain) or any(len(a) != len(b) for a, b in zip(cipher, plain)):
        return False
    key, back = {}, {}
    for a, b in zip("".join(cipher), "".join(plain)):
        if a.isalpha() != b.isalpha() or (not a.isalpha() and a != b):
            return False
        if a.isalpha():
            a, b = a.lower(), b.lower()
            if key.setdefault(a, b) != b or back.setdefault(b, a) != a:
                return False
    return True


def text_block(r):
    """The puzzle's lines and the screen position of its first letter."""
    rows = r.rows()
    help_row = next(i for i, l in enumerate(rows) if HELP in l)
    left = rows[help_row].index(HELP)
    lines = []
    for l in rows[:help_row]:
        if l.strip():
            lines.append(l[left:].rstrip())
        elif lines:
            break
    top = help_row - 1
    while not rows[top].strip():
        top -= 1
    top -= len(lines) - 1
    return lines, top, left


def goto(r, top, left, ty, tx):
    cy, cx = r.screen.cursor.y - top, r.screen.cursor.x - left
    while cy != ty:
        r.key(rec.DOWN if ty > cy else rec.UP, 0.05)
        cy = r.screen.cursor.y - top
    cx = r.screen.cursor.x - left
    while cx != tx:
        r.key(rec.RIGHT if tx > cx else rec.LEFT, 0.04)
        cx = r.screen.cursor.x - left


def main():
    r = rec.Rec("cgram", "Cgram", cwd=os.path.join(rec.ROOT, "asciiverse", "cgram"))
    r.wait_for(HELP)
    r.pump(1.5)
    lines, top, left = text_block(r)
    solution = next(m for m in maxims() if fits(lines, m))
    # decode the letters that occur most often first
    counts = {}
    for c in "".join(solution).lower():
        if c.isalpha():
            counts[c] = counts.get(c, 0) + 1
    for p in sorted(counts, key=lambda c: -counts[c]):
        lines, top, left = text_block(r)
        spot = next(((y, x) for y, line in enumerate(solution) for x, c in enumerate(line)
                     if c.lower() == p and lines[y][x].lower() != p), None)
        if spot is None:
            continue
        goto(r, top, left, *spot)
        r.pump(0.25)
        r.key(p, 0.55)
    r.wait_for("*solved*", 3)
    r.pump(4.0)
    r.finish(b"~")


main()
