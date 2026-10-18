"""hunt preview: the recorded player, Nightjar, hunts two of hunt's own
computer players (hunt -o, "otto") through the maze.

The two ottos run in pseudo-terminals of their own, not recorded: the
first starts the game, and with it the server huntd beside it; the second
joins by hunt's broadcast on the local network. An otto only moves once
the server has answered a key of its own (READY), so each is started with
one scan (s). The recorded client then joins as a player, named through
hunt's own HUNT variable and entering with the scanner on, so the ottos
show on its map wherever they are.

A small bot plays it by reading the screen through pyte: it walks the
maze it has seen towards a square in line with an otto (turning to face
each step first, since walking sideways onto a mine trips it far more
often), turns to face the otto and fires, throws a grenade now and then,
and re-enters when it is killed. After about 44 seconds it quits, and the
recording ends on the game's statistics (hunt -S), which list the kills.
The ottos and the server are stopped after.

    python3 asciiverse/record/hunt.py
"""
import collections, fcntl, os, pty, random, select, shutil, signal, struct, sys, tempfile, termios, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

OUT = os.path.join(rec.ROOT, "out")
NAME = "Nightjar"
PLAY_SECONDS = 44

# the arena is 51x23 with the status at column 60, the message line under it
WIDTH, HEIGHT = 51, 23
WALLS = set("-|+/\\#")
MINES = set(";g")
ME = {">": "l", "<": "h", "^": "k", "v": "j"}
OTTO = {"}": "l", "{": "h", "i": "k", "!": "j"}
STEP = {"h": (0, -1), "j": (1, 0), "k": (-1, 0), "l": (0, 1)}

random.seed(5)
LOG = os.environ.get("HUNT_REC_LOG")


def log(msg):
    if LOG:
        with open(LOG, "a") as f:
            f.write(msg + "\n")


def otto(home):
    """A computer player in a pseudo-terminal of its own, not recorded."""
    pid, fd = pty.fork()
    if pid == 0:
        env = {"PATH": f"{OUT}:{os.environ['PATH']}", "HOME": home, "USER": "player",
               "LOGNAME": "player", "TERM": "xterm-256color", "LANG": "C.UTF-8"}
        os.chdir(home)
        os.execvpe("hunt", ["hunt", "-o"], env)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 24, 80, 0, 0))
    return pid, fd


def drain(fd):
    """Read and drop a computer player's screen, so it never blocks."""
    while True:
        r, _, _ = select.select([fd], [], [], 0)
        if not r:
            return
        try:
            if not os.read(fd, 65536):
                return
        except OSError:
            return


def servers():
    """The huntd processes started from out/: huntd renames itself HUNT, so
    it is found by its executable, not its name."""
    me = os.path.realpath(os.path.join(OUT, "huntd"))
    found = []
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                exe = os.readlink(f"/proc/{pid}/exe")
            except OSError:
                continue
            if exe in (me, me + " (deleted)"):
                found.append(int(pid))
    return found


def stop_servers():
    for pid in servers():
        os.kill(pid, signal.SIGKILL)


class View:
    """What the player's screen shows: the arena, where everyone is."""

    def __init__(self, rows):
        self.ok = False
        for y, line in enumerate(rows):
            x = line.find("Ammo:")
            if x >= 60:
                self.oy, self.ox = y, x - 60
                self.ok = True
                break
        if not self.ok:
            return
        self.grid = [rows[self.oy + y][self.ox:self.ox + WIDTH] for y in range(HEIGHT)]
        self.me, self.facing, self.ottos = None, None, []
        for y, line in enumerate(self.grid):
            for x, c in enumerate(line):
                if c in ME:
                    self.me, self.facing = (y, x), ME[c]
                elif c in OTTO:
                    self.ottos.append((y, x))
        status = [rows[self.oy + y][self.ox + 60:] for y in range(HEIGHT)]
        self.ammo = int(status[0].split()[-1]) if status[0].split()[-1].isdigit() else 0
        self.gun_ok = "ok" in status[1]
        self.scanning = any(NAME in s and s[6:7] == "*" for s in status)

    def free(self, y, x):
        return 0 <= y < HEIGHT and 0 <= x < WIDTH and self.grid[y][x] not in WALLS | MINES

    def line_of_fire(self, a, b, reach=20):
        """(direction, walls) from a to b if they are in line, walls being
        how many plain walls seen stand between them (a shot breaks those),
        else None; a door or a diagonal wall in the way is None too."""
        (ay, ax), (by, bx) = a, b
        if ay == by and 0 < abs(bx - ax) <= reach:
            d = "l" if bx > ax else "h"
            cells = [(ay, x) for x in range(min(ax, bx) + 1, max(ax, bx))]
        elif ax == bx and 0 < abs(by - ay) <= reach:
            d = "j" if by > ay else "k"
            cells = [(y, ax) for y in range(min(ay, by) + 1, max(ay, by))]
        else:
            return None
        between = [self.grid[y][x] for y, x in cells]
        if any(c in "/\\#" for c in between):
            return None
        return d, sum(c in WALLS for c in between)


class Hunter:
    def __init__(self, r):
        self.r = r
        self.blocked = {}          # square -> time it was found blocked
        self.wander = None
        self.last_grenade = 0.0

    def send(self, k, wait=0.1):
        self.r.key(k, wait)

    def path_to(self, v, goals):
        """First step of the shortest walk over squares not known to be walls
        or mines, to any of goals."""
        now = time.time()
        start = v.me
        prev = {start: None}
        q = collections.deque([start])
        while q:
            cur = q.popleft()
            if cur in goals and cur != start:
                while prev[cur] != start:
                    cur = prev[cur]
                for k, (dy, dx) in STEP.items():
                    if (start[0] + dy, start[1] + dx) == cur:
                        return k
            for dy, dx in STEP.values():
                n = (cur[0] + dy, cur[1] + dx)
                if n in prev or not v.free(*n) or now - self.blocked.get(n, -99) < 4:
                    continue
                prev[n] = cur
                q.append(n)
        return None

    def walk(self, v, k):
        """Face the way, then step; remember a square that would not take us."""
        if v.facing != k:
            self.send(k.upper())
            return
        before = v.me
        self.send(k, 0.1)
        end = time.time() + 0.35
        while time.time() < end:
            after = View(self.r.rows())
            if after.ok and after.me != before:
                return
            self.r.key(b"", 0.05)
        dy, dx = STEP[k]
        self.blocked[(before[0] + dy, before[1] + dx)] = time.time()

    @staticmethod
    def walls_ok(v):
        """How many walls to shoot through: more the more charges we have."""
        return min(3, v.ammo // 10)

    def cool(self, v, ahead):
        """The gun cools off only as its owner moves (three shots, then a
        step): step ahead if it is open, else to the side, still facing."""
        dy, dx = STEP[ahead]
        if v.free(v.me[0] + dy, v.me[1] + dx) and (v.me[0] + 2 * dy, v.me[1] + 2 * dx) not in v.ottos:
            self.send(ahead, 0.15)
            return
        sides = [d for d in ("hl" if ahead in "jk" else "jk")
                 if v.free(v.me[0] + STEP[d][0], v.me[1] + STEP[d][1])]
        self.send(random.choice(sides) if sides else ahead, 0.15)

    def tick(self):
        text = self.r.text()
        if "Re-enter game" in text:
            self.send("y", 1.0)
            return
        v = View(self.r.rows())
        if not v.ok or v.me is None:
            self.r.pump(0.1)
            return
        if not v.scanning and v.ammo > 3:
            self.send("s")
            return
        near = sorted(v.ottos, key=lambda o: abs(o[0] - v.me[0]) + abs(o[1] - v.me[1]))
        # an otto in line, in the open or behind a wall or two: face it and
        # fire (a shot breaks a wall), throw a grenade or a satchel charge
        for o in near:
            lf = v.line_of_fire(v.me, o)
            if lf is None or lf[1] > self.walls_ok(v):
                continue
            d, walls = lf
            if v.facing != d:
                self.send(d.upper())
                return
            dist = abs(o[0] - v.me[0]) + abs(o[1] - v.me[1])
            log(f"fire {d} at {o} from {v.me} walls={walls} ammo={v.ammo}")
            if dist >= 6 and time.time() - self.last_grenade > 6 and v.ammo >= 60:
                self.last_grenade = time.time()
                self.send("G", 0.3)         # a bomb
            elif dist >= 5 and time.time() - self.last_grenade > 6 and v.ammo >= 35:
                self.last_grenade = time.time()
                self.send("F", 0.3)         # a satchel charge
            elif (dist >= 3 or walls) and time.time() - self.last_grenade > 6 and v.ammo >= 20:
                self.last_grenade = time.time()
                self.send("g", 0.3)
            elif v.ammo > 0 and v.gun_ok:
                self.send("f", 0.15)
            elif dist == 1:
                self.send(d, 0.15)          # out of charges: stab
            else:
                self.cool(v, d)
            return
        # else walk to a square in line with an otto
        goals = set()
        for o in v.ottos:
            for k, (dy, dx) in STEP.items():
                walls = 0
                for n in range(1, 16):
                    sq = (o[0] + dy * n, o[1] + dx * n)
                    if not (0 <= sq[0] < HEIGHT and 0 <= sq[1] < WIDTH) or v.grid[sq[0]][sq[1]] in "/\\#":
                        break
                    if v.grid[sq[0]][sq[1]] in WALLS:
                        walls += 1
                        if walls > self.walls_ok(v):
                            break
                        continue
                    if v.free(*sq):
                        goals.add(sq)
        k = self.path_to(v, goals) if goals else None
        if k is None and near and v.ammo > 10 and v.gun_ok:
            # no way round: shoot through towards the nearest one
            o = near[0]
            dy, dx = o[0] - v.me[0], o[1] - v.me[1]
            d = ("j" if dy > 0 else "k") if abs(dy) > abs(dx) else ("l" if dx > 0 else "h")
            log(f"dig {d} towards {o} from {v.me}")
            if v.facing != d:
                self.send(d.upper())
            else:
                self.send("f", 0.15)
            return
        if k is None and near and v.ammo > 10:
            self.cool(v, v.facing)
            return
        if k is None:
            if self.wander is None or self.wander == v.me or random.random() < 0.05:
                self.wander = (random.randrange(1, HEIGHT - 1), random.randrange(1, WIDTH - 1))
            k = self.path_to(v, {self.wander})
            if k is None:
                # boxed in by what we have seen: keep going the way we face
                # while it is open, else any open way, else break a wall
                self.wander = None
                open_ways = [d for d, (dy, dx) in STEP.items() if v.free(v.me[0] + dy, v.me[1] + dx)]
                if v.facing in open_ways:
                    k = v.facing
                elif open_ways:
                    k = random.choice(open_ways)
                elif v.ammo > 0:
                    log(f"break out {v.facing} from {v.me}")
                    self.send("f", 0.15)
                    return
                else:
                    k = random.choice("hjkl")
            log(f"wander {k} to {self.wander} from {v.me}")
        else:
            log(f"walk {k} from {v.me} ottos={v.ottos}")
        self.walk(v, k)


def main():
    stop_servers()
    home = tempfile.mkdtemp(prefix="netbsd-rec-hunt-")
    players = [otto(home)]
    deadline = time.time() + 3
    while time.time() < deadline:
        drain(players[0][1])
        time.sleep(0.05)
    players.append(otto(home))
    deadline = time.time() + 2
    while time.time() < deadline:
        for _, fd in players:
            drain(fd)
        time.sleep(0.05)
    for _, fd in players:
        os.write(fd, b"s")
    server_pids = servers()

    # play, then quit and show the statistics; "localhost" so the table's
    # heading names no machine
    r = rec.Rec("hunt", "Hunt", command="hunt; clear; hunt -S localhost; sleep 3",
                env={"HUNT": f"scan,name={NAME}"})
    _key = r.key

    def key(k, wait=0.15):
        _key(k, 0)
        end = time.time() + wait
        while time.time() < end:
            r.pump(0.03)
            for _, fd in players:
                drain(fd)
    r.key = key

    r.wait_for("team", 10)
    r.key(rec.ENTER, 1.0)
    h = Hunter(r)
    while r.elapsed() < PLAY_SECONDS:
        h.tick()
    r.key("q", 0.6)
    if "uit" in r.text():
        r.key("y", 0.3)
    r.wait_for("Enemy", 5)
    r.finish(b"", grace=8.0)
    for pid, _ in players:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
    for pid in server_pids:
        try:
            os.kill(pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
    stop_servers()
    shutil.rmtree(home, ignore_errors=True)


main()
