# -*- coding: utf-8 -*-
"""R277 bm-a: register FUSION-P1-NAV ready entry in results/runnable_pool.json
(T-85 s1 NAV harvest batch; O-20260926-2320 24h saturation supply line).
Byte-face safe append per R255/R257 laws; autofill C8 fires it next tick.
"""
import json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POOL = ROOT / "results" / "runnable_pool.json"
NOW = time.strftime("%Y-%m-%d %H:%M:%S")

ENTRY = {
 "id": "FUSION-P1-NAV",
 "ticket_ref": "T-2026-09-26-85 s1 (CEO order O-20260926-2320 24h saturation; claimed bm-a R277 commit aea185e3)",
 "prereg_ref": "s1 NAV harvest = derivation face, ledger +0 (anchor-replay t24 precedent); prereg freeze due BEFORE s2/s3 fusion-grid judged runs (R99 law); member specs pinned to results/t56_caliber_registry snapshot (r256 A1 law, manifest dual-gate verified)",
 "runner": "scripts/fusion_p1_nav.py",
 "runner_args": ["run"],
 "lane_owner": None,
 "priority": 1,
 "status": "ready",
 "entered_at": NOW,
 "data_gates": "in-runner fail-closed exit 2: caliber manifest dual-gate hash verify (R253 raw+LF law, bare-name keys under firm/traders) + per-member hard anchors (CE backtest-block via p3.anchor_checks ANCHOR_TOL / PROSPECT prospect.recorded_* / overlay x2 vs frozen stress_x2 of results/exit_overlay_p1.json) + census gate (lines == 28x2 + wired_overlayx2, wired set = stress_x2 recorded combos zero-invention) + atomic tmp+rename + idempotent complete-census no-op (FUSION_P1_NAV_REFINALIZE=1 = only redo); selftest 15/15 pre-pooling (r263 law)",
 "workers_plan": {
  "workers": "min(worker_cap(), 12) ProcessPool via parallel_runner.run_cells_parallel (O-2130 compliant)",
  "priority": "BelowNormal",
  "note": "autofill sets BelowNormal on launch; 32 jobs (28 base-member jobs x2 cost faces inside + 4 wired-overlay jobs x2 inside); est minutes-class wall (56-sleeve battery precedent ~9s on bm-a class); deterministic idempotent"
 },
 "shards": [
  {
   "key": "fusion-nav-0of1",
   "status": "ready",
   "owner": None,
   "checkpoint": "results/fusion_p1/navs.jsonl atomic complete census (64 lines) = landed marker; harvest round flips entry+shard done per r244 landed-marker law",
   "note": "single shard, internal ProcessPool parallelism; results/fusion_p1/navs_summary.json carries evidence_cutoff + anchors + audit.workers"
  }
 ],
 "note": "R277 supply-line discharge of pool_starvation red card (v2.3 any-day law first live fire, span 251min): first real batch of the O-2320 three-ticket quenching line; s2 fusion grid + s3 gates owe their own frozen prereg BEFORE any judged run (R99); B_MAXDIV enters as benchmark only (T-27 veto window until 10-01 zero wiring)."
}

def main():
    raw = POOL.read_bytes()
    bom = raw.startswith(b"\xef\xbb\xbf")
    eol = b"\r\n" if b"\r\n" in raw else b"\n"
    txt = raw.decode("utf-8-sig" if bom else "utf-8")
    non_ascii = any(ord(c) > 127 for c in txt)
    indent = 1
    for ln in txt.splitlines():
        if ln.startswith(" "):
            indent = len(ln) - len(ln.lstrip(" "))
            break
    tnl = raw.endswith(b"\n")
    d = json.loads(txt)
    entries = d.get("entries") or []
    assert not any(e.get("id") == "FUSION-P1-NAV" for e in entries), "already registered"
    entries.append(ENTRY)
    d["entries"] = entries
    out = json.dumps(d, ensure_ascii=not non_ascii, indent=indent)
    if tnl:
        out += "\n"
    data = out.encode("utf-8")
    if bom:
        data = b"\xef\xbb\xbf" + data
    if eol == b"\r\n":
        data = data.replace(b"\n", b"\r\n")
    POOL.write_bytes(data)
    ready = [e.get("id") for e in entries if e.get("status") == "ready"]
    print(f"pool entries={len(entries)} ready={ready} (bom={bom} eol={eol!r} indent={indent} tnl={tnl})")

if __name__ == "__main__":
    main()
