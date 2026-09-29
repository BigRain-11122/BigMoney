import json, time, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

path = "state.json"
s = json.load(open(path, encoding="utf-8"))
now = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")

s["machine_id"] = "bm-b"
s["round_no"] = 443
s["note"] = (
    "r443: W11 chain advance single round -- GENERATE heritage adopted (w11_candidates n=1262, grammar sha16 "
    "128962592feeb8d3 == FROZEN pin, r240 adopt-verify-close; dead-tick 23:44-00:00 window same as bm-a r450 "
    "adoption face) -> 31-UU pull-rebase canonical resolve per bigmoney-conflict-resolve (fork-point r444 "
    "--onto explicit replay: origin advanced cb4734950->eab3a15f3 mid-window, abort+replay zero loss; "
    "compute_audit union 201+201->203, x2_watch newline-loss repair 1800->1814 objects zero loss incl. origin "
    "glued line) -> SCREEN burned 1462/1462 pid14156 10min wall -> screen-finalize: null p95 0.5148 IN "
    "[0.50,0.52], survivors 229/1262=18.15%, RESEARCH FACT STD-axis enrichment std10_hi 24.66% > none 17.59% "
    "> std20_hi 12.59% (first STD screen face, positive 10d/negative 20d asymmetry), MOM continuation 1.25x "
    "weaker than W10 1.88x, ledger 350018 linear -> judge-prep PASS (STD meta 1511 decidable) -> JUDGE armed+"
    "ignited pid16392 01:04:15 (host_gates 5383 parquet verified; claim 01:00 push-reject yield self-healed "
    "01:04 second tick) -> ETA finalize ~01:35. S6 37 legs rc0 except update_lhb rc3 source-restatement "
    "quarantine (r229 3rd observation). MSG slot-4 berth processed: bm-b declines adopt this round (W11 lane "
    "full-load), bm-c continues per its note. NEXT: judge-finalize harvest -> intake (D6) -> CEO-REPORT-WAVE11 "
    "(48h clock at judge landing); W12 prereg reference-band feed (null p95 0.5148). WATERMARK GREEN"
)
s["last_round_at"] = now
s["last_round_ts"] = "r443"
s["ts"] = now
s["updated"] = now

with open(path, "w", encoding="utf-8") as f:
    json.dump(s, f, ensure_ascii=False, indent=1)
print("state.json -> round_no", s["round_no"], "|", now)
