# -*- coding: utf-8 -*-
# r846 bm-c W206 pre-finalize six-gate probe (verbatim-roll of
# _r917bma_w198_prefinalize_probe.py with W206 constants from frozen prereg
# research/PERPETUAL_N1_W206_PREREG.md / freeze receipt _w206bmc_freeze_receipt.json:
# A base 468_004 n=2000, B exit base 470_004 n=200, chain head = W205 landed
# ledger 868,171 (bm-a r963 finalize one-pass, receipt w205_upstream.ledger_total).
import glob, json, os, subprocess, sys

OUT = "results/perpetual_faces/n1_w206_results.json"
SHARDS = sorted(glob.glob("results/p2cal_ext/n1_w206/shard-*-of-*.json"))
A_BASE, A_N = 468004, 2000
B_BASE, B_N = 470004, 200
HEAD = 868171  # W205 finalize landed ledger 868,171 (one-pass, receipt-anchored)
gates = {}

# G4 output absent
gates["G4_output_absent"] = not os.path.exists(OUT)

# G5 no live finalize proc (r708: file-face is not process-face)
cim = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process -Filter \"Name='python.exe'\" | "
     "Where-Object {$_.CommandLine -match 'perpetual_faces_n1\\.py.*finalize'} | "
     "Measure-Object | Select-Object -ExpandProperty Count"],
    capture_output=True, text=True)
gates["G5_no_live_finalize_proc"] = int(cim.stdout.strip() or 0) == 0

a_runs, b_runs, nbt, shards_seen = [], [], 0, set()
a_til, b_til = [], []
for sf in SHARDS:
    d = json.load(open(sf, encoding="utf-8"))
    shards_seen.add(d["shard"])
    fams = d.get("families") or {}
    ar = (fams.get("A_random_engine_exit") or {}).get("runs") or []
    br = (fams.get("B_random_entry_random_exit") or {}).get("runs") or []
    a_runs += ar; b_runs += br
    nbt += (d.get("audit") or {}).get("n_backtests", 0)
    a_til.append((d["shard"], tuple(d["a_range"])))
    b_til.append((d["shard"], tuple(d["b_range"])))

# G1 counts (r831 half-open: families.n is the truth face)
gates["G1_shard_set"] = shards_seen == set(range(12))
gates["G1_A_n"] = len(a_runs) == A_N
gates["G1_B_n"] = len(b_runs) == B_N

# G2 total backtests + half-open tiling (r831 law: [start,end) semantics)
gates["G2_n_backtests"] = nbt == A_N + B_N
def _tile(rngs, n_tot):
    s = sorted(rngs)
    return (s[0][1][0] == 0 and s[-1][1][1] == n_tot
            and all(s[i][1][1] == s[i + 1][1][0] for i in range(len(s) - 1)))
gates["G2_A_halfopen_tiling"] = _tile(a_til, A_N)
gates["G2_B_halfopen_tiling"] = _tile(b_til, B_N)

# G3 seed continuity (closed-band endpoints, unique sweep)
a_seeds = sorted(int(r["seed_rng"]) for r in a_runs)
b_entry = sorted(int(r["seed_rng_entry"]) for r in b_runs)
b_exit = sorted(int(r["seed_rng_exit"]) for r in b_runs)
gates["G3_A_min_max_uniq"] = (a_seeds[0] == A_BASE and a_seeds[-1] == A_BASE + A_N - 1
                              and len(set(a_seeds)) == A_N)
gates["G3_A_contiguous"] = a_seeds == list(range(A_BASE, A_BASE + A_N))
gates["G3_B_exit_band"] = (b_exit and b_exit[0] == B_BASE and b_exit[-1] == B_BASE + B_N - 1
                           and len(set(b_exit)) == B_N)
gates["G3_B_entry_pairs_A"] = b_entry == a_seeds[:B_N]

# G6 chain head derive (r538: prev = scan of landed results files)
tot = []
for f in glob.glob("results/perpetual_faces/n1_w*_results.json"):
    try:
        d = json.load(open(f, encoding="utf-8"))
        led = (d.get("science_gates") or {}).get("ledger") or d.get("trials_ledger") or {}
        if led.get("total"):
            tot.append(led["total"])
    except Exception:
        pass
gates["G6_head_868171"] = (max(tot) if tot else None) == HEAD

ok = all(bool(v) for v in gates.values())
for k, v in gates.items():
    print(("PASS " if v else "FAIL ") + k + ("" if v else f"  <- {v}"))
print("VERDICT:", "GREEN_FINALIZE_READY" if ok else "BLOCKED")
json.dump({"wave": 206, "gates": {k: bool(v) for k, v in gates.items()},
           "verdict": "GREEN_FINALIZE_READY" if ok else "BLOCKED",
           "head": max(tot) if tot else None, "n_shard_files": len(SHARDS)},
          open("results/_r846bmc_w206_prefinalize_probe.json", "w"),
          ensure_ascii=False, indent=1)
sys.exit(0 if ok else 2)
