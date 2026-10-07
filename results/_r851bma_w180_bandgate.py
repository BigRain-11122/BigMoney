# -*- coding: utf-8 -*-
"""r851 bm-a W180 band gate -- four legs (r848 W179 band-gate bloodline:
gate-merge single-receipt law r812/r820/r823). Read-only; runs after the
seat publication push. ADMIT = the seat chain half-window closes green and
the r852 prereg+freeze (gated push) may proceed on these bands."""
import json, subprocess, sys, os
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
receipt = {"gate": "r851 W180 band gate", "legs": {}}

# leg0b: own seat on origin (r565 pre-freeze law: seat MSG on origin BEFORE freeze)
r = subprocess.run(["git", "show", "origin/main:fleet/inbox/processed/MSG-2026-10-08-0030-bma-w180-seat.md"],
                   cwd=ROOT, capture_output=True)
leg0b = r.returncode == 0 and "410_804..412_803" in r.stdout.decode("utf-8", "replace") \
    and "412_804..413_003" in r.stdout.decode("utf-8", "replace")
receipt["legs"]["leg0b_own_seat_on_origin"] = leg0b

# leg1: parity -- probe receipt bands == seat MSG bands == law-§4 staircase relation
p = json.load(open(os.path.join(ROOT, "results", "_r851bma_w180_probe_receipt.json"), encoding="utf-8"))
leg1 = (p["verdict"] == "ADMIT"
        and p["bands"] == {"A": "410804_412803", "B": "412804_413003"}
        and p["legs"]["leg1"]["A"] == [410804, 412803]
        and p["legs"]["leg1"]["B"] == [412804, 413003]
        and p["legs"]["leg1"]["hops_A"] == 1 and p["legs"]["leg1"]["hops_B"] == 1
        and p["legs"]["leg1"]["ARITH_A"] == [410604, 412603]
        and p["legs"]["leg1"]["ARITH_B"] == [410804, 411003]
        and "FORTIETH" in p["legs"]["leg1"]["A_semantics"])
receipt["legs"]["leg1_parity"] = leg1

# leg2: zero conflicts (probe leg2) + A/B machine relations
l1 = p["legs"]["leg1"]
leg2 = (p["legs"]["leg2"]["conflicts"] == 0
        and l1["A"][0] == 410_803 + 1            # A base == prior-wave (W179) B tail+1
        and l1["B"][0] == l1["A"][1] + 1          # B base == own-wave A tail+1
        and not (l1["A"][1] < l1["B"][0] or l1["B"][1] < l1["A"][0]) is False)
receipt["legs"]["leg2_zero_conflicts"] = leg2

# leg3: W181+ projection present (probe leg4, next freezer re-derives)
l4 = p["legs"]["leg4"]
leg3 = (l4["W181p_A"] == "412804..414803" and l4["W181p_B"] == "413004..413203"
        and l4["hops_A"] == 0 and l4["hops_B"] == 0
        and l4["W181p_B_lands_inside_W181p_A"] is True
        and "W181 freezer MUST re-derive" in l4["note"])
receipt["legs"]["leg3_w181_projection"] = leg3

ok = all(receipt["legs"].values())
receipt["probe_verdict"] = "ADMIT" if ok else "REFUSE"
receipt["rc"] = 0 if ok else 1
json.dump(receipt, open(os.path.join(ROOT, "results", "_r851bma_w180_bandgate.json"), "w",
                        encoding="utf-8"), ensure_ascii=False, indent=1)
print("W180 band gate:", receipt["probe_verdict"], receipt["legs"])
sys.exit(receipt["rc"])
