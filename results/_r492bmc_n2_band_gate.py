"""r492 bm-c N2-W15 slice-3 freeze-window band gate (W12/W13/W109/r602
precedent form): machine-derive the trio placement, never transcribe.
Legs:
 1. REFUSAL FACTS for the prereg sec.5 original trio (31_000/31_500/
    32_000): band extents vs live N1_BANDS (all rows, A + B) -- the
    forced-skip machine proof for the prereg disclosure.
 2. Reserved-set build: N1_BANDS all rows (A + B integer ranges, live
    import of scripts/perpetual_faces.py) + SEED_REGISTRY values with
    2,000 halo (own three N2 keys excluded -- they are being re-valued
    this window) + explicit documented actual ranges (lfc 30_000..30_099,
    t18 54_000..54_999, xstock 51/52k x999, N4 reserved trio
    68_501..69_999, N3 domain 70_000..70_999, probe cluster
    95_000..95_004, design probes 40_000/40_001) + A-ladder horizon
    reservation [A_head_end+1 .. A_head_end+130*2_000] (r682 ladder
    horizon law) + B-ladder projection above the B head of the highest
    registered wave.
 3. ADMIT derive: X = smallest 500-multiple >= A_head_end + 130*2_000 + 1;
    verify trio [X..X+499], [X+500..X+999], [X+1000..X+1499] disjoint
    from the whole reserved set; report nearest reserved faces.
Receipt -> results/_r492bmc_n2_band_gate.txt (ADMIT rc0 / REFUSE rc2).
Zero console CJK (r458 family)."""
import sys

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = REPO + r"\results\_r492bmc_n2_band_gate.txt"
OWN = {"perpetual_n2_w15_gen", "perpetual_n2_w15_scrnull",
       "perpetual_n2_w15_unc"}
OLD_TRIO = [("gen", 31_000), ("scrnull", 31_500), ("unc", 32_000)]
BAND_WIDTH = 499
HALO = 2_000
EXPLICIT = [
    ("lfc_actual", 30_000, 30_099),          # registry comment: 30_000+k flow
    ("t18_actual", 54_000, 54_999),          # 54_000+i, i<1000
    ("xstock_nullA_actual", 51_000, 51_999),  # 51_000+i, i<1000
    ("xstock_nullB_actual", 52_000, 52_999),  # 52_000+i, i<1000
    ("n4_reserved_trio", 68_501, 69_999),     # N4-B1 registry comment
    ("n3_domain", 70_000, 70_999),            # N3-R1 actual + 500-ladder
    ("probe_cluster", 95_000, 95_004),       # 95_002/95_003/95_004 design probes
    ("design_probe_40k", 40_000, 40_001),    # N2/N4 design-probe reserved pts
]


def main():
    lines = []
    sys.path.insert(0, REPO)                 # knowledge.cost_spec at root
    sys.path.insert(0, REPO + r"\scripts")
    import science_gates as sg               # noqa: E402
    import perpetual_faces as n1mod          # noqa: E402

    bands = n1mod.N1_BANDS
    rows = [(w, bands[w]["a"][0], bands[w]["a"][1],
             bands[w]["b_exit"][0], bands[w]["b_exit"][1])
            for w in sorted(bands)]
    n1_rows = len(rows)
    a_head_end = max(r[2] for r in rows)
    max_wave = max(bands)
    b_head_end = bands[max_wave]["b_exit"][1]
    lines.append(f"N1_BANDS rows={n1_rows} max_wave=W{max_wave} "
                 f"A_head_end={a_head_end} B_head_end(W{max_wave})={b_head_end}")

    # leg 1: refusal facts for the ORIGINAL trio
    refusals = []
    for nm, base in OLD_TRIO:
        lo, hi = base, base + BAND_WIDTH
        for w, a0, a1, b0, b1 in rows:
            if not (hi < a0 or lo > a1):
                refusals.append(f"OLD-{nm} band {lo}..{hi} hits W{w} A {a0}..{a1}")
            if not (hi < b0 or lo > b1):
                refusals.append(f"OLD-{nm} band {lo}..{hi} hits W{w} B {b0}..{b1}")
    lines.append(f"LEG1_OLD_TRIO_REFUSALS {len(refusals)}")
    lines.extend("  " + r for r in refusals[:12])

    # leg 2: reserved set
    reserved = []      # (lo, hi) integer intervals
    for w, a0, a1, b0, b1 in rows:
        reserved.append((a0, a1))
        reserved.append((b0, b1))
    reg = {k: v for k, v in sg.SEED_REGISTRY.items()
           if isinstance(v, (int, float)) and k not in OWN}
    reg_n = len(reg)
    for k, v in reg.items():
        reserved.append((int(v) - HALO, int(v) + HALO))
    for nm, lo, hi in EXPLICIT:
        reserved.append((lo, hi))
    horizon_lo = a_head_end + 1
    horizon_hi = a_head_end + 130 * 2_000
    reserved.append((horizon_lo, horizon_hi))
    bproj_hi = b_head_end + 130 * 200 + 5_000
    reserved.append((b_head_end + 1, bproj_hi))
    lines.append(f"LEG2_RESERVED reg_n={reg_n} halo={HALO} "
                 f"A_horizon=[{horizon_lo}..{horizon_hi}] "
                 f"B_projection=[{b_head_end + 1}..{bproj_hi}] "
                 f"n_intervals={len(reserved)}")

    def clean(lo, hi):
        return all(hi < r0 or lo > r1 for r0, r1 in reserved)

    # leg 3: ADMIT derive
    x_min = horizon_hi + 1                    # r682: lower bound above horizon
    x = ((x_min + 499) // 500) * 500          # smallest 500-multiple >= x_min
    trio = [("gen", x), ("scrnull", x + 500), ("unc", x + 1_000)]
    verdict = "ADMIT"
    details = []
    for nm, base in trio:
        lo, hi = base, base + BAND_WIDTH
        ok = clean(lo, hi)
        details.append(f"NEW-{nm} band {lo}..{hi} "
                       f"{'CLEAN' if ok else 'COLLISION'}")
        if not ok:
            verdict = "REFUSE"
    lines.append(f"LEG3_DERIVED_X {x} (x_min={x_min} rounded to 500)")
    lines.extend("  " + d for d in details)

    # nearest reserved faces below/above the trio (audit readability)
    trio_lo, trio_hi = x, x + 1_499
    below = max((r1 for r0, r1 in reserved if r1 < trio_lo), default=None)
    reg_below_20m = max((int(v) for v in reg.values() if int(v) < 20_000_000),
                        default=None)
    reg_above = min((int(v) for v in reg.values() if int(v) > trio_hi),
                    default=None)
    lines.append(f"AUDIT nearest_reserved_below={below} "
                 f"registry_max_below_20M={reg_below_20m} "
                 f"registry_min_above_trio={reg_above}")
    lines.append(f"BAND_GATE_VERDICT {verdict}")
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        f.write("\n".join(lines))
    print("BAND_GATE_VERDICT " + verdict + " X=" + str(x))
    return 0 if verdict == "ADMIT" else 2


if __name__ == "__main__":
    sys.exit(main())
