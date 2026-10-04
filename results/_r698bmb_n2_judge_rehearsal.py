"""r698 bm-b N2-W15 judge-stage rehearsal probe (r633 finalize-rehearsal
precedent: validate BEFORE the judge batch -- every import face the
sec.9 placeholder names, machine-derive the judge band placement, live
read the N_eff chain head). Zero console CJK (r458 family). Receipt ->
results/_r698bmb_n2_judge_rehearsal.json.

Legs:
 A. import faces: science_gates (g1_prime_v2/g2_registration_v2/
    dsr_from_stats/ledger_head/append_ledger/SEED_REGISTRY/cutoff_meta),
    p5c (EVIDENCE_CUTOFF_GRID=="2026-09-22" binding + FROZEN_CENSUS shape
    == W3 sec.9.1 anchors), mass_trial_w1 judge three-legs
    (cmd_judge_prep/cmd_judge/cmd_judge_finalize), tl14
    run_candidate_curve_w14 (screen replay face == judge replay face,
    same-stack zero-migration claim), tl14.CUTOFF binding, tl2
    _finalize_math.
 B. screen progress face: 12-shard pool statuses + screen-finalize
    product absence (= sec.9 freeze precondition 1 pending); ZERO
    survivor claims (sec.4 zero-claim discipline, no reading of any
    survivor numbers).
 C. judge band derive (r492 recipe mirror, local root): reserved set =
    N1_BANDS live export (A+B) + SEED_REGISTRY values +-2000 halo
    (OWN={perpetual_n2_w15_judge} excluded -- being placed) + explicit
    documented actual ranges + A-ladder horizon
    [A_head_end+1 .. A_head_end+130*2000] (r682 law) + B-ladder
    projection; X_judge = smallest 500-multiple >= horizon_hi+1 with
    [X..X+499] clean vs whole reserved set (scan forward in 500 steps).
 D. ledger head live read (sg.ledger_head() -- read-only; the N_eff
    accumulation base for the sec.9 correction law; finalize-time
    re-read law applies, this value is a disclosure snapshot only).
"""
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "results", "_r698bmb_n2_judge_rehearsal.json")
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
    out = {"tag": "_r698bmb_n2_judge_rehearsal", "legs": {}, "err": None}
    rc = 0
    try:
        # ---- leg A: import faces ----
        import science_gates as sg
        import p5c_virtual_timepoint as p5c
        import mass_trial_w1 as mtw1
        import trial_labor_w14 as tl14
        import trial_labor_w2 as tl2
        import perpetual_faces as n1mod
        a = {
            "science_gates": all(hasattr(sg, f) for f in (
                "g1_prime_v2", "g2_registration_v2", "dsr_from_stats",
                "ledger_head", "append_ledger", "cutoff_meta", "SEED_REGISTRY")),
            "p5c_cutoff_binding": p5c.EVIDENCE_CUTOFF_GRID == "2026-09-22",
            "p5c_census_shape": p5c.FROZEN_CENSUS == EXPECT_CENSUS,
            "mtw1_judge_legs": all(hasattr(mtw1, f) for f in (
                "cmd_judge_prep", "cmd_judge", "cmd_judge_finalize")),
            "tl14_replay_face": hasattr(tl14, "run_candidate_curve_w14"),
            "tl14_cutoff_binding": tl14.CUTOFF == "2026-09-22",
            "tl2_finalize_math": hasattr(tl2, "_finalize_math"),
            "n1_bands_live_export": hasattr(n1mod, "N1_BANDS"),
        }
        out["legs"]["A_import_faces"] = a
        if not all(a.values()):
            rc = 2

        # ---- leg B: screen progress face (zero survivor claims) ----
        with open(os.path.join(REPO, "results", "runnable_pool.json"),
                  encoding="utf-8") as f:
            pool = json.load(f)
        shard_status = {}
        for ent in pool.get("entries", []):
            k = ent.get("key") or ent.get("id") or ""
            if k.startswith("PERPETUAL-N2-W15-SHARD-"):
                for sh in ent.get("shards", []):
                    shard_status[sh.get("shard_id") or sh.get("key", "?")] = \
                        sh.get("status")
        screen_product = os.path.join(REPO, "results", "n2_w15",
                                      "n2_w15_screen.json")
        b = {
            "shards": shard_status,
            "n_done": sum(1 for v in shard_status.values() if v == "done"),
            "screen_finalize_product_present": os.path.exists(screen_product),
            "survivor_claims": "none (sec.9 freeze precondition 1 pending "
                               "until screen-finalize lands)",
        }
        out["legs"]["B_screen_progress"] = b

        # ---- leg C: judge band derive (r492 recipe mirror) ----
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
            "verdict": "ADMIT" if band_clean else "COLLIDE",
            "note": "derive recipe disclosure only -- registration happens "
                    "at sec.9.1 freeze commit (R250 one-step law); freeze "
                    "window must re-derive with live exports",
        }
        out["legs"]["C_judge_band_derive"] = c
        if not band_clean:
            rc = 2

        # ---- leg D: ledger head live read (N_eff base, read-only) ----
        lh = sg.ledger_head()
        lh_small = {k: v for k, v in lh.items()
                    if isinstance(v, (int, float, str, bool, type(None)))}
        d = {"ledger_head": lh_small,
             "note": "N_eff accumulation base snapshot (read-only); "
                     "finalize-time re-read is binding, this is disclosure"}
        out["legs"]["D_ledger_head"] = d
    except Exception as e:  # mechanism fault -> honest report
        out["err"] = repr(e)
        rc = 2
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=True, indent=1)
    print("REHEARSAL rc=%d A_faces=%s B_done=%d/12 C_verdict=%s X_judge=%s "
          "D_total=%s err=%s" % (
              rc,
              all(out["legs"].get("A_import_faces", {}).values())
              if out["legs"].get("A_import_faces") else "N/A",
              out["legs"].get("B_screen_progress", {}).get("n_done", -1),
              out["legs"].get("C_judge_band_derive", {}).get("verdict", "N/A"),
              out["legs"].get("C_judge_band_derive", {}).get("derived_x_judge",
                                                             "N/A"),
              out["legs"].get("D_ledger_head", {}).get("ledger_head", {})
              .get("total", "N/A"),
              out["err"]))
    return rc


if __name__ == "__main__":
    sys.exit(main())
