"""Records hack's catalog preview (hub/RECORDING.md): a Fighter called Ada
explores the first levels, fights what she meets, picks things up and goes
down the stairs. Usage, from the repo root after asciiverse/build.sh, with
pyte installed:

    python3 asciiverse/record/hack.py

The game runs from a copy of its archive's files (hack reads help, data and
rumors from the folder it is started in, as under av). The exploring logic
(explore_step) is shared with larn's driver.
"""
import os, random, shutil, sys, tempfile, time
from collections import deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec, ROOT  # noqa: E402


def stage(id):
    """A folder holding the game's archive files but the binary, as av
    installs them; the binary itself runs by name from out/."""
    d = tempfile.mkdtemp(prefix=f"{id}-install-")
    with open(os.path.join(ROOT, "asciiverse", "archive", f"{id}.txt")) as f:
        for line in f:
            parts = line.split()
            if not parts or parts[0].startswith("#") or parts[0] == f"out/{id}":
                continue
            name = parts[2] if len(parts) == 3 and parts[1] == "->" else os.path.basename(parts[0])
            shutil.copy(os.path.join(ROOT, parts[0]), os.path.join(d, name))
    return d


def in_doorway(grid, c):
    """A doorway sits in a wall: walls on both sides of it (the @ hides the
    door character when we stand in one)."""
    x, y = c
    h, w = len(grid), len(grid[0])
    if grid[y][x] in "+":
        return True
    vert = 0 < y < h - 1 and grid[y - 1][x] in "|-" and grid[y + 1][x] in "|-"
    horiz = 0 < x < w - 1 and grid[y][x - 1] in "|-" and grid[y][x + 1] in "|-"
    return vert or horiz


DIRS = {(-1, 0): "h", (1, 0): "l", (0, -1): "k", (0, 1): "j",
        (-1, -1): "y", (1, -1): "u", (-1, 1): "b", (1, 1): "n"}


def explore_step(grid, me, passable, want, monster, avoid=(), diagonal=True,
                 nodiag=""):
    """One move toward the nearest thing worth a visit: a monster next to us
    is attacked; otherwise breadth-first search over passable cells to the
    nearest cell that want() likes (items, stairs, unexplored edges). No
    diagonal step goes into or out of a cell whose character is in nodiag
    (hack's doorways). grid is a list of strings; me is (x, y). Returns a
    direction key."""
    h, w = len(grid), len(grid[0])
    dirs = [d for d in DIRS if diagonal or 0 in d]
    for (dx, dy) in dirs:
        x, y = me[0] + dx, me[1] + dy
        if 0 <= y < h and 0 <= x < w and monster(grid[y][x]) and (x, y) not in avoid:
            return DIRS[(dx, dy)]
    seen = {me: None}
    q = deque([me])
    goal = None
    while q:
        cur = q.popleft()
        if cur != me and want(grid, cur):
            goal = cur
            break
        for (dx, dy) in dirs:
            x, y = cur[0] + dx, cur[1] + dy
            if dx and dy and nodiag and 0 <= y < h and 0 <= x < w and \
                    (grid[y][x] in nodiag or in_doorway(grid, cur)):
                continue
            if 0 <= y < h and 0 <= x < w and (x, y) not in seen and passable(grid[y][x]) \
                    and (x, y) not in avoid:
                seen[(x, y)] = cur
                q.append((x, y))
    if goal is None:
        return random.choice([DIRS[d] for d in dirs])
    while seen[goal] != me:
        goal = seen[goal]
    return DIRS[(goal[0] - me[0], goal[1] - me[1])]


# hack's field is 80x24, centred: on 100x30 it starts at column 10, row 3;
# the map is its rows 1 to 21, the status lines 22 and 23
X0, Y0 = 10, 3
FLOOR = set(".#+<>%)[!?/=*\"$`^:")
ITEMS = set("%)[!?/=*\"$")


def hack_grid(r):
    return [r.rows()[Y0 + 1 + i][X0:X0 + 80] for i in range(21)]


def find(grid, ch):
    for y, row in enumerate(grid):
        x = row.find(ch)
        if x >= 0:
            return (x, y)
    return None


def score(cast):
    """How good a take is to watch: it must last 35 seconds, then hits and
    kills count most, then things picked up and stairs taken."""
    import json
    lines = open(cast).read().splitlines()
    idle = json.loads(lines[0]).get("idle_time_limit") or 2
    length = sum(min(json.loads(l)[0], idle) for l in lines[1:])
    if length < 35:
        return -1
    text = "".join(json.loads(l)[2] for l in lines[1:] if json.loads(l)[1] == "o")
    hits = text.count("You hit") + 3 * (text.count("You kill") + text.count("You destroy"))
    picks = len([1 for m in text.split("\x1b[4;11H")[1:] if m[:4] in [f"{c} - " for c in "abcdefghijklmnopqrstuvwxyz"]])
    return 3 * hits + 2 * picks + 4 * (text.count("Level 2") > 0)


def main():
    best = None
    cast = os.path.join(ROOT, "asciiverse", "casts", "hack.cast")
    for attempt in range(8):
        take()
        sc = score(cast)
        print(f"take {attempt + 1}: score {sc}", file=sys.stderr)
        if best is None or sc > best[0]:
            best = (sc, open(cast).read())
        if sc >= 20:
            break
    with open(cast, "w") as f:
        f.write(best[1])


def take():
    install = stage("hack")
    r = Rec("hack", "Hack", args=("-u", "Ada"), cwd=install)
    r.wait_for("experienced", 6)
    r.key("y", 0.6)
    r.wait_for("Fighter", 3)
    r.key("F", 1.5)
    visited = set()
    level = 1
    stuck = 0
    while r.elapsed() < 52:
        t = r.text()
        if "--More--" in t:
            r.key(" ", 0.4)
            continue
        if "Really attack" in t or "[yn" in t or "(y/n)" in t or "[ynq]" in t:
            r.key("n", 0.3)
            continue
        if "Pick up" in t or "pick up what" in t.lower():
            r.key("\x1b", 0.3)
            continue
        grid = hack_grid(r)
        me = find(grid, "@")
        if me is None:
            r.key(" ", 0.3)
            continue
        visited.add(me)
        here_items = False
        # stairs down once we have looked around a little
        if grid[me[1]][me[0]] == "@" and r.elapsed() > 18 * level and find(grid, ">"):
            stairs = find(grid, ">")
            if abs(stairs[0] - me[0]) <= 1 and abs(stairs[1] - me[1]) <= 1 and stairs != me:
                d = DIRS[(stairs[0] - me[0], stairs[1] - me[1])]
                r.key(d, 0.35)
                r.key(">", 0.8)
                level += 1
                visited.clear()
                continue

        def want(g, c):
            ch = g[c[1]][c[0]]
            if ch in ITEMS:
                return True
            if r.elapsed() > 18 * level and ch == ">":
                return True
            if c in visited:
                return False
            # an edge of what we know: a passable cell next to darkness
            for (dx, dy) in DIRS:
                x, y = c[0] + dx, c[1] + dy
                if 0 <= y < len(g) and 0 <= x < len(g[0]) and g[y][x] == " " and ch in ".#+":
                    return True
            return False

        def monster(ch):
            return ch.isalpha() and ch != "d"  # d is Ada's dog, let it be

        def passable(ch):
            return ch in FLOOR or ch.isalpha()

        dog = find(grid, "d")
        if stuck >= 2:          # the last moves changed nothing: try another way
            k = random.choice(list(DIRS.values()))
            stuck = 0
        else:
            k = explore_step(grid, me, passable, want, monster,
                             avoid={dog} if dog else (), nodiag="+")
        r.key(k, 0.28)
        after = hack_grid(r)
        stuck = stuck + 1 if after == grid else 0
        # step onto an item: pick it up
        if "You see here" in r.text() or "There are several" in r.text():
            r.key(",", 0.5)
    r.key("S", 1.0)            # save, which ends the game quietly
    r.finish(b"", grace=4.0)
    shutil.rmtree(install, ignore_errors=True)


if __name__ == "__main__":
    main()
