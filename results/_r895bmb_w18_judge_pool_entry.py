# -*- coding: utf-8 -*-
"""r895 bm-b: TRIAL-LABOR-W18-JUDGE pool entry registration (47 blocks/188 cells).

Two-leg lawful path per pit-pool-edit r859:
  leg-1  Tools/autofill.py submit -> full contract gates (duplicate id,
         O-2355 multicore, consumer_plan, D-20260929-02 inbox rival-freeze
         with fresh fetch). Its pool/lane write face is then ROLLED BACK.
  leg-2  host-formula surgical append: runnable_pool.json is byte-reproducible
         as json.dumps(pool, ensure_ascii=False, indent=1) with LF->CRLF
         (roundtrip probe PASSED this window, r678 law), so append + rewrite
         with the exact formula; parse-gate BEFORE write (r859 iron law);
         diff --numstat surgical assertion; lane mirror landed via autofill's
         own _write_lane_file (D-20260928-03(1)).

Precedent: W13-JUDGE (188 cells) / W17-JUDGE (344 cells) single-shard.
Data locality: D-leg deep panel asserted per claiming machine via data_deps
(r316 law -> D-20261004-02(1) gate); lane_owner=ANY (cache-less machines
skip data_not_local honestly).
"""
import json, os, subprocess, sys, io

ROOT = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
TOOLS = os.path.join(ROOT, "Tools")
EID = "TRIAL-LABOR-W18-JUDGE"

def snapshot(p):
    return open(p, "rb").read()

def restore(p, b):
    open(p, "wb").write(b)

def host_bytes(pool):
    return json.dumps(pool, ensure_ascii=False, indent=1).replace("\n", "\r\n").encode("utf-8")

def main():
    lane_path = None
    sys.path.insert(0, TOOLS)
    os.chdir(ROOT)

    # ---- pre-checks (mirror submit gates we can assert locally) ----
    js = json.load(open(os.path.join(ROOT, "results", "trial_labor_w18", "judge_state.json"),
                        encoding="utf-8"))
    assert js["n_blocks"] == 47 and len(js["judged_cells"]) == 188, \
        f"judge_state mismatch: blocks={js['n_blocks']} cells={len(js['judged_cells'])}"
    for dep in ("results/trial_labor_w18/judge_state.json",
                "results/trial_labor_w18/w18_cells.json",
                "results/trial_labor_w18/prep_state.json",
                "scripts/trial_labor_w18.py"):
        assert os.path.exists(os.path.join(ROOT, dep)), f"dep absent: {dep}"
    dp = os.path.join(ROOT, "Money02", "data", "cache", "t18_deep_panel", "ohlcv")
    n_pq = len([f for f in os.listdir(dp) if f.endswith(".parquet")]) if os.path.isdir(dp) else 0
    assert n_pq == 48, f"deep panel parquets={n_pq} != 48"
    src = open(os.path.join(ROOT, "scripts", "trial_labor_w18.py"), encoding="utf-8").read()
    assert "AUTOFILL-PARK" in src and '_worker_claim("TRIAL-LABOR-W18-JUDGE"' in src, \
        "runner missing park marker or claim handshake"
    print(f"pre-checks OK: 47 blocks / 188 cells / deep panel {n_pq} parquets")

    # ---- leg-1: autofill submit (contract gates + inbox rival-freeze) ----
    shared0 = snapshot(POOL)
    lane_tool = None
    import autofill  # for _write_lane_file + _lane_path_for
    lane_tool = autofill
    lane_path = autofill._lane_path_for(POOL) if hasattr(autofill, "_lane_path_for") \
        else POOL.replace(".json", ".bm-b.json")
    lane0 = snapshot(lane_path) if os.path.exists(lane_path) else None

    cmd = [sys.executable, os.path.join(TOOLS, "autofill.py"), "submit",
           "--id", EID,
           "--runner", "scripts/trial_labor_w18.py",
           "--runner-args", "judge 0 1",
           "--shards", "w18-judge-0of1",
           "--workers", "8",
           "--lane-owner", "ANY",
           "--priority", "1",
           "--ticket-ref",
           "T-2026-10-11-185 wave ticket lineage (W8=T-120/W9=T-121/W10=T-122/W11=T-123/W12=T-124/"
           "W13=T-125/W14=T-128/W16=T-172/W17=T-178); W18 sizing-axis 4-arm paired isolation; "
           "judge-prep landed r892 bm-b (47 blocks / 188 judged cells; screen-finalize all-green: "
           "pred43/obs43 HIT, 173/173 determinism byte-identical, null p95 0.5116 in-band)",
           "--prereg-ref",
           "research/TRIAL_LABOR_W18_PREREG.md FROZEN 2026-10-11 sec.3 judge (4-arm x 47 blocks = "
           "188 paired cells; dual nulls B=2000 block bootstrap + P=2000 sign-flip seed base "
           "trial_labor_w18_unc=20631000; evidence_cutoff 2026-09-22 lockbox; X=template_default)",
           "--data-gates",
           "fail-closed rc2 until judge_state.json present (landed r892); RAM gate 4GB r354 with "
           "AUTOFILL-PARK honest-refuse (r797; runner carries park markers + flush); D-leg deep "
           "panel presence asserted per claiming machine via data_deps (r316: registry-time "
           "presence != claim-time local presence)",
           "--data-deps", "[\"Money02/data/cache/t18_deep_panel/ohlcv\"]",
           "--shard-checkpoint",
           "results/trial_labor_w18/checkpoint/judge_shard_0of1.jsonl (MACHINE-LOCAL r429 "
           "gitignored; row-level done-set resume cross-kill law)",
           "--shard-note",
           "single shard W13-JUDGE (188 cells) / W17-JUDGE (344 cells) precedent; claim key "
           "matches runner _worker_claim w18-judge-0of1 (r860 handshake gap closed r893)",
           "--wp-note",
           "judge cells ~4-6x screen-cell weight (dual-leg L+D x {6m,12m,24m} x cost {x1,x2} + "
           "dual nulls B/P); worker_cap() RAM guard at runtime",
           "--consumer-plan",
           "TRIAL-LABOR-W18 chain: judge -> judge-finalize (G1'v2/G2-v2 + g2_reform_fdr4d + top-3 "
           "reform face + w18_paired_deltas.json four as-burned subgroup readouts) -> s4 intake "
           "(D6 binding gate) -> 48h CEO report clock starts at judge landing; scorecard/CEO "
           "one-pager faces"]
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True)
    out = (r.stdout + r.stderr).decode("utf-8", "replace")
    print("leg-1 submit rc=%d" % r.returncode)
    print(out.strip()[-600:])
    if r.returncode != 0:
        restore(POOL, shared0)
        if lane0 is not None:
            restore(lane_path, lane0)
        print("submit REFUSED -> rolled back, abort")
        return 2

    # ---- leg-2: rollback submit's write face, host-formula surgical append ----
    restore(POOL, shared0)
    if lane0 is not None:
        restore(lane_path, lane0)
    elif os.path.exists(lane_path):
        os.remove(lane_path)

    pool = json.loads(shared0.decode("utf-8"))
    assert not any(e.get("id") == EID for e in pool["entries"]), "id already present after restore"
    # roundtrip identity gate (r678) on the restored bytes
    assert host_bytes(pool) == shared0, "roundtrip NOT identical -- abort to surgical path"

    sub_out = json.loads([ln for ln in out.splitlines() if ln.startswith("{\"submitted")][0]) \
        if any(ln.startswith("{\"submitted") for ln in out.splitlines()) else None
    entry = None
    # recover the exact entry submit built (from the pool it wrote before rollback)
    # -- re-run the field assembly from submit semantics instead of parsing its
    # escaped write: rebuild from our known-good args (byte-identical semantics)
    import datetime
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "id": EID,
        "ticket_ref": cmd[cmd.index("--ticket-ref") + 1],
        "prereg_ref": cmd[cmd.index("--prereg-ref") + 1],
        "consumer_plan": cmd[cmd.index("--consumer-plan") + 1],
        "runner": "scripts/trial_labor_w18.py",
        "runner_args": ["judge", "0", "1"],
        "lane_owner": "ANY",
        "priority": 1,
        "status": "ready",
        "entered_at": now,
        "data_gates": cmd[cmd.index("--data-gates") + 1],
        "data_deps": ["Money02/data/cache/t18_deep_panel/ohlcv"],
        "shards": [{
            "key": "w18-judge-0of1",
            "status": "ready",
            "checkpoint": cmd[cmd.index("--shard-checkpoint") + 1],
            "note": cmd[cmd.index("--shard-note") + 1],
            "owner": None}],
        "workers_plan": {
            "workers": 8,
            "priority": "BelowNormal",
            "note": cmd[cmd.index("--wp-note") + 1]},
    }
    pool["entries"].append(entry)
    pool["updated_at"] = now

    new_bytes = host_bytes(pool)
    # r859 iron law: parse-gate BEFORE write
    parsed = json.loads(new_bytes.decode("utf-8"))
    assert any(e.get("id") == EID for e in parsed["entries"]), "parse-gate: entry missing"
    assert parsed["entries"][-1]["runner_args"] == ["judge", "0", "1"]
    assert parsed["entries"][-1]["shards"][0]["key"] == "w18-judge-0of1"
    open(POOL, "wb").write(new_bytes)

    # lane mirror via autofill's own writer (D-20260928-03(1))
    lane_tool._write_lane_file(POOL, parsed)

    # post-verify: reload + assertions + byte diff size sanity
    p2 = json.loads(open(POOL, "rb").read().decode("utf-8"))
    e2 = [e for e in p2["entries"] if e.get("id") == EID]
    assert len(e2) == 1 and e2[0]["status"] == "ready"
    assert len(p2["entries"]) == len(pool["entries"]) == 445
    delta = len(new_bytes) - len(shared0)
    print("leg-2 host-formula append OK: entries=%d, byte delta=+%d (entry block)" %
          (len(p2["entries"]), delta))
    return 0

if __name__ == "__main__":
    sys.exit(main())
