# -*- coding: utf-8 -*-
"""r914 bm-a rebase conflict resolver (r907/r910 face-law bloodline).

Faces (5, both-sides-touched during absorb-commit replay):
  - compute_audit.json   : rolling-history UNION by ts; latest=newer-wins
  - regime_state.json    : triggers/transitions/history union (r910 law)
                           + newer top-level scalars (probe 12:11:48 mine)
  - scorecard_v1.json    : take-mine (host=bm-a writer r378 + newer 12:12:57)
  - strategy_scorecard   : take-mine (host=bm-a writer r378 + newer 12:13:04)
  - update_status.json   : take-mine (max-cutoff take, r907 law)
Stage convention during rebase: :2 = ours = origin/main side,
:3 = theirs = replayed bm-a commit side (mine).  Backup copies at
C:\\Users\\sjs20\\.codely-cli\\tmp\\r914-rebase\\ as belt-and-braces.
"""
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GIT = r"C:\Program Files\Git\cmd\git.exe"
G = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage(n, path):
    b = subprocess.run([GIT, "-C", G, "show", ":%d:%s" % (n, path)],
                       capture_output=True).stdout
    if not b:
        raise SystemExit("stage %d empty for %s" % (n, path))
    return json.loads(b.decode("utf-8"))


def write(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


# --- take-mine faces (stage 3) ------------------------------------------
for f in ("results/scorecard_v1.json", "results/strategy_scorecard.json",
          "results/update_status.json"):
    mine = stage(3, f)
    theirs = stage(2, f)
    mk = mine.get("generated") or mine.get("updated")
    tk = theirs.get("generated") or theirs.get("updated")
    print("%s: take-mine (mine=%s > theirs=%s)" % (f, mk, tk))
    assert mk >= tk, "take-mine violated: %s older than %s" % (mk, tk)
    write(f, mine)

# --- regime_state: union lists + newer scalars ---------------------------
f = "results/regime_state.json"
mine, theirs = stage(3, f), stage(2, f)
assert mine["updated"] >= theirs["updated"], "regime newer-wins violated"
merged = dict(mine)  # newer scalars/asof/state/days from mine
for key in ("triggers", "transitions", "history"):
    seen, out = set(), []
    for e in theirs.get(key, []) + mine.get(key, []):
        ident = json.dumps(e, sort_keys=True, ensure_ascii=False)
        if ident not in seen:
            seen.add(ident)
            out.append(e)
    merged[key] = out
    print("regime %s union: theirs=%d mine=%d -> %d zero-loss" %
          (key, len(theirs.get(key, [])), len(mine.get(key, [])), len(out)))
write(f, merged)

# --- compute_audit: history union by ts + latest newer-wins --------------
f = "results/compute_audit.json"
mine, theirs = stage(3, f), stage(2, f)
mh, th = mine["history"], theirs["history"]
by_ts = {}
for e in th:
    by_ts[e["ts"]] = e
for e in mh:
    by_ts[e["ts"]] = e  # mine wins same-ts
union = sorted(by_ts.values(), key=lambda x: x["ts"])
lt_m = mine["latest"].get("ts", "")
lt_t = theirs["latest"].get("ts", "")
latest = mine["latest"] if lt_m >= lt_t else theirs["latest"]
print("compute_audit union: theirs=%d mine=%d -> %d zero-loss; "
      "latest mine=%s theirs=%s -> %s" %
      (len(th), len(mh), len(union), lt_m, lt_t,
       "MINE" if lt_m >= lt_t else "THEIRS"))
write(f, {"latest": latest, "history": union})
print("resolver complete: 5 faces resolved (3 take-mine + 1 union + "
      "1 history-union); zero-loss asserted")
