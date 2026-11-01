"""Records phantasia's catalog preview (hub/RECORDING.md): a new character,
a Fighter named Terminus, wanders out from the start, fights what it meets
and takes the gold it finds, then quits. Usage, from the repo root after
asciiverse/build.sh, with pyte installed:

    python3 asciiverse/record/phantasia.py

Encounters are random, so it plays several takes and keeps the one with
the most fighting.
"""
import json, os, random, re, shutil, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rec import Rec, ROOT  # noqa: E402
from hack import stage  # noqa: E402


def take():
    install = stage("phantasia")
    r = Rec("phantasia", "Phantasia", cwd=install)
    r.wait_for("character to run", 6)
    r.key("n", 1.5)                  # a new character ...
    r.key("2", 1.2)                  # ... a Fighter
    r.key("1", 1.0)                  # keep the first roll
    for c in "Terminus":
        r.key(c, 0.08)
    r.key("\r", 0.6)
    r.key("pass\r", 0.4)             # a password, twice
    r.key("pass\r", 1.5)
    heading = random.choice("NE")
    while r.elapsed() < 46:
        t = r.text()
        if "Care to give it another try" in t:
            r.key("n", 2.0)
            break
        if "-- more --" in t:
            r.key(" ", 0.6)
            continue
        if "want them ?" in t:       # gold found
            r.key("y", 0.8)
            continue
        if "Still want one ?" in t or "Do you want to quit ?" in t:
            r.key("n", 0.6)
            continue
        if "1:Melee" in t:           # a fight: mostly melee, sometimes skirmish
            r.key(random.choice("1112"), 0.7)
            continue
        if "1:Move" not in t:
            r.pump(0.3)
            continue
        if random.random() < 0.2:
            heading = random.choice("NE")
        r.key(heading, 0.45)         # wander out, where the monsters are
    # good-bye only works from the main menu: see a fight through first
    for _ in range(40):
        t = r.text()
        if "1:Move" in t and "1:Melee" not in t and "-- more --" not in t:
            r.key("5", 0.8)          # good-bye ...
            r.key("y", 1.0)          # ... really
            break
        if "Care to give it another try" in t:
            r.key("n", 2.0)
            break
        r.key(" " if "-- more --" in t else "1", 0.5)
    r.finish(b"", grace=4.0)
    shutil.rmtree(install, ignore_errors=True)


def score(cast):
    """30 to 60 seconds; then the more kinds of monster met the better (a
    long flock of one kind is dull), kills and gold found."""
    lines = open(cast).read().splitlines()
    idle = json.loads(lines[0]).get("idle_time_limit") or 2
    length = sum(min(json.loads(l)[0], idle) for l in lines[1:])
    if not 30 <= length <= 60:
        return -1
    text = "".join(json.loads(l)[2] for l in lines[1:] if json.loads(l)[1] == "o")
    kinds = set(re.findall(r"attacked by (?:an? |the )?([A-Za-z' -]+?),", text))
    return 10 * len(kinds) + text.count("You killed it") + 3 * text.count("gold pieces")


def main():
    best = None
    cast = os.path.join(ROOT, "asciiverse", "casts", "phantasia.cast")
    for attempt in range(6):
        random.seed(attempt)
        take()
        sc = score(cast)
        print(f"take {attempt + 1}: score {sc}", file=sys.stderr)
        if best is None or sc > best[0]:
            best = (sc, open(cast).read())
        if sc >= 45:
            break
    with open(cast, "w") as f:
        f.write(best[1])


if __name__ == "__main__":
    main()
