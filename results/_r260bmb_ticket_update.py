import json

P = "fleet/tasks/T-2026-09-26-76-P1.json"
d = json.load(open(P, encoding="utf-8-sig"))
assert "progress_r260" not in d
d["progress_r260"] = (
    "R260 bm-b face (e) DELIVERED same-round (arXiv standing academic channel first sweep, "
    "R153 recipe): scripts/arxiv_sweep.py standing weekly tool (export.arxiv.org/api/query "
    "category face q-fin.PM+q-fin.STR, 7d submittedDate window, serial 3s pacing R109, direct "
    "urllib+ProxyHandler({}), certifi CA fix + 60s timeout/1-retry cold-query face, "
    "idempotent-by-day, atomic write, exit 2 honest fetch-fail, selftest offline Atom fixture "
    "PASS) + machine face results/harvest/arxiv_sweep_20260926.json (window 2026-09-19..09-26: "
    "PM 4 / STR 0 slow-week honest) + digest research/digests/DIGEST-20260926-wave10-arxiv-sweep.md: "
    "triage 4 entries = #1 2609.27051 anytime-valid frozen referee for LLM factor-mining agents = "
    "A-lead methodology family (dialogues our frozen-gate architecture prereg/science_gates/C-arm "
    "blind-eval; consumption route = science_gates methodology face post deep-read, UNVERIFIED "
    "until then per leverage law) + #2 2609.27113 SPT concentrated-equity EW-vs-cap regime "
    "dependence = B-lead economic prior for EW6/alloc family + #3 2609.29887 cost-sensitive "
    "online window-size aggregation = C-watch (blend/clock lookback face) + #4 IVC-BSDE = "
    "D-pass (no daily-bar face); funnel harvest 4 / gate-pass 0 (material-level registration "
    "only, gate chain untouched, EW6_PORTFOLIO frozen file zero-touch); zero new families "
    "(all three leads = existing-family reinforcement). Faces (a) jisilu/hibor/guorn + jin-gong "
    "verify = date-gated 09-28 open window; faces (c) QuantsPlaybook second-sweep + (d) "
    "judgment-consumption remain open single-writer faces per shard protocol."
)
# four-face mirror: no BOM, CRLF, indent=1, ASCII-only (verified vs HEAD blob)
with open(P, "w", encoding="utf-8", newline="\r\n") as f:
    json.dump(d, f, ensure_ascii=True, indent=1)
    f.write("\n")
print("written")
