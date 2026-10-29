"""Run the smoke suite with a faulthandler watchdog.

Why this exists: two detached `python -m smoke_test` runs in r1350 stopped emitting output
mid-suite with CPU flat, and a redirected stdout gives no way to tell a slow leg from a
blocked one. `-u` fixes the buffering half; this wrapper fixes the diagnosis half -- after
`--after` seconds faulthandler dumps every thread's stack and the process exits, so the next
occurrence names the leg instead of costing another window.

Usage:
    python Tools/smoke_watchdog.py [--after=300]
"""
import faulthandler
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

after = 300
for a in sys.argv[1:]:
    if a.startswith("--after="):
        after = int(a.split("=", 1)[1])

faulthandler.dump_traceback_later(after, exit=True)

import smoke_test  # noqa: E402

sys.exit(smoke_test.main())