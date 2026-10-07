"""r695 bm-c HANDOVER facts: unified-chain live head read (science_gates
ledger_head() from newest n1_w*_results.json), QA five-round pack family
existence, board/satengine summary snapshot for the 5x line."""
import glob
import json
import os
import re

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
facts = {}

# 1. newest perpetual_faces n1 results file -> ledger head
heads = []
for f in glob.glob(os.path.join(REPO, "results", "perpetual_faces",
                                "n1_w*_results.json")):
    m = re.search(r"n1_w(\d+)_results\.json$", f)
    if m:
        heads.append((int(m.group(1)), f))
heads.sort()
facts["n1_files_total"] = len(heads)
if heads:
    wnum, latest = heads[-1]
    facts["n1_latest_wave"] = wnum
    try:
        with open(latest, encoding="utf-8") as fh:
            data = json.load(fh)
        sg = data.get("science_gates") or {}
        lh = None
        if isinstance(sg, dict):
            lh = sg.get("ledger_head") or sg.get("ledger_total") or sg.get("trials_ledger")
        if lh is None:
            lh = (data.get("trials_ledger") or {}).get("total")
        facts["n1_latest_ledger_head"] = lh
        facts["n1_latest_mu"] = sg.get("merged_mu") or sg.get("mu")
    except Exception as e:
        facts["n1_latest_error"] = repr(e)[:200]

# 2. QA five-round pack family existence r691..r695
qa = {}
for r in range(691, 696):
    md = os.path.join(REPO, "qa", f"smoke-r{r}.md")
    png = os.path.join(REPO, "qa", f"equity-curve-r{r}.png")
    qa[f"r{r}"] = {"md": os.path.exists(md),
                   "png_bytes": os.path.getsize(png) if os.path.exists(png) else None}
facts["qa_family"] = qa

# 3. r691 round-report line head (5th from tail) for window summary
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rp, encoding="utf-8", errors="replace") as fh:
    lines = [ln for ln in fh.read().splitlines() if ln.strip()]
facts["r691_head"] = lines[-5][:400] if len(lines) >= 5 else None

out = os.path.join(REPO, "results", "_r695bmc_ho_facts.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print(json.dumps(facts, indent=1, ensure_ascii=False))
