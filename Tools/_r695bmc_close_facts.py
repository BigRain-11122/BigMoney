"""r695 bm-c mid-close facts probe: (1) last round-report lines r691-694
summaries (for the 5x HANDOVER increment window), (2) QA runner terminal
state + product files, (3) O-2115 acceptance pack latest state,
(4) py_watermark last verdict, (5) attrition guard scan pre-state.
Facts JSON -> results/_r695bmc_close_facts.json."""
import json
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
facts = {}

# 1. round report tail
rp = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")
with open(rp, encoding="utf-8", errors="replace") as fh:
    lines = [ln for ln in fh.read().splitlines() if ln.strip()]
facts["rr_total_lines"] = len(lines)
tail = []
for ln in lines[-4:]:
    tail.append(ln[:420])
facts["rr_tail_heads"] = tail

# 2. QA runner terminal state
qo = os.path.join(REPO, "results", "_r695bmc_qa_runner.out")
qe = os.path.join(REPO, "results", "_r695bmc_qa_runner.err")
if os.path.exists(qo):
    txt = open(qo, encoding="utf-8", errors="replace").read()
    facts["qa_out_tail"] = txt.strip().splitlines()[-8:]
else:
    facts["qa_out_tail"] = None
facts["qa_err_tail"] = (open(qe, encoding="utf-8", errors="replace").read()
                        .strip().splitlines()[-5:]
                        if os.path.exists(qe) else None)

qa_md = os.path.join(REPO, "qa", "smoke-r695.md")
qa_png = os.path.join(REPO, "qa", "equity-curve-r695.png")
facts["qa_md_exists"] = os.path.exists(qa_md)
facts["qa_png_bytes"] = os.path.getsize(qa_png) if os.path.exists(qa_png) else None
if facts["qa_md_exists"]:
    md = open(qa_md, encoding="utf-8", errors="replace").read()
    facts["qa_md_head"] = md.strip().splitlines()[:4]
    facts["qa_md_pass_count"] = md.count("[PASS]")
    facts["qa_md_fail_count"] = md.count("[FAIL]")

# 3. O-2115 pack latest
pk = os.path.join(REPO, "results", "o2115_acceptance", "pack_latest.json")
if os.path.exists(pk):
    with open(pk, encoding="utf-8") as fh:
        pack = json.load(fh)
    facts["o2115_keys"] = sorted(pack.keys())[:12]
    facts["o2115_generated"] = pack.get("generated_at") or pack.get("ts")
    ver = pack.get("overall") or pack.get("verdict") or pack.get("status")
    facts["o2115_overall"] = ver
else:
    facts["o2115_generated"] = None

# 4. py_watermark last line
pw = os.path.join(REPO, "results", "watermark.jsonl")
if os.path.exists(pw):
    last = open(pw, encoding="utf-8", errors="replace").read().strip().splitlines()[-1]
    try:
        w = json.loads(last)
        facts["wm_last"] = {k: w.get(k) for k in
                            ("ts", "machine", "verdict", "cpu_total_pct", "py_cpu_pct")}
    except Exception:
        facts["wm_last"] = {"parse_error": True}

# 5. NULLS burn line count (bm-b watch)
nz = os.path.join(REPO, "results", "fund_divlowvol_p1", "nulls.jsonl")
if os.path.exists(nz):
    n = sum(1 for _ in open(nz, encoding="utf-8", errors="replace"))
    mt = os.path.getmtime(nz)
    import datetime
    facts["nulls_burn"] = {"lines": n,
                           "mtime": datetime.datetime.fromtimestamp(mt).isoformat()}

out = os.path.join(REPO, "results", "_r695bmc_close_facts.json")
with open(out, "w", encoding="utf-8") as fh:
    json.dump(facts, fh, indent=1, ensure_ascii=False)
print(json.dumps(facts, indent=1, ensure_ascii=False))
