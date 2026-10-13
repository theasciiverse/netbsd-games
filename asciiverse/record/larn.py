"""Records larn's catalog preview (hub/RECORDING.md): from the town the
player walks into the dungeon, then explores, fights and takes what lies
around. Usage, from the repo root after asciiverse/build.sh, with pyte
installed:

    python3 asciiverse/record/larn.py

larn draws no @: the player is where the cursor stands. Explored floor is
blank, like the unexplored, so the driver prefers blank cells it has not
visited and treats # as wall.
"""
import json, os, random, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec, ROOT  # noqa: E402
from hack import DIRS, stage  # noqa: E402

# larn's screen is 80x24, centred: on 100x30 it starts at column 10, row 3;
# the map is its first 17 rows and 67 columns
X0, Y0, MAPW, MAPH = 10, 3, 67, 17
MONSTERS = set("BGHJKOScjtAELNQRZabhiCTYdegmvzFWflorXVpqsyUkMwDPxnu")
ITEMS = set("!?$*:)([]{}^=+~&ofTPBC%<")


def grid_of(r):
    return [r.rows()[Y0 + i][X0:X0 + MAPW] for i in range(MAPH)]


def me_of(r):
    c = r.screen.cursor
    return (c.x - X0, c.y - Y0)


def take():
    install = stage("larn")
    r = Rec("larn", "Larn", cwd=install)
    r.wait_for("Press return", 6)
    r.key("\r", 1.2)
    visited = {}
    in_dungeon = False
    last = None
    while r.elapsed() < 54:
        # only the newest message line is a question waiting for us
        msgs = [row[X0:].rstrip() for row in r.rows()[Y0 + 19:Y0 + 24]]
        low = next((m for m in reversed(msgs) if m.strip()), "").lower()
        if "go inside" in low and low.endswith("?"):
            r.key("g", 0.8)
            in_dungeon = True
            continue
        if "take it" in low and low.endswith("?"):
            r.key("t", 0.4)
            continue
        if "ignore it" in low and low.endswith("?"):
            r.key("i", 0.3)
            continue
        if "--more--" in low or "press return" in low or "press space" in low:
            r.key(" ", 0.4)
            continue
        grid = grid_of(r)
        me = me_of(r)
        if not (0 <= me[0] < MAPW and 0 <= me[1] < MAPH):
            r.key("\x1b", 0.3)
            continue
        visited[me] = visited.get(me, 0) + 1
        if not in_dungeon:
            # walk to the dungeon entrance
            ent = next(((x, y) for y, row in enumerate(grid) for x, ch in enumerate(row) if ch == "E"), None)
            if ent:
                dx = (ent[0] > me[0]) - (ent[0] < me[0])
                dy = (ent[1] > me[1]) - (ent[1] < me[1])
                if (dx, dy) == (0, 0):
                    in_dungeon = True
                    continue
                r.key(DIRS[(dx, dy)], 0.12)
                continue
        # next to a monster: attack it
        moved = False
        for (dx, dy), k in DIRS.items():
            x, y = me[0] + dx, me[1] + dy
            if 0 <= x < MAPW and 0 <= y < MAPH and grid[y][x] in MONSTERS:
                r.key(k, 0.3)
                moved = True
                break
        if moved:
            continue
        # an item or monster in sight: head for it
        targets = [(x, y) for y, row in enumerate(grid) for x, ch in enumerate(row)
                   if (ch in ITEMS or ch in MONSTERS) and (x, y) != me and visited.get((x, y), 0) < 2]
        options = []
        for (dx, dy), k in DIRS.items():
            x, y = me[0] + dx, me[1] + dy
            if not (0 <= x < MAPW and 0 <= y < MAPH) or grid[y][x] == "#":
                continue
            cost = visited.get((x, y), 0) * 3 + random.random()
            if targets:
                tx, ty = min(targets, key=lambda p: max(abs(p[0] - me[0]), abs(p[1] - me[1])))
                cost += max(abs(tx - x), abs(ty - y)) * 2
            options.append((cost, k))
        if not options:
            r.key(random.choice(list(DIRS.values())), 0.2)
            continue
        k = min(options)[1]
        r.key(k, 0.18)
        last = k
    r.key("Q", 0.8)          # quit, which asks
    r.key("y", 1.5)
    r.finish(b"", grace=4.0)
    shutil.rmtree(install, ignore_errors=True)


def score(cast):
    """It must last 35 seconds; then fights count most, then things taken."""
    lines = open(cast).read().splitlines()
    idle = json.loads(lines[0]).get("idle_time_limit") or 2
    length = sum(min(json.loads(l)[0], idle) for l in lines[1:])
    if length < 35:
        return -1
    text = "".join(json.loads(l)[2] for l in lines[1:] if json.loads(l)[1] == "o")
    return 3 * (text.count("You hit") + 3 * text.count("You have killed")) + \
        2 * (text.count("You pick up") + text.count("You find")) + text.count("Gold:")


def main():
    best = None
    cast = os.path.join(ROOT, "asciiverse", "casts", "larn.cast")
    for attempt in range(6):
        random.seed(attempt)
        take()
        sc = score(cast)
        print(f"take {attempt + 1}: score {sc}", file=sys.stderr)
        if best is None or sc > best[0]:
            best = (sc, open(cast).read())
        if sc >= 25:
            break
    with open(cast, "w") as f:
        f.write(best[1])


if __name__ == "__main__":
    main()
