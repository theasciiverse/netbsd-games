"""worms preview: 30 s of `worms -C -H -n 8`, as av starts it, then any
key ends it.

    python3 asciiverse/record/worms.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

r = rec.Rec("worms", "Worms", args=("-C", "-H", "-n", "8"))
r.pump(30.0)
r.finish(b"q")
