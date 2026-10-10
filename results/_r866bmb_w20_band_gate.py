"""r866 bm-b PERPETUAL-N2-W20 slice-2 freeze-window band gate (r864 W19
precedent form, live derive, never transcribe). Legs:
 1. DRAFT-band-value absence (prereg sec.3 writes NO band values -- r702
    lesson) + forced-skip facts: the naive next 500-slot above the W19
    family band (737_500) now collides with the W19 registered-key halo
    (perpetual_n2_w19_unc=737_000, halo 2_000 -> 739_000) -> the derive
    walks past the whole W18+W19 halo chain; position forced by the r682
    law, not free-picked (replication wave: only free degree = seed band).
 2. Reserved-set build: N1_BANDS all rows (A + B, live import) +
    SEED_REGISTRY values with 2,000 halo (own W20 keys excluded -- none
    registered yet, belt keeps the gate idempotent) + explicit documented
    actual ranges (r492 list) + A-ladder horizon reservation
    [A_head_end+1 .. A_head_end+130*2_000] + B-ladder projection above
    the B head of the highest registered wave.
 3. ADMIT derive: X = smallest 500-multiple >= A_head_end + 130*2_000 + 1;
    trio [X..X+499], [X+500..X+999], [X+1000..X+1499] disjoint from the
    whole reserved set; nearest reserved faces audit; repo text scan for
    the derived band strings in scripts/ + research/ (foreign-zero-hit
    disclosure, census r841 registration precedent).
Receipt -> results/_r866bmb_w20_band_gate.txt (ADMIT rc0 / REFUSE rc2).
Zero console CJK (r458 family).
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REPO, "results", "_r866bmb_w20_band_gate.txt")
PREREG = os.path.join(REPO, "research", "PERPETUAL_N2_W20_PREREG.md")
OWN = {"perpetual_n2_w20_gen", "perpetual_n2_w20_scrnull",
       "perpetual_n2_w20_unc"}
BAND_WIDTH = 499
HALO = 2_000
EXPLICIT = [
    ("lfc_actual", 30_000, 30_099),           # registry comment: 30_000+k flow
    ("t18_actual", 54_000, 54_999),           # 54_000+i, i<1000
    ("xstock_nullA_actual", 51_000, 51_999),  # 51_000+i, i<1000
    ("xstock_nullB_actual", 52_000, 52_999),  # 52_000+i, i<1000
    ("n4_reserved_trio", 68_501, 69_999),     # N4-B1 registry comment
    ("n3_domain", 70_000, 70_999),            # N3-R1 actual + 500-ladder
    ("probe_cluster", 95_000, 95_004),        # 95_002/95_003/95_004 probes
    ("design_probe_40k", 40_000, 40_001),     # N2/N4 design-probe reserved pts
]


def main():
    lines = []
    sys.path.insert(0, REPO)                  # knowledge.cost_spec at root
    sys.path.insert(0, os.path.join(REPO, "scripts"))
    import science_gates as sg               # noqa: E402
    import perpetual_faces as n1mod           # noqa: E402

    # ---- leg 1: draft band-value absence + forced-skip facts
    with open(PREREG, encoding="utf-8") as f:
        ptext = f.read()
    draft_seed_line = [ln for ln in ptext.splitlines()
                      if "草案禁写带值" in ln]
    band_numbers_in_seed = re.findall(
        r"perpetual_n2_w20_(?:gen|scrnull|unc)\D{0,40}?(\d{2,3}[_ ]?\d{3})",
        ptext)
    lines.append("LEG1_DRAFT_POSTURE")
    lines.append(f"  draft_no_band_values_marker_lines="
                 f"{len(draft_seed_line)} (expect >=1)")
    lines.append(f"  band_values_in_prereg={band_numbers_in_seed} "
                 f"(expect [])")

    bands = n1mod.N1_BANDS
    rows = [(w, bands[w]["a"][0], bands[w]["a"][1],
             bands[w]["b_exit"][0], bands[w]["b_exit"][1])
            for w in sorted(bands)]
    n1_rows = len(rows)
    a_head_end = max(r[2] for r in rows)
    max_wave = max(bands)
    b_head_end = bands[max_wave]["b_exit"][1]
    lines.append(f"  N1_BANDS rows={n1_rows} max_wave=W{max_wave} "
                 f"A_head_end={a_head_end} B_head_end(W{max_wave})="
                 f"{b_head_end}")
    horizon_lo, horizon_hi = a_head_end + 1, a_head_end + 130 * 2_000
    naive_after_w19 = 737_500                # next 500-slot above W19 trio
    w19_unc = sg.SEED_REGISTRY.get("perpetual_n2_w19_unc")
    w19_halo_hi = None if w19_unc is None else int(w19_unc) + HALO
    forced = (w19_halo_hi is not None
              and naive_after_w19 <= w19_halo_hi)
    lines.append(f"  A_horizon=[{horizon_lo}..{horizon_hi}] "
                 f"naive_next_slot_after_W19={naive_after_w19} "
                 f"W19_unc={w19_unc} W19_halo_hi={w19_halo_hi} "
                 f"naive_collides_w19_halo={forced} -> derive position "
                 f"forced by r682 law + W18+W19 family halo chain (not "
                 f"free-picked)")

    # ---- leg 2: reserved set
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
    reserved.append((horizon_lo, horizon_hi))
    bproj_hi = b_head_end + 130 * 200 + 5_000
    reserved.append((b_head_end + 1, bproj_hi))
    lines.append(f"LEG2_RESERVED reg_n={reg_n} halo={HALO} "
                 f"A_horizon=[{horizon_lo}..{horizon_hi}] "
                 f"B_projection=[{b_head_end + 1}..{bproj_hi}] "
                 f"n_intervals={len(reserved)}")

    def clean(lo, hi):
        return all(hi < r0 or lo > r1 for r0, r1 in reserved)

    # ---- leg 3: ADMIT derive
    x_min = horizon_hi + 1                    # r682: lower bound above horizon
    x = ((x_min + 499) // 500) * 500          # smallest 500-multiple >= x_min
    verdict = "ADMIT"
    details = []
    while True:
        trio = [("gen", x), ("scrnull", x + 500), ("unc", x + 1_000)]
        ok_all = all(clean(b, b + BAND_WIDTH) for _, b in trio)
        if ok_all:
            for nm, base in trio:
                details.append(f"NEW-{nm} band {base}..{base + BAND_WIDTH} "
                               f"CLEAN")
            break
        details.append(f"SKIP x={x} (collision, walking +500)")
        x += 500
        if x > x_min + 100_000:
            verdict = "REFUSE"
            details.append("walk window exhausted")
            break
    lines.append(f"LEG3_DERIVED_X {x} (x_min={x_min} rounded to 500)")
    lines.extend("  " + d for d in details)

    # nearest reserved faces below/above the trio (audit readability)
    trio_lo, trio_hi = x, x + 1_499
    below = max((r1 for r0, r1 in reserved if r1 < trio_lo), default=None)
    above = min((r0 for r0, r1 in reserved if r0 > trio_hi), default=None)
    lines.append(f"AUDIT nearest_reserved_below={below} "
                 f"nearest_reserved_above={above}")

    # repo text scan for the derived band strings (foreign-zero-hit
    # disclosure, census r841 precedent). NEW face vs W19 form: the r865
    # draft probe read-only derive readout (X=739,500) is quoted in the
    # r865 HANDOVER 5x row (research/) -> self-face classification leg:
    # a hit whose containing line carries the own-wave draft-readout
    # marker (W20 + derive/只读) is the registration's own custody chain
    # (r865 probe readout -> r866 freeze derive confirmation), disclosed
    # not blocking; any hit without that marker = foreign -> REFUSE.
    hits = []
    self_hits = []
    pats = [f"{x:,}", f"{x + 500:,}", f"{x + 1_000:,}",
            str(x), str(x + 500), str(x + 1_000)]
    pats = sorted(set(pats))
    for sub in ("scripts", "research"):
        d = os.path.join(REPO, sub)
        for fn in os.listdir(d):
            if not fn.endswith(".py") and not fn.endswith(".md"):
                continue
            fp = os.path.join(d, fn)
            try:
                with open(fp, encoding="utf-8", errors="replace") as f:
                    t = f.read()
            except OSError:
                continue
            for p in pats:
                if p in t:
                    i = t.find(p)
                    ln_start = t.rfind("\n", 0, i) + 1
                    ln_end = t.find("\n", i)
                    if ln_end == -1:
                        ln_end = len(t)
                    line_text = t[ln_start:ln_end]
                    is_self = ("W20" in line_text
                               and ("derive" in line_text
                                    or "只读" in line_text))
                    rec = f"{sub}/{fn}:{p}"
                    if is_self:
                        self_hits.append(rec + " [SELF own-wave r865 "
                                         "draft-readout citation]")
                    else:
                        hits.append(rec)
    lines.append(f"REPO_TEXT_SCAN patterns={pats} foreign_hits={hits} "
                 f"self_hits={self_hits} "
                 f"(self=own-wave r865 draft-probe readout custody face, "
                 f"disclosed not blocking; foreign!=0 -> REFUSE)")
    if hits:
        verdict = "REFUSE"
    lines.append(f"BAND_GATE_VERDICT {verdict}")
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))
    print("BAND_GATE_VERDICT " + verdict + " X=" + str(x))
    return 0 if verdict == "ADMIT" else 2


if __name__ == "__main__":
    sys.exit(main())
