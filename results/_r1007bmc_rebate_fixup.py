# r1007 resolver fixup: 3 remaining marker files via bytes-safe subprocess (GBK pipe pit)
import json, io, os, subprocess

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
GIT = r"C:\Program Files\Git\cmd\git.exe"

def stage_bytes(i, fp):
    r = subprocess.run([GIT, "show", ":%d:%s" % (i, fp)], cwd=ROOT,
                       capture_output=True, timeout=30)
    return r.stdout

def ts_of(d):
    for k in ("ts", "generated", "generated_at", "updated", "now", "epoch", "asof"):
        if d.get(k) is not None:
            return str(d.get(k))
    return ""

report = []

# small dict: regime_state.json newer-wins
p = "results/regime_state.json"
o = json.loads(stage_bytes(2, p).decode("utf-8", "replace"))
t = json.loads(stage_bytes(3, p).decode("utf-8", "replace"))
win = o if ts_of(o) >= ts_of(t) else t
io.open(os.path.join(ROOT, p), "w", encoding="utf-8", newline="").write(
    json.dumps(win, ensure_ascii=False, indent=1))
report.append((p, "newer-wins " + ("ours" if win is o else "theirs"), ts_of(win)))

# daily_report pair: JSON newer-wins, md follows same side
pj = "docs/daily_report/REPORT-2026-10-14.json"
pm = "docs/daily_report/REPORT-2026-10-14.md"
o = json.loads(stage_bytes(2, pj).decode("utf-8", "replace"))
t = json.loads(stage_bytes(3, pj).decode("utf-8", "replace"))
ours_newer = ts_of(o) >= ts_of(t)
side = 2 if ours_newer else 3
win = o if ours_newer else t
io.open(os.path.join(ROOT, pj), "w", encoding="utf-8", newline="").write(
    json.dumps(win, ensure_ascii=False, indent=1))
md = stage_bytes(side, pm).decode("utf-8", "replace")
io.open(os.path.join(ROOT, pm), "w", encoding="utf-8", newline="").write(md)
report.append((pj, "side%d newer-wins" % side, ts_of(win)))
report.append((pm, "follows JSON side%d" % side, "len=%d" % len(md)))

for r in report:
    print(r)
