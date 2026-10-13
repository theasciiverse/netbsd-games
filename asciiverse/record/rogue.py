"""rogue preview: exploring the Dungeons of Doom and fighting what turns up.

rogue's 80x24 screen is centred whole (compat/centre.h, nb_fixed), so in
the 100x30 recording it starts at row 3, column 10. The driver walks to
the nearest thing worth having (gold and other items it can see), else
a door it has not been through, else a corridor's unexplored end, only
ever moving across or up and down, which is always allowed; attacks any
monster beside it; rests when its hit points are down to a third;
answers --More--; and after about 28 seconds, or when nothing is left to
explore, takes the stairs (%) down. After about 45 seconds it quits, and
the cast ends on rogue's score table. A take where the hero dies early
is recorded again.

    python3 asciiverse/record/rogue.py
"""
import collections, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

OY, OX = 3, 10          # where the centred 80x24 screen sits in 100x30
ITEMS = set("*!?:)]/=,")
WALK = set(".#+%") | ITEMS
STEPS = {(0, -1): "h", (1, 0): "j", (-1, 0): "k", (0, 1): "l"}
DIAG = {(-1, -1): "y", (-1, 1): "u", (1, -1): "b", (1, 1): "n"}


def grid(r):
    rows = r.rows()
    return [rows[OY + y][OX:OX + 80] for y in range(24)]


def find(g, ch):
    for y in range(1, 23):
        x = g[y].find(ch)
        if x >= 0:
            return y, x
    return None


def path_to(g, start, goal):
    """First step of a shortest orthogonal path to a cell where goal(y, x)."""
    seen = {start: None}
    q = collections.deque([start])
    while q:
        y, x = q.popleft()
        if (y, x) != start and goal(y, x):
            while seen[(y, x)] != start:
                y, x = seen[(y, x)]
            return (y - start[0], x - start[1])
        for dy, dx in STEPS:
            ny, nx = y + dy, x + dx
            if 1 <= ny < 23 and 0 <= nx < 80 and (ny, nx) not in seen and g[ny][nx] in WALK:
                seen[(ny, nx)] = (y, x)
                q.append((ny, nx))
    return None


def hit_points(g):
    m = re.search(r"Hp: *(\d+)\((\d+)\)", g[23])
    return (int(m.group(1)), int(m.group(2))) if m else (1, 1)


def take():
    """One recording; True when the hero lived to the end."""
    r = rec.Rec("rogue", "Rogue")
    r.wait_for("Level:", 8)
    r.pump(1.0)
    visited = collections.Counter()
    while r.elapsed() < 45:
        g = grid(r)
        if "Rogueists" in r.text() or "killed by" in r.text():
            r.finish(b" ")
            return False
        if "--More--" in g[0] or "-more-" in g[0]:
            r.key(" ", 0.15)
            continue
        me = find(g, "@")
        if me is None:
            r.key(" ", 0.2)
            continue
        visited[me] += 1
        y, x = me
        # a monster next to us: hit it
        foe = next(((dy, dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1)
                    if (dy or dx) and 1 <= y + dy < 23 and 0 <= x + dx < 80
                    and g[y + dy][x + dx].isupper()), None)
        if foe:
            r.key(STEPS.get(foe) or DIAG[foe], 0.18)
            continue
        hp, hp_max = hit_points(g)
        if hp * 3 <= hp_max:
            r.key("s", 0.12)
            continue

        def frontier(fy, fx):
            near_dark = any(0 <= fx + dx < 80 and g[fy + dy][fx + dx] == " "
                            for dy, dx in STEPS if 1 <= fy + dy < 23)
            return near_dark and g[fy][fx] in "#+" and visited[(fy, fx)] < 2

        step = None
        if r.elapsed() > 28 and find(g, "%"):
            if g[y][x] == "%" or (r.elapsed() > 36 and visited[me] > 3):
                r.key(">", 0.5)
                visited.clear()
                continue
            step = path_to(g, me, lambda fy, fx: g[fy][fx] == "%")
        if step is None:
            step = path_to(g, me, lambda fy, fx: g[fy][fx] in ITEMS)
        if step is None:
            step = path_to(g, me, lambda fy, fx: g[fy][fx] == "+" and visited[(fy, fx)] == 0)
        if step is None:
            step = path_to(g, me, frontier)
        if step is None and find(g, "%"):
            if g[y][x] == "%":
                r.key(">", 0.5)
                visited.clear()
                continue
            step = path_to(g, me, lambda fy, fx: g[fy][fx] == "%")
        if step is None:
            step = path_to(g, me, lambda fy, fx: visited[(fy, fx)] == 0)
        if step is None:
            r.key("s", 0.15)
            continue
        r.key(STEPS[step], 0.11)
    r.pump(1.0)
    r.key("Q", 0.6)
    r.key("y", 1.2)
    for _ in range(4):
        r.key(" ", 0.8)
    r.finish(b"")
    return True


for attempt in range(6):
    if take():
        break
    print("the hero died early; recording again", file=sys.stderr)
