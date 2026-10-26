"""backgammon preview: White against the computer, played from the board on
screen, as `backgammon -w` (av starts it plain; -w skips the questions).

The driver reads the board at backgammon's own positions (fancy.c: the
board is 53 columns wide; the points' cells are 4 columns apart from
column 1, 13 to 18 and 12 to 7, and from column 29, 19 to 24 and 6 to 1;
White's men are 'w', the computer's 'r', counted in each 3-column cell on
the five rows above or below the middle; the bar's men sit in columns 25
to 27), placed by the label row, wherever centring put it. White moves
from 24 down to 1 and bears off to h. With the dice from the "White's
roll" line ("White's roll: 2 5" or "White rolls 3 4") it tries every order of play, keeps the sequences that use the
most dice, and plays the one that hits most, then makes most points, then
leaves fewest blots. It rolls with a space, accepts a double, and after
about 45 seconds leaves the game with q.

    python3 asciiverse/record/backgammon.py
"""
import itertools, os, re, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

TOP = "|13  14  15  16  17  18 |   |19  20  21  22  23  24 |"


def read_board(r):
    """{point: count} with White positive and Red negative, plus White's
    men on the bar, or None if the board is not on screen."""
    rows = r.rows()
    for y, line in enumerate(rows):
        x = line.find(TOP)
        if x >= 0:
            break
    else:
        return None
    board = {p: 0 for p in range(1, 25)}
    bar = 0

    def cell(p):
        if p >= 13:
            i = p - 13
            return 1 + 4 * i if i < 6 else 29 + 4 * (i - 6)
        i = 12 - p
        return 1 + 4 * i if i < 6 else 29 + 4 * (i - 6)

    for p in range(1, 25):
        rng = range(y + 1, y + 6) if p >= 13 else range(y + 7, y + 12)
        for yy in rng:
            if yy >= len(rows):
                continue
            seg = rows[yy][x + cell(p): x + cell(p) + 3]
            board[p] += seg.count("w") - seg.count("r")
    for yy in range(y + 1, y + 12):
        if yy < len(rows):
            bar += rows[yy][x + 25: x + 28].count("w")
    return board, bar


def moves_for(board, bar, die):
    """White's single moves with one die: (from, to), from 25 for the bar,
    to 0 for bearing off."""
    out = []
    if bar:
        t = 25 - die
        if board[t] >= -1:
            out.append((25, t))
        return out
    home = all(board[p] <= 0 for p in range(7, 25))
    highest = max([p for p in range(1, 25) if board[p] > 0], default=0)
    for s in range(1, 25):
        if board[s] <= 0:
            continue
        t = s - die
        if t >= 1:
            if board[t] >= -1:
                out.append((s, t))
        elif home and (t == 0 or s == highest):
            out.append((s, 0))
    return out


def apply(board, bar, mv):
    b = dict(board)
    s, t = mv
    hit = 0
    if s == 25:
        bar -= 1
    else:
        b[s] -= 1
    if t >= 1:
        if b[t] == -1:
            b[t] = 0
            hit = 1
        b[t] += 1
    return b, bar, hit


def sequences(board, bar, dice):
    """All ways to play the dice in some order: (moves, board, hits)."""
    best = []
    orders = set(itertools.permutations(dice))

    def go(b, br, left, done, hits):
        if not left:
            best.append((done, b, hits))
            return
        ms = moves_for(b, br, left[0])
        if not ms:
            best.append((done, b, hits))
            return
        for mv in ms:
            nb, nbr, h = apply(b, br, mv)
            go(nb, nbr, left[1:], done + [mv], hits + h)

    for o in orders:
        go(board, bar, list(o), [], 0)
    return best


def choose(board, bar, d1, d2):
    dice = [d1] * 4 if d1 == d2 else [d1, d2]
    seqs = sequences(board, bar, dice)
    most = max(len(s[0]) for s in seqs)
    seqs = [s for s in seqs if len(s[0]) == most]
    if most == 1 and d1 != d2:
        # only one die can be played: the larger, if it can
        big = [s for s in seqs if s[0] and abs(s[0][0][0] - s[0][0][1]) >= max(d1, d2)
               or (s[0] and s[0][0][1] == 0)]
        seqs = big or seqs

    def score(s):
        moves, b, hits = s
        made = sum(1 for p in range(1, 25) if b[p] >= 2)
        blots = sum(1 for p in range(1, 25) if b[p] == 1)
        return (hits, made, -blots)

    return max(seqs, key=score)[0]


def fmt(moves):
    def pos(p):
        return "b" if p == 25 else "h" if p == 0 else str(p)
    return ",".join(f"{pos(s)}-{pos(t)}" for s, t in moves)


r = rec.Rec("bsd-backgammon", "BSD Backgammon", command="backgammon -w")
r.pump(1.5)
r.wait_for("continue", 5.0)
r.key(b"\n", 1.5)
start = time.time()
last = None
while time.time() - start < 45:
    text = r.text()
    if "accept" in text.lower() and "?" in text:
        r.key(b"y", 1.0)
        continue
    if "play again" in text.lower():
        break
    # "White's roll:  2 5  Move:" on the first move, "White rolls 3 4.  Move:"
    # after a roll of its own
    m = re.search(r"White(?:'s roll:| rolls)\s+(\d)\s+(\d)\.?\s+Move:\s*$", text, re.M)
    if m:
        state = read_board(r)
        if state and (m.group(0), state) != last:
            board, bar = state
            moves = choose(board, bar, int(m.group(1)), int(m.group(2)))
            last = (m.group(0), state)
            r.pump(1.0)
            for ch in fmt(moves).encode():
                r.key(bytes([ch]), 0.12)
            r.key(b"\n", 2.0)
            continue
    # White's turn to roll: a line that is only "White" (row 18; the
    # computer's last move is reported on the line below it)
    if re.search(r"^\s*White\s*$", text, re.M):
        r.key(b" ", 1.5)
        continue
    r.pump(0.5)
r.key(b"q", 0.8)
r.key(b"y", 1.0)
r.finish(b"")
