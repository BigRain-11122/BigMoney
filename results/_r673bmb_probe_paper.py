import subprocess, json, io

OUT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r673bmb_probe_paper.txt"
lines = []

def show(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)], capture_output=True)
    return r.stdout

PAPER = [
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
]

def last_date_walk(o, best=[None]):
    # find max ISO date string anywhere
    import re
    if isinstance(o, dict):
        for v in o.values():
            last_date_walk(v, best)
    elif isinstance(o, list):
        for v in o:
            last_date_walk(v, best)
    elif isinstance(o, str):
        m = re.match(r"^(\d{4}-\d{2}-\d{2})", o)
        if m and (best[0] is None or m.group(1) > best[0]):
            best[0] = m.group(1)

for f in PAPER:
    ob = show("HEAD", f)
    tb = show("MERGE_HEAD", f)
    if ob == tb:
        lines.append("IDENTICAL %s" % f)
        continue
    try:
        jo = json.loads(ob.decode("utf-8")); jt = json.loads(tb.decode("utf-8"))
        bo = [None]; last_date_walk(jo, bo); bt = [None]; last_date_walk(jt, bt)
        # count leaf values as proxy for data volume
        def cnt(o):
            if isinstance(o, dict): return sum(cnt(v) for v in o.values())
            if isinstance(o, list): return sum(cnt(v) for v in o) + 1
            return 1
        lines.append("%s ours: lastdate=%s leaves=%d bytes=%d | theirs: lastdate=%s leaves=%d bytes=%d" % (
            f, bo[0], cnt(jo), len(ob), bt[0], cnt(jt), len(tb)))
        # key-level diff summary (top level)
        ko = set(jo.keys()) if isinstance(jo, dict) else set()
        kt = set(jt.keys()) if isinstance(jt, dict) else set()
        if ko != kt:
            lines.append("  topkeys ours-only=%s theirs-only=%s" % (sorted(ko-kt)[:6], sorted(kt-ko)[:6]))
    except Exception as e:
        lines.append("%s PARSE-FAIL %s bytes ours=%d theirs=%d" % (f, e, len(ob), len(tb)))

with io.open(OUT, "w", encoding="utf-8") as fh:
    fh.write("\n".join(lines))
print("probe done")
