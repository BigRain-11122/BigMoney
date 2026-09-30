"""r476 bm-b: submit EXCLUSION-MARGINAL-P1-RUN to runnable_pool (double-file:
shared results/runnable_pool.json + lane results/runnable_pool.bm-b.json,
W14/T104 double-file precedent). Idempotent: skips if entry id already present."""
import io
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"

ENTRY = {
    "id": "EXCLUSION-MARGINAL-P1-RUN",
    "ticket_ref": "D-20260930-41 deliverable #3 / RETAIL_QUANT_TRACK sec.2 #3 (bm-b berth, F-04 MSG-20260930-1935; r475 freeze commit 3e4630648)",
    "prereg_ref": "research/EXCLUSION_MARGINAL_PREREG.md (frozen r475 pre-burn R99; 16 cells FULL/NONE/6LOO/6AOI/RANDx2 measurement scan, zero registration face; trial gate +16 -> 318/500 cumulative; M1 marginal verdicts frozen sec.4)",
    "runner": "scripts/exclusion_marginal_scan.py",
    "runner_args": ["run"],
    "lane_owner": "bm-b",
    "priority": 0,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "entered_by": "bm-b (OS iteration loop r476)",
    "data_gates": "in-runner FAIL-CLOSED: probe same-face assertions (paths+counts bit-pinned) + panel complete&cutoff>=2026-09-22 + eligibility snapshot<24h + closed_family open + seed-registry law (exclusion_marginal_rand=20329000 registered r476) + cost_spec.verify + ADV-cap mirror; idempotency: existing scan.json = no-op exit 0 (EXCLUSION_MARGINAL_REBURN=1 redo channel); selftest 16/16 hermetic incl. hand-value cost legs (r474 law); trials_ledger appended BEFORE json.dump embed (r474 embed-order law); gate_attrition.bm-b.json +1 measurement row append-only",
    "shards": [
        {
            "key": "exclusion-0of1",
            "status": "ready",
            "owner": "bm-b",
            "owner_since": time.strftime("%Y-%m-%d %H:%M:%S"),
            "checkpoint": "results/exclusion_marginal_scan/scan.json single-shot (idempotency guard; no partial-state resume face by design -- 16-cell burn is one deterministic pass)",
            "note": "r476 bm-b: engine leg landed (monthly rotation event-walk: resume-day exits realize on resume day = no liquidity look-ahead, suspension entry-skip, overlap hold, ADV20 1% fill cap, 100-share lots, min-comm 5, V2 stock cost via knowledge/rules primitives imported never rewritten); gates probe on real data ALL PASS (panel 5217/elig 5229/cutoff 2026-09-29/age 8.2h/family open); timing probe 150 files 1.5s -> full load ~52s, whole burn est 5-15min (prereg sec.0 upper budget 20-40min stands); burn via pool per O-2100 (>5min law); after burn = next round backfills prereg sec.7 + carrier EXCLUSION_MARGINAL.md marginal table + TRACK sec.2 #3 row flip",
        }
    ],
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": "prereg sec.0 frozen pool routing; serial deterministic single pass (T33/GRID-P1 light-batch precedent); holiday full-core amendment (O-20260930-1858) applies from 2026-10-01 -- this entry stays default-priority per current law",
    },
    "worker_class": "bm-hosted",
}


def submit(path: str) -> str:
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    if any(e.get("id") == ENTRY["id"] for e in d["entries"]):
        return f"SKIP (already present): {path}"
    d["entries"].append(ENTRY)
    d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return f"APPENDED -> {path}"


print(submit(io.open and r"{}\results\runnable_pool.json".format(ROOT)))
print(submit(r"{}\results\runnable_pool.bm-b.json".format(ROOT)))
