"""Records warp's catalog preview (hub/RECORDING.md): the Enterprise hunts
the enemies of the first waves, firing photon torpedoes and phasers along
any line where an enemy sits. Usage, from the repo root after
asciiverse/build.sh, with pyte installed:

    python3 asciiverse/record/warp.py

warp reads its star maps from the folder it is started in (as under av),
and its scoreboard takes the player's name from $NAME, which the shared
recorder does not set, so this driver adds NAME=player.
"""
import json, os, random, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec  # noqa: E402
from rec import Rec, ROOT  # noqa: E402
from hack import stage  # noqa: E402

_execvpe = os.execvpe


def _execvpe_with_name(file, args, env):
    return _execvpe(file, args, dict(env, NAME="player"))


os.execvpe = _execvpe_with_name

# warp's screen is 80x24, centred: on 100x30 it starts at column 10, row 3;
# its status line is row 0, the 23x40 universe rows 1 to 23, two columns a cell
X0, Y0, ROWS, COLS = 10, 3, 23, 40
SHIP = "EeCc"
ENEMIES = set("KGRATxXoO&<>")
MOVE = {(-1, 0): "h", (1, 0): "l", (0, -1): "k", (0, 1): "j",
        (-1, -1): "y", (1, -1): "u", (-1, 1): "b", (1, 1): "n"}


def universe(r):
    rows = r.rows()
    return [[rows[Y0 + 1 + y][X0 + 2 * x] for x in range(COLS)] for y in range(ROWS)]


def wrapd(a, b, n):
    """The shortest signed step from a to b on a ring of n."""
    d = (b - a) % n
    return d - n if d > n // 2 else d


def take():
    install = stage("warp")
    r = Rec("warp", "Warp", cwd=install)
    r.wait_for("instructions", 6)
    r.key("n", 4.5)
    fired = 0
    while r.elapsed() < 52:
        t = r.text()
        if "Hit space" in t:
            r.key(" ", 2.0)
            continue
        u = universe(r)
        ship = next(((x, y) for y in range(ROWS) for x in range(COLS) if u[y][x] in SHIP), None)
        if ship is None:
            r.key("i", 0.5)             # back to the Enterprise
            continue
        enemies = [(x, y) for y in range(ROWS) for x in range(COLS) if u[y][x] in ENEMIES]
        shot = False
        for (ex, ey) in enemies:
            dx, dy = wrapd(ship[0], ex, COLS), wrapd(ship[1], ey, ROWS)
            dist = max(abs(dx), abs(dy))
            if dist == 0 or dist > 6:
                continue
            if dist <= 3 and random.random() < 0.5:
                r.key("%", 0.35)                       # torpedoes all round
                fired += 1
                shot = True
                break
            if dx == 0 or dy == 0 or abs(dx) == abs(dy):
                step = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
                key = MOVE[step]
                if dist <= 4 and random.random() < 0.6:
                    r.key(chr(ord(key) & 31), 0.35)     # Ctrl: phasers
                else:
                    r.key(key.upper(), 0.35)           # Shift: torpedo
                fired += 1
                shot = True
                break
        if shot:
            continue
        if enemies:
            ex, ey = min(enemies, key=lambda e: max(abs(wrapd(ship[0], e[0], COLS)),
                                                     abs(wrapd(ship[1], e[1], ROWS))))
            dx, dy = wrapd(ship[0], ex, COLS), wrapd(ship[1], ey, ROWS)
            # line up with it: close the shorter gap first
            if abs(dx) > 1 and abs(dy) > 1 and abs(dx) != abs(dy):
                if abs(dx) < abs(dy):
                    step = ((dx > 0) - (dx < 0), 0)
                else:
                    step = (0, (dy > 0) - (dy < 0))
            else:
                step = ((dx > 0) - (dx < 0), (dy > 0) - (dy < 0))
            nx, ny = (ship[0] + step[0]) % COLS, (ship[1] + step[1]) % ROWS
            if u[ny][nx] == "*":            # never ram a star
                step = random.choice(list(MOVE))
            r.key(MOVE[step], 0.5)
        else:
            r.key(random.choice("hjklyubn"), 0.6)
    r.key("Q", 1.5)
    for _ in range(4):
        if "Hit space" in r.text() or "[Type" in r.text():
            r.key("q", 1.0)
    r.finish(b"q", grace=5.0)
    shutil.rmtree(install, ignore_errors=True)
    return fired


def score(cast):
    """It must last 35 seconds; then the points warp shows at the end of its
    status line (enemies destroyed, waves survived)."""
    import pyte
    lines = open(cast).read().splitlines()
    idle = json.loads(lines[0]).get("idle_time_limit") or 2
    length = sum(min(json.loads(l)[0], idle) for l in lines[1:])
    if length < 35:
        return -1
    screen = pyte.Screen(100, 30)
    stream = pyte.ByteStream(screen)
    best = 0
    for l in lines[1:]:
        e = json.loads(l)
        if e[1] != "o":
            continue
        stream.feed(e[2].encode())
        status = screen.display[Y0]
        if "Stardate" in status:
            tail = status.split()[-1]
            if tail.lstrip("-").isdigit():
                best = max(best, int(tail))
    return best


def main():
    best = None
    cast = os.path.join(ROOT, "asciiverse", "casts", "warp.cast")
    for attempt in range(4):
        random.seed(attempt)
        take()
        sc = score(cast)
        print(f"take {attempt + 1}: score {sc}", file=sys.stderr)
        if best is None or sc > best[0]:
            best = (sc, open(cast).read())
    with open(cast, "w") as f:
        f.write(best[1])


if __name__ == "__main__":
    main()
