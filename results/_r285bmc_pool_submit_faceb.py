"""r285 bm-c: submit CROSS-START-ROBUSTNESS-P1-FACEB-RUN to runnable_pool
(double-file: shared results/runnable_pool.json + owner-lane
results/runnable_pool.bm-b.json, W14/T104/r476 double-file precedent).
Idempotent: skips if entry id already present. Data locality: the astock
per-code panel is gitignored and physically bm-b-only -> lane_owner=bm-b +
host gate (autofill MSG-1142 claim-before-check); science berth stays
bm-c (prereg + driver), burn host = bm-b, artifacts land in git."""
import io
import json
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"

ENTRY = {
    "id": "CROSS-START-ROBUSTNESS-P1-FACEB-RUN",
    "ticket_ref": "D-20260930-41 deliverable #1 face B / RETAIL_QUANT_TRACK sec.2 #1 (bm-c berth, F-04 MSG-20260930-1947; prereg frozen r284 commit e6f06a3e5 + r285 sec.3-B/sec.5-B pre-burn amendments)",
    "prereg_ref": "research/CROSS_START_ROBUSTNESS.md sec.3-B/5-B (burn window OPENED by bm-b engine landing r476 commit 25b13a8a5 per MSG-1947 sec.2; B-FULL raw baseline + B-RAND seeded null, 16 Jan-firsts 2007..2022, trial gate +2 -> 308/500 cumulative)",
    "runner": "scripts/cross_start_robustness.py",
    "runner_args": ["run_face_b"],
    "lane_owner": "bm-b",
    "priority": 0,
    "status": "ready",
    "entered_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    "entered_by": "bm-c (OS iteration loop r285)",
    "host_gates": [
        {"kind": "dir_nonempty", "path": "data/astock_daily/per"},
    ],
    "data_gates": "in-runner FAIL-CLOSED (_face_b_gates): engine probe same-face assertions (paths+counts) + panel host face + panel complete&cutoff>=2026-09-22 + eligibility snapshot<24h + BOTH closed families open (cross-start-robustness / exclusion_marginal_p1) + BOTH seed keys registered (cross_start_robustness_p1=20329000 band +100 B-RAND offset / exclusion_marginal_rand=20329500) + cost_spec.verify + ADV-cap mirror; idempotency: existing results/cross_start_robustness/face_b.json = FAIL-CLOSED no-op (FACE_B_REBURN=1 redo channel); selftest 19/19 hermetic (13 Face A + 6 Face B legs incl seeded-null determinism + calendar-bounds filter); trials_ledger appended BEFORE json.dump embed (r474 embed-order law); NO gate_attrition row (adjudication batch, Face A precedent zero-rejection face)",
    "shards": [
        {
            "key": "faceb-0of1",
            "status": "ready",
            "owner": None,
            "owner_since": None,
            "checkpoint": "results/cross_start_robustness/face_b.json single-shot (idempotency guard; one deterministic pass, no partial-state resume face by design)",
            "note": "r285 bm-c: engine = 100% import from bm-b exclusion_marginal_scan (r476) -- _sim_cell/_metrics/_build_selection/_signal_schedule/_load_calendar/_side_cost/_ffill_np, zero rewrite (MSG-1947 sec.2 anti-dup); assembly mirrors ems.run() with ONE disclosed deviation: pre-calendar-face (<2005-02-23) panel rows filtered before mapping (both cells run all-rules-OFF, barcnt/stale unconsumed, signal-date amt20 identical; ems.run() original FAIL-CLOSEDs on pre-2005 listings -- engineering fact in MSG-20260930-2115, bm-b berth fork); est burn 2-4min on bm-b (panel load ~52s + 34 event-walk sims), workers:1 serial deterministic single pass (T33/GRID-P1 light-batch precedent); after burn = consumer backfill by bm-c next round: prereg sec.7/8 + SUMMARY + TRACK sec.2 #1 flip + sec.4 consumption 306->308",
        }
    ],
    "workers_plan": {
        "workers": 1,
        "priority": "BelowNormal",
        "note": "serial deterministic single pass (event-walk engine, T33/GRID-P1 light-batch precedent; runner self-applies BELOW_NORMAL via ctypes per O-20260929-1029 headroom law); holiday full-core amendment (O-20260930-1858) applies from 2026-10-01 -- this entry stays default-priority per current law",
    },
    "worker_class": "bm-hosted",
}


def submit(path: str) -> str:
    with io.open(path, encoding="utf-8") as f:
        d = json.load(f)
    if any(e.get("id") == ENTRY["id"] for e in d.get("entries", [])):
        return f"SKIP (already present): {path}"
    d["entries"].append(ENTRY)
    d["updated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    return f"APPENDED -> {path}"


print(submit(r"{}\results\runnable_pool.json".format(ROOT)))
print(submit(r"{}\results\runnable_pool.bm-b.json".format(ROOT)))
