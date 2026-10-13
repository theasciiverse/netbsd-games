"""hunt preview: a deathmatch between two of hunt's own computer players
(hunt -o, "otto"), seen through hunt's spectator mode (hunt -m), which
shows the whole maze.

The two ottos run in pseudo-terminals of their own, not recorded: the
first starts the game, and with it the server huntd beside it; the second
joins by hunt's broadcast on the local network. An otto only moves once
the server has answered a key of its own (READY), so each is started with
one scan (s). The recorded client then joins as the spectator "watcher".
After about 45 seconds it quits, and the ottos and the server are stopped
(the server would otherwise wait 90 seconds for players before leaving).

    python3 asciiverse/record/hunt.py
"""
import fcntl, os, pty, select, shutil, signal, struct, sys, tempfile, termios, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

OUT = os.path.join(rec.ROOT, "out")


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
    """Read and drop the second player's screen, so it never blocks."""
    while True:
        r, _, _ = select.select([fd], [], [], 0)
        if not r:
            return
        try:
            if not os.read(fd, 65536):
                return
        except OSError:
            return


def stop_servers():
    """kill -9 the huntd started from out/: it renames itself HUNT, so it is
    found by its executable, not its name."""
    me = os.path.realpath(os.path.join(OUT, "huntd"))
    for pid in os.listdir("/proc"):
        if pid.isdigit():
            try:
                exe = os.readlink(f"/proc/{pid}/exe")
            except OSError:
                continue
            if exe in (me, me + " (deleted)"):
                os.kill(int(pid), signal.SIGKILL)


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
    r = rec.Rec("hunt", "Hunt", args=("-m", "-n", "watcher"))
    r.wait_for("team", 10)
    r.pump(0.8)
    r.key(rec.ENTER, 0.5)
    while r.elapsed() < 45:
        r.pump(0.2)
        for _, fd in players:
            drain(fd)
    r.key("q", 1.0)
    if "uit" in r.text():
        r.key("y", 0.5)
    r.finish(b"", grace=4.0)
    for pid, _ in players:
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
    stop_servers()
    shutil.rmtree(home, ignore_errors=True)


main()
