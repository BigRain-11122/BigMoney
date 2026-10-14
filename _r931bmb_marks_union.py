# -*- coding: utf-8 -*-
# _r931bmb_marks_union.py -- r931 bm-b: union-merge UU append-only marks jsonl
# (r570 append-only jsonl union law; r995 bm-c shared-face union-merge precedent).
# ours (:2) = origin side rows, theirs (:3) = replayed r931 rows; union preserve
# first-seen order (origin rows first, then ours-only rows), byte-exact per row.
import subprocess

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
F = "results/paper/marks/marks-20261014.jsonl"


def rows(spec):
    r = subprocess.run(["git", "-C", ROOT, "show", spec],
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        return None
    txt = r.stdout.decode("utf-8", "replace")
    return [ln for ln in txt.split("\n") if ln.strip()]


def main():
    ours = rows(":2:%s" % F)
    theirs = rows(":3:%s" % F)
    if ours is None or theirs is None:
        print("ABORT: stage missing")
        return 1
    seen = set()
    merged = []
    dup_o = dup_t = 0
    for src in (ours, theirs):
        for ln in src:
            key = ln.strip()
            if key in seen:
                if src is ours:
                    dup_o += 1
                else:
                    dup_t += 1
                continue
            seen.add(key)
            merged.append(ln)
    print("ours=%d theirs=%d merged=%d dup_ours=%d dup_theirs=%d"
          % (len(ours), len(theirs), len(merged), dup_o, dup_t))
    if not merged:
        print("ABORT: empty union")
        return 1
    with open(ROOT + "\\" + F.replace("/", "\\"), "w", encoding="utf-8",
              newline="") as f:
        f.write("\n".join(merged) + "\n")
    r = subprocess.run(["git", "-C", ROOT, "add", F],
                       capture_output=True, timeout=30)
    if r.returncode != 0:
        print("ADD FAIL: %s" % r.stderr.decode("utf-8", "replace"))
        return 1
    print("union written+staged: %d rows" % len(merged))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
