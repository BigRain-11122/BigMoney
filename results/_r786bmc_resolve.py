# -*- coding: utf-8 -*-
"""r786 bm-c merge-conflict resolver (12 UU faces, mid-merge state).
Laws: CODELY.md append-only memory union (r315 stage-aware extraction + EOF
append + dedupe fail-closed; r417 line-start marker matching; r405 read
blobs from COMMIT OBJECTS :2:/:3: not index-after-add) / same-day idempotent
derive faces take-new-by-wallclock-ts (r505) / x2_watch_log.jsonl union with
ts-stable sort (r758) / post-resolve residual-marker line-start assert
(r417). Zero-loss assertions; receipt -> results/_r786bmc_resolve.json."""
import json
import os
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CNW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

CODELY = "CODELY.md"
TAKE_NEW = [
    "results/_attrition_guard_scan.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/t35_open_fill_verify.json",
]
UNION_JSONL = "results/x2_watch_log.jsonl"
TS_KEYS = ("ts", "generated_at", "generated", "updated_at", "updated",
           "scan_ts", "last_scan_ts")


def git(*args):
    p = subprocess.run(["git", "-C", ROOT] + list(args), capture_output=True,
                       creationflags=CNW)
    return p.returncode, p.stdout, p.stderr


def blob(stage, path):
    rc, out, _ = git("show", ":%d:%s" % (stage, path))
    assert rc == 0, "stage read failed %s" % path
    return out


def ts_of(obj):
    for k in TS_KEYS:
        v = obj.get(k) if isinstance(obj, dict) else None
        if isinstance(v, str) and v:
            return v
    return ""


def resolve_codely():
    work = open(os.path.join(ROOT, CODELY), encoding="utf-8").read()
    lines = work.splitlines(keepends=True)
    marks = [i for i, ln in enumerate(lines)
             if ln.startswith(("<<<<<<<", "|||||||", "=======", ">>>>>>>"))]
    assert len(marks) == 4, "expected one diff3 block, got %d markers" % len(marks)
    i0, i1, i2, i3 = marks
    pre = lines[:i0]
    ours = lines[i0 + 1:i1]
    theirs = lines[i2 + 1:i3]
    post = lines[i3 + 1:]
    # union: ours entry first (earlier ts 10-08 23:5x), then theirs (10-09 01:1x)
    merged = pre + ours + theirs + post
    out = "".join(merged)
    # residual marker assert: line-start only (r417)
    for ln in merged:
        assert not ln.startswith(("<<<<<<<", "|||||||", "=======", ">>>>>>>")), \
            "residual marker: %r" % ln[:40]
    with open(os.path.join(ROOT, CODELY), "w", encoding="utf-8",
              newline="") as fh:
        fh.write(out)
    return {"ours_lines": len(ours), "theirs_lines": len(theirs),
            "ours_head": ours[0][:60] if ours else "",
            "theirs_head": theirs[0][:60] if theirs else ""}


def resolve_take_new(path):
    o = json.loads(blob(2, path).decode("utf-8"))
    t = json.loads(blob(3, path).decode("utf-8"))
    to, tt = ts_of(o), ts_of(t)
    if to >= tt:
        side, obj = "ours", o
    else:
        side, obj = "theirs", t
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "w",
              encoding="utf-8", newline="") as fh:
        json.dump(obj, fh, indent=1, ensure_ascii=False)
        if not out_ends_nl(blob(2, path)):
            pass
    return {"side": side, "ours_ts": to, "theirs_ts": tt}


def out_ends_nl(b):
    return b.endswith(b"\n")


def resolve_union_jsonl(path):
    o_lines = blob(2, path).decode("utf-8").splitlines()
    t_lines = blob(3, path).decode("utf-8").splitlines()
    seen = set()
    union = []
    for ln in o_lines + t_lines:
        if ln not in seen:
            seen.add(ln)
            union.append(ln)

    def tskey(ln):
        m = re.search(r'"ts"\s*:\s*"([^"]+)"', ln)
        return m.group(1) if m else "9999"

    union.sort(key=tskey)
    with open(os.path.join(ROOT, path.replace("/", os.sep)), "w",
              encoding="utf-8", newline="") as fh:
        fh.write("\n".join(union) + ("\n" if union else ""))
    return {"ours_n": len(o_lines), "theirs_n": len(t_lines),
            "union_n": len(union),
            "dupes": len(o_lines) + len(t_lines) - len(union)}


def main():
    receipt = {"round": 786, "codely": resolve_codely(),
               "take_new": {}, "union_jsonl": None}
    for p in TAKE_NEW:
        receipt["take_new"][p] = resolve_take_new(p)
    receipt["union_jsonl"] = resolve_union_jsonl(UNION_JSONL)
    rc, out, err = git("add", CODELY, UNION_JSONL, *TAKE_NEW)
    assert rc == 0, err.decode("utf-8", "replace")
    rc, out, _ = git("ls-files", "-u")
    assert not out.strip(), "UU remain:\n%s" % out.decode("utf-8", "replace")
    with open(os.path.join(ROOT, "results", "_r786bmc_resolve.json"), "w",
              encoding="utf-8") as fh:
        json.dump(receipt, fh, indent=1, ensure_ascii=False)
    print(json.dumps(receipt, indent=1, ensure_ascii=False)[:1500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
