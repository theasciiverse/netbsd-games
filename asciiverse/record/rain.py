"""rain preview: 30 s of rain on a still pond, then any key ends it.

    python3 asciiverse/record/rain.py
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rec

r = rec.Rec("rain", "Rain")
r.pump(30.0)
r.finish(b"q")
