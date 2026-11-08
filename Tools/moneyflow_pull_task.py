"""Task-carried moneyflow first-pull / continuation runner.

Why this exists (r1417, MSG-20261108-0700 follow-up):
`update_moneyflow.py` spawns the long pull with DETACHED_PROCESS, which does
NOT escape the creating process' job object. When the puller is seeded from an
interactive CLI session (or from a lane tick whose task ends), the job dies and
takes the child with it: the checkpoint in data/moneyflow/_progress.json froze
at done=758/5226 for 54 minutes while the gate kept reporting a healthy lane.
A scheduled task that RUNS the pull in the foreground is the carrier that the
job cannot outlive -- the task instance stays Running until the pull ends.

Contract:
  - lock alive  -> exit 0, mode no-op (never two pullers on one panel)
  - panel complete -> exit 0, mode no-op
  - otherwise   -> run refresh() in the foreground, exit with its code

Exit 0 = done or nothing to do, 2 = universe unavailable, 3 = panel mismatch
(all inherited from update_moneyflow.refresh -- this file adds no policy).
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
os.chdir(ROOT)

import scripts.update_moneyflow as mf  # noqa: E402  (path set above)


def _status():
    try:
        with io.open(mf.STATUS, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return {}


def main():
    st = _status()
    panel = st.get("panel") or {}
    if mf._lock_alive():
        print("no-op: refresh lock alive (another puller owns the panel)")
        return 0
    if panel.get("complete") and panel.get("cutoff_from_bytes") == panel.get("cutoff"):
        print("no-op: panel complete")
        return 0
    print("foreground pull starting (task-carried; CLI job cannot kill this)")
    return mf.refresh()


if __name__ == "__main__":
    sys.exit(main())