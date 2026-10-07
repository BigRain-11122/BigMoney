# -*- coding: utf-8 -*-
"""r671 bm-c rebase-conflict per-face resolver (18-UU, push-race window
11:12-11:15 vs bm-a r819 postscript 43cef3eb3).

Laws applied (r440 two-rule + r758 host-single-writer + r405 stage-vanish
+ r619 union, all from pit canon):
  * bm-a host single-writer faces (dashboard_status.*, strategy_scorecard,
    scorecard_v1) -> ORIGIN side wins (host alive, postscript 11:14:53).
  * every other face -> ts-duel newer-wins on extracted max ISO timestamp;
    no ts field -> local side (:3) = fresher local measurement default.
  * Stage semantics: during REBASE stage2=upstream(origin) stage3=replayed
    commit(mine) -- opposite of merge; explicit `git show :N:path`
    materialization only, NEVER checkout --ours/--theirs (r405+semantics
    family). Read stages BEFORE add (stages vanish after add, r405).
Receipt -> results/_r671bmc_rebase_resolve.json. Zero --no-verify."""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CREATE_NO_WINDOW = 0x08000000
RECEIPT = os.path.join(ROOT, "results", "_r671bmc_rebase_resolve.json")
HOST_ORIGIN_FACES = {
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/strategy_scorecard.json",
    "results/scorecard_v1.json",
}
TS_PAT = re.compile(
    r'"(?:generated|ts|updated_at|updated|last_run_at|generated_at|asof|scan_ts)"'
    r'\s*:\s*"?(\d{4}-\d{2}-\d{2}[T ][\d:.]+)')


def _git(args):
    r = subprocess.run(["git", "-C", ROOT] + args, capture_output=True,
                       creationflags=CREATE_NO_WINDOW)
    return r.returncode, (r.stdout or b""), (r.stderr or b"")


def _stage(path, n):
    rc, out, err = _git(["show", ":%d:%s" % (n, path)])
    if rc != 0:
        return None
    return out


def _max_ts(blob):
    if blob is None:
        return None
    try:
        txt = blob.decode("utf-8", errors="replace")
    except Exception:
        return None
    stamps = TS_PAT.findall(txt)
    return max(stamps) if stamps else None


def main():
    rc, out, _ = _git(["diff", "--name-only", "--diff-filter=U"])
    files = [f.strip() for f in out.decode("utf-8", "replace").splitlines()
             if f.strip()]
    assert files, "no UU files -- wrong context"
    decisions = []
    for path in files:
        p2 = _stage(path, 2)
        p3 = _stage(path, 3)
        assert p2 is not None and p3 is not None, \
            "stage read fail %s (r405 vanish guard)" % path
        ts2, ts3 = _max_ts(p2), _max_ts(p3)
        if path in HOST_ORIGIN_FACES:
            side, why = 2, "bm-a host single-writer face (r758/r378 law)"
        elif ts2 and ts3:
            side = 3 if ts3 >= ts2 else 2
            why = "ts-duel newer-wins (origin=%s local=%s)" % (ts2, ts3)
        else:
            side, why = 3, "no-ts default: local fresher measurement (r440)"
        winner = _stage(path, side)
        assert winner is not None, "winner re-read fail %s" % path
        with open(os.path.join(ROOT, path), "wb") as fh:
            fh.write(winner)
        rca, _, erra = _git(["add", "--", path])
        assert rca == 0, "add fail %s: %s" % (path, erra.decode(errors="replace"))
        decisions.append({"path": path, "winner_stage": side,
                          "winner_is": "origin/upstream" if side == 2 else "local/replayed",
                          "ts_origin": ts2, "ts_local": ts3, "rule": why})
    with open(RECEIPT, "w", encoding="utf-8", newline="\n") as fh:
        json.dump({"round": 671, "machine": "bm-c",
                   "context": "push-race 18-UU vs bm-a r819 postscript 43cef3eb3",
                   "n_faces": len(decisions), "faces": decisions},
                  fh, ensure_ascii=False, indent=1)
    for d in decisions:
        print("RESOLVED %-46s -> %s (%s)" % (d["path"], d["winner_is"], d["rule"]))
    print("receipt:", os.path.relpath(RECEIPT, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
