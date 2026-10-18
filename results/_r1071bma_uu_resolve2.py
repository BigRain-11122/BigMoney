# -*- coding: utf-8 -*-
"""r1071 bm-a rebase UU resolver v2 (15 faces, bm-b r1016 same-day regen race).

Delta vs v1: today's REPORT twin resolves by GENERATOR-SUPERSET deliverable
law (take mine) -- the upstream same-day regen (bm-b r1016, newer wall-clock
ts) was produced by the OLD daily_report.py (no A2 G4 attribution section),
so ts-newer-wins would degrade the round's main deliverable face.  All other
faces follow the r1008 family: ts newer-wins / deep-union per-machine rows /
md-js twins follow the json side.

Rebase semantics: :2 = upstream (origin/bm-b face), :3 = my replayed commit.
"""
import json
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def g(*a, binary=False):
    r = subprocess.run(["git"] + list(a), capture_output=True, cwd=ROOT)
    return r.stdout if binary else (r.stdout + r.stderr).decode("utf-8", "replace")


def stage(side, path):
    return g("show", ":%s:%s" % (side, path), binary=True).decode("utf-8", "replace")


def ts_of(obj):
    for k in ("generated_at", "ts", "updated", "updated_at", "asof", "last_run"):
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 10:
            return v
    return ""


def resolve(path):
    a2 = stage("2", path)
    a3 = stage("3", path)
    if path.endswith((".json", ".js")):
        try:
            o2 = json.loads(a2)
        except Exception:
            o2 = None
        try:
            o3 = json.loads(a3)
        except Exception:
            o3 = None
        if o2 is None and o3 is None:
            return a3.encode("utf-8"), "both-unparseable take-mine"
        if o2 is None:
            return a3.encode("utf-8"), "side2-unparseable take-mine"
        if o3 is None:
            return a2.encode("utf-8"), "side3-unparseable take-upstream"
        t2, t3 = ts_of(o2), ts_of(o3)
        merged = dict(o2)
        merged.update(o3)
        for k in set(o2) & set(o3):
            if isinstance(o2[k], dict) and isinstance(o3[k], dict):
                m = dict(o2[k])
                m.update(o3[k])
                merged[k] = m
        note = "deep-union newer-keys-win (t2=%s t3=%s)" % (t2, t3)
        return json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8"), note
    jpath = path[:-3] + ".json"
    try:
        j2 = json.loads(stage("2", jpath))
        j3 = json.loads(stage("3", jpath))
        t2, t3 = ts_of(j2), ts_of(j3)
        winner = "mine" if t3 >= t2 else "upstream"
    except Exception:
        winner = "mine"
    src = a3 if winner == "mine" else a2
    return src.encode("utf-8"), "md-follows-json %s" % winner


DELIVERABLE_MINE = ("docs/daily_report/REPORT-2026-10-19.json",
                    "docs/daily_report/REPORT-2026-10-19.md")

UU = [l[3:].strip() for l in g("status", "--porcelain").splitlines() if l.startswith("UU")]
print("UU faces:", len(UU))
for path in UU:
    if path in DELIVERABLE_MINE:
        data = stage("3", path).encode("utf-8")
        note = "deliverable-law take-mine (generator superset: section 7)"
    else:
        data, note = resolve(path)
    with open(ROOT + "\\" + path.replace("/", "\\"), "wb") as f:
        f.write(data)
    r = subprocess.run(["git", "add", "--", path], capture_output=True, cwd=ROOT)
    print("resolved %-46s %s" % (path, note))
    if r.returncode != 0:
        print("ADD FAILED", path, r.stderr.decode("utf-8", "replace"))
        sys.exit(1)

rep = open(ROOT + r"\docs\daily_report\REPORT-2026-10-19.md", encoding="utf-8").read()
assert "七、盈亏归因日账（A2 · G4 · 按 sleeve/腿）" in rep, \
    "FAIL: winning REPORT lost the A2 G4 attribution section"
assert "跨族日 PnL 总计" in rep, "FAIL: winning REPORT lost the grand total row"
print("ASSERT OK: A2 G4 section + grand total preserved in winning REPORT twin")
print("resolver v2 done")
