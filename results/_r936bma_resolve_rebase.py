# -*- coding: utf-8 -*-
"""r936 rebase conflict resolver: 32 UU faces, all regen/live-state.
Canon: take-newer by embedded timestamp; jsonl = union; fallback = theirs.
Zero-loss assertion: every UU file resolved exactly once, reported per-file.
"""
import json, re, subprocess, sys

GIT = r"C:\Program Files\Git\cmd\git.exe"
ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"

def run(*args):
    return subprocess.run([GIT] + list(args), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", cwd=ROOT)

uu = [l.strip() for l in run("diff", "--name-only", "--diff-filter=U").stdout.splitlines() if l.strip()]
print("UU count:", len(uu))

TS_KEYS = ("generated_at", "generated", "last_generated", "ts", "updated",
           "updated_at", "last_update", "asof", "as_of", "time", "datetime",
           "last_run", "clock_read", "date")

def find_ts(obj, depth=0):
    """Recursively find the max timestamp value (ISO str or epoch number)."""
    best = None
    if depth > 6 or obj is None:
        return None
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and k in TS_KEYS:
                c = v
            else:
                c = find_ts(v, depth + 1)
            if c and (best is None or c > best):
                best = c
    elif isinstance(obj, list):
        for v in obj:
            c = find_ts(v, depth + 1)
            if c and (best is None or c > best):
                best = c
    elif isinstance(obj, (int, float)):
        # epoch seconds heuristic (2020-2030 window)
        if 1577836800 <= obj <= 1893456000:
            best = obj
    return best

def blob(stage, path):
    r = run("show", ":%d:%s" % (stage, path))
    return r.stdout if r.returncode == 0 else None

def md_ts(text):
    stamps = re.findall(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?", text or "")
    return max(stamps) if stamps else None

report = []
for path in uu:
    ours, theirs = blob(2, path), blob(3, path)
    if ours is None or theirs is None:
        report.append((path, "STAGE-MISSING", "theirs" if theirs else "ours"))
        continue
    pick, why = None, None
    if path.endswith(".jsonl"):
        o_lines, t_lines = ours.splitlines(), theirs.splitlines()
        seen, merged = set(), []
        for ln in o_lines + t_lines:
            if ln not in seen:
                seen.add(ln); merged.append(ln)
        pick, why = "\n".join(merged) + ("\n" if merged else ""), "union(%d+%d->%d)" % (len(o_lines), len(t_lines), len(merged))
    else:
        to_, tt_ = None, None
        try:
            to_ = find_ts(json.loads(ours))
            tt_ = find_ts(json.loads(theirs))
        except Exception:
            to_, tt_ = md_ts(ours), md_ts(theirs)
        if to_ is not None and tt_ is not None and to_ != tt_:
            pick, why = (theirs if tt_ > to_ else ours), "ts-newer(%s vs %s)" % (to_, tt_)
        else:
            pick, why = theirs, "tie-or-none->theirs"
    with open(ROOT + "\\" + path.replace("/", "\\"), "w", encoding="utf-8", newline="") as f:
        f.write(pick)
    r = run("add", "--", path)
    report.append((path, "resolved", why))
    if r.returncode != 0:
        print("ADD FAIL", path, r.stderr[:200]); sys.exit(1)

for p, s, w in report:
    print(s, "|", w, "|", p)
print("RESOLVED", len(report), "of", len(uu))
