"""r671 post_review REPORT-face check + moneyflow panel state + N1 queue."""
import json, os, glob, subprocess
REPO = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
w = open(r"C:\Users\sjs20\AppData\Local\Temp\r671_p0.txt", "w", encoding="utf-8")

# 1) post_review REPORT face
reports = sorted(glob.glob(REPO + r"\results\post_review\REPORT-*.md"))
w.write(f"post_review reports: {len(reports)}\n")
if reports:
    latest = reports[-1]
    w.write(f"latest: {os.path.basename(latest)}\n")
    txt = open(latest, encoding="utf-8", errors="replace").read()
    for line in txt.splitlines():
        if any(k in line for k in ("判定分布", "✗", "verdict")):
            w.write(line[:180] + "\n")

# 2) moneyflow panel state
for p in (r"\data\moneyflow", r"\results\moneyflow_panel"):
    d = REPO + p
    if os.path.isdir(d):
        fs = glob.glob(d + r"\*.json") + glob.glob(d + r"\*.csv")
        w.write(f"\nmoneyflow dir {p}: {len(fs)} files\n")
        for f in fs[:5]:
            w.write("  " + os.path.basename(f) + "\n")

# 3) N1 engine queue (saturation engine local)
try:
    g = subprocess.run(["git", "-C", REPO, "show", "origin/main:results/saturation_engine/state_bm-a.json"], capture_output=True)
    st = json.loads(g.stdout)
    w.write("\n== sat engine state_bm-a ==\n")
    for k in ("last_verdict", "last_tick", "queue_len"):
        w.write(f"{k}: {st.get(k,'?')}\n")
    q = st.get("queue", st.get("n1_queue", []))
    w.write(f"queue entries: {len(q) if isinstance(q,(list,dict)) else q}\n")
    if isinstance(q, list):
        for e in q[:8]:
            w.write("  " + json.dumps(e, ensure_ascii=False)[:150] + "\n")
except Exception as e:
    w.write(f"sat state fail: {e}\n")
w.close()
print("written")
