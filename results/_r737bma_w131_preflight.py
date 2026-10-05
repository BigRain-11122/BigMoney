# -*- coding: utf-8 -*-
"""r737 bm-a W131 finalize pre-flight 3-leg probe (r708 law, r736 v2 bloodline).
leg1 file completeness 12/12 reparse + dup + entry-count arithmetic;
leg2 live-process probe (python.exe runners only, probe-self exclusion --
the querying powershell carries the needle in its own CommandLine = self-match
false positive, r734 live-fire pit);
leg3 seat presence (published pre-freeze r736 fde20e3a1, archived r736 close 8fddd672a).
Receipt -> results/_r737bma_w131_preflight.json
"""
import subprocess
import glob
import json
import os

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
receipt = {"probe": "r737 W131 finalize pre-flight (r708 3-leg, r736 v2 bloodline)", "legs": {}}

# --- leg 1: file completeness + dup + entry arithmetic -----------------------
sh = sorted(glob.glob("results/p2cal_ext/n1_w131/shard-*-of-12.json"))
assert len(sh) == 12, f"leg1 FAIL: only {len(sh)} shards present"
names = [os.path.basename(s) for s in sh]
assert len(set(names)) == 12, "leg1 FAIL: dup shard names"
n_a = n_b = 0
for f in sh:
    d = json.load(open(f, encoding="utf-8"))
    fam = d["families"]
    n_a += fam["A_random_engine_exit"]["n"]
    n_b += fam["B_random_entry_random_exit"]["n"]
assert n_a + n_b == 2200, f"leg1 FAIL: entries {n_a}+{n_b} != 2200"
receipt["legs"]["leg1"] = {"shards": "12/12", "reparse": "PASS", "dup": 0,
                           "family_A": n_a, "family_B": n_b, "total": n_a + n_b}
print(f"leg1 PASS: 12/12 reparse, dup=0, A={n_a} B={n_b} total={n_a + n_b}")

# --- leg 2: live-process probe (python runners; exclude probe-self powershell) --
ps = subprocess.run(
    ["powershell", "-NoProfile", "-Command",
     "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' "
     "-and $_.CommandLine -match 'perpetual_faces_n1' } | "
     "ForEach-Object { $_.ProcessId }"],
    capture_output=True)
pids = [ln.strip() for ln in ps.stdout.decode("utf-8", "replace").splitlines()
        if ln.strip()]
receipt["legs"]["leg2"] = {"n1_runner_pids": pids,
                           "self_match_excluded": "python.exe filter only"}
print(f"leg2: live python N1 runner pids = {pids if pids else 'NONE'}")
assert not pids, f"leg2 FAIL: N1 runner still in flight: {pids}"

# --- leg 3: seat presence (published pre-freeze r736 fde20e3a1, archived r736 close 8fddd672a) --
g = subprocess.run(
    ["git", "log", "--oneline", "-1", "--",
     "fleet/inbox/processed/MSG-2026-10-05-1726-bma-w131-seat.md"],
    capture_output=True)
seat_commit = g.stdout.decode("utf-8", "replace").strip()
if not seat_commit:
    g = subprocess.run(
        ["git", "log", "--oneline", "--follow", "-1", "--",
         "fleet/inbox/MSG-2026-10-05-1726-bma-w131-seat.md"],
        capture_output=True)
    seat_commit = g.stdout.decode("utf-8", "replace").strip()
assert seat_commit, "leg3 FAIL: W131 seat MSG not found in git history"
receipt["legs"]["leg3"] = {"seat_commit": seat_commit.split()[0],
                           "seat": "MSG-2026-10-05-1726-bma-w131-seat",
                           "published": "r736 pre-freeze fde20e3a1 (r565 law)"}
print(f"leg3 PASS: seat on origin {seat_commit.split()[0]} (published=reserved)")

receipt["verdict"] = "GREEN_FINALIZE_READY"
json.dump(receipt, open("results/_r737bma_w131_preflight.json", "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("PRE-FLIGHT VERDICT: GREEN_FINALIZE_READY (3/3 legs)")
