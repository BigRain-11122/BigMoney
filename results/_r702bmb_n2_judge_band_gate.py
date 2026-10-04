"""r702 bm-b N2-W15 sec.9.1 freeze-window judge-band derive (fresh
re-run per sec.9.1 precondition 3; r698 rehearsal recipe verbatim +
precondition-1 machine verification now that screen-finalize landed).
Receipt -> results/_r702bmb_n2_judge_band_gate.json.

Legs:
 P1. sec.9.1 precondition 1 verification: screen product present +
     trials_ledger block (finalize landed) + survivors non-empty.
 A.  import faces binding (science_gates / p5c census+cutoff / mtw1
     judge legs / tl14 replay+cutoff / n1 N1_BANDS live export).
 C.  judge band derive (r492 recipe): reserved = N1_BANDS live export
     (A+B) + SEED_REGISTRY values +-2000 halo (OWN excluded) +
     explicit documented actual ranges + A-ladder horizon (r682) +
     B-ladder projection; X_judge = smallest 500-multiple clean band.
 D.  ledger head live read (disclosure snapshot; finalize re-read law).
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "results", "_r702bmb_n2_judge_band_gate.json")
sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "scripts"))

BAND_WIDTH = 499
HALO = 2_000
OWN = {"perpetual_n2_w15_judge"}
EXPLICIT = [
    ("lfc_actual", 30_000, 30_099),
    ("t18_actual", 54_000, 54_999),
    ("xstock_nullA_actual", 51_000, 51_999),
    ("xstock_nullB_actual", 52_000, 52_999),
    ("n4_reserved_trio", 68_501, 69_999),
    ("n3_domain", 70_000, 70_999),
    ("probe_cluster", 95_000, 95_004),
    ("design_probe_40k", 40_000, 40_001),
]
EXPECT_CENSUS = {"L": {"6m": 1253, "12m": 1127, "24m": 875},
                 "D": {"6m": 3104, "12m": 2978, "24m": 2726}}


def main() -> int:
    out = {"tag": "_r702bmb_n2_judge_band_gate", "legs": {}, "err": None}
    rc = 0
    try:
        import science_gates as sg
        import p5c_virtual_timepoint as p5c
        import mass_trial_w1 as mtw1
        import trial_labor_w14 as tl14
        import perpetual_faces as n1mod

        # ---- P1: sec.9.1 precondition 1 (screen finalize landed) ----
        sp = os.path.join(REPO, "results", "n2_w15", "n2_w15_screen.json")
        p1 = {"screen_product_present": os.path.exists(sp)}
        if p1["screen_product_present"]:
            screen = json.load(open(sp, encoding="utf-8"))
            p1["trials_ledger_present"] = bool(screen.get("trials_ledger"))
            p1["n_survivors"] = screen.get("n_survivors")
            p1["survivors_nonempty"] = bool(screen.get("survivors"))
            p1["trials_total"] = (screen.get("trials_ledger") or
                                  {}).get("total")
        else:
            p1["trials_ledger_present"] = False
            p1["survivors_nonempty"] = False
        out["legs"]["P1_precondition_1"] = p1
        if not (p1["screen_product_present"]
                and p1["trials_ledger_present"]
                and p1["survivors_nonempty"]):
            rc = 2

        # ---- A: import faces binding ----
        a = {
            "science_gates": all(hasattr(sg, f) for f in (
                "g1_prime_v2", "g2_registration_v2", "dsr_from_stats",
                "ledger_head", "append_ledger", "cutoff_meta",
                "SEED_REGISTRY")),
            "p5c_cutoff_binding": p5c.EVIDENCE_CUTOFF_GRID == "2026-09-22",
            "p5c_census_shape": p5c.FROZEN_CENSUS == EXPECT_CENSUS,
            "mtw1_judge_legs": all(hasattr(mtw1, f) for f in (
                "cmd_judge_prep", "cmd_judge", "cmd_judge_finalize")),
            "tl14_replay_face": hasattr(tl14, "run_candidate_curve_w14"),
            "tl14_cutoff_binding": tl14.CUTOFF == "2026-09-22",
            "n1_bands_live_export": hasattr(n1mod, "N1_BANDS"),
        }
        out["legs"]["A_import_faces"] = a
        if not all(a.values()):
            rc = 2

        # ---- C: judge band derive (r492 recipe, live exports) ----
        bands = n1mod.N1_BANDS
        rows = [(w, bands[w]["a"][0], bands[w]["a"][1],
                 bands[w]["b_exit"][0], bands[w]["b_exit"][1])
                for w in sorted(bands)]
        a_head_end = max(r[2] for r in rows)
        max_wave = max(bands)
        b_head_end = bands[max_wave]["b_exit"][1]
        reserved = []
        for w, a0, a1, b0, b1 in rows:
            reserved.append((a0, a1))
            reserved.append((b0, b1))
        reg = {k: v for k, v in sg.SEED_REGISTRY.items()
               if isinstance(v, (int, float)) and k not in OWN}
        for v in reg.values():
            reserved.append((int(v) - HALO, int(v) + HALO))
        for _nm, lo, hi in EXPLICIT:
            reserved.append((lo, hi))
        horizon_lo = a_head_end + 1
        horizon_hi = a_head_end + 130 * 2_000
        reserved.append((horizon_lo, horizon_hi))
        bproj_hi = b_head_end + 130 * 200 + 5_000
        reserved.append((b_head_end + 1, bproj_hi))

        def clean(lo, hi):
            return all(hi < r0 or lo > r1 for r0, r1 in reserved)

        x_min = horizon_hi + 1
        x = ((x_min + 499) // 500) * 500
        steps = 0
        while not clean(x, x + BAND_WIDTH):
            x += 500
            steps += 1
            if steps > 4000:
                break
        band_clean = clean(x, x + BAND_WIDTH)
        n2_trio = {k: sg.SEED_REGISTRY.get(k) for k in (
            "perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull",
            "perpetual_n2_w15_unc")}
        c = {
            "n1_bands_rows": len(rows), "n1_max_wave": max_wave,
            "a_head_end": a_head_end, "b_head_end": b_head_end,
            "horizon": [horizon_lo, horizon_hi],
            "registry_n": len(reg), "halo": HALO,
            "own_key_excluded": sorted(OWN),
            "derived_x_judge": x, "scan_steps_past_x_min": steps,
            "band": [x, x + BAND_WIDTH],
            "band_clean": band_clean,
            "n2_screen_trio_in_registry": n2_trio,
            "verdict": "ADMIT" if (band_clean and rc == 0) else "REFUSE",
            "note": "sec.9.1 freeze-window derive (fresh live exports); "
                    "registration lands at the sec.9.1 freeze commit "
                    "(R250 one-step law, same commit)",
        }
        out["legs"]["C_judge_band_derive"] = c
        if not band_clean:
            rc = 2

        # ---- D: ledger head live read (disclosure snapshot) ----
        lh = sg.ledger_head()
        lh_small = {k: v for k, v in lh.items()
                    if isinstance(v, (int, float, str, bool, type(None)))}
        out["legs"]["D_ledger_head"] = {
            "ledger_head": lh_small,
            "note": "N_eff accumulation base snapshot (read-only); "
                    "finalize-time re-read is binding"}
    except Exception as e:  # mechanism fault -> honest report
        out["err"] = repr(e)
        rc = 2
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=True, indent=1)
    c = out["legs"].get("C_judge_band_derive", {})
    print("BANDGATE rc=%d P1_ok=%s verdict=%s X_judge=%s band=%s err=%s"
          % (rc,
             bool(out["legs"].get("P1_precondition_1", {})
                  .get("survivors_nonempty")),
             c.get("verdict", "N/A"), c.get("derived_x_judge", "N/A"),
             c.get("band", "N/A"), out["err"]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
