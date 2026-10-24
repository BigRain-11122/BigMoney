#!/usr/bin/env python
# n1_seat_probe.py -- generic PERPETUAL N1 pre-seat probe (bm-c engine-owner lane).
#
# Why this tool exists (gate-building law, r1168/r1171 pit class):
#   every wave the bm-c window used to COPY-SHIFT the previous wave's probe
#   script (results/_w<N-1>bmc_*_probe.py -> _w<N>bmc_*_probe.py) and patch
#   literals by hand.  That copy-shift is exactly the "double shift" defect
#   surface (r1168 wave-gate literals moved twice; r1171 literal counting by
#   line instead of occurrence).  This tool derives EVERYTHING live from the
#   registered universe (scripts/perpetual_faces.py N1_BANDS) and the previous
#   wave's finalize product -- zero transcribed bands, zero literal patching.
#
# Usage:
#   python Tools/n1_seat_probe.py                 # wave = max(owner)+1
#   python Tools/n1_seat_probe.py --wave 296
#   python Tools/n1_seat_probe.py --wave 296 --a-hop-ordinal 49 --above-ordinal 50
#   python Tools/n1_seat_probe.py selftest
#
# What it does (all read-only except the receipt file):
#   leg0  universe continuity: owner rows == wave-1, tail == wave-1, prev
#         finalize product present + ledger/merged anchors machine-read
#   leg1  live forward-monotone hop walk (r587) for A and B; own-wave A window
#         reserved when deriving B (W141 builder / E36 convention)
#   leg2  seed_admit_gate FREE on both bands (O-20261010-1945-bm-a)
#   leg3  point-wise clear of EVERY registered wave
#   leg4  projection on the pre-<wave> universe for the next freezer
#
# Exit codes: 0 = ADMIT receipt written, 2 = REFUSE/mechanism fault (no write).
# ENCODING: pure ASCII source; receipt JSON written UTF-8.
import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO, "scripts"))
import perpetual_faces as pf  # noqa: E402

WIDTH_A = 2000
WIDTH_B = 200
ORDINALS = [
    "FIRST", "SECOND", "THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH",
    "EIGHTH", "NINTH", "TENTH", "ELEVENTH", "TWELFTH", "THIRTEENTH",
    "FOURTEENTH", "FIFTEENTH", "SIXTEENTH", "SEVENTEENTH", "EIGHTEENTH",
    "NINETEENTH", "TWENTIETH", "TWENTY-FIRST", "TWENTY-SECOND",
    "TWENTY-THIRD", "TWENTY-FOURTH", "TWENTY-FIFTH", "TWENTY-SIXTH",
    "TWENTY-SEVENTH", "TWENTY-EIGHTH", "TWENTY-NINTH", "THIRTIETH",
    "THIRTY-FIRST", "THIRTY-SECOND", "THIRTY-THIRD", "THIRTY-FOURTH",
    "THIRTY-FIFTH", "THIRTY-SIXTH", "THIRTY-SEVENTH", "THIRTY-EIGHTH",
    "THIRTY-NINTH", "FORTIETH", "FORTY-FIRST", "FORTY-SECOND",
    "FORTY-THIRD", "FORTY-FOURTH", "FORTY-FIFTH", "FORTY-SIXTH",
    "FORTY-SEVENTH", "FORTY-EIGHTH", "FORTY-NINTH", "FIFTIETH",
]


def ordinal_word(n):
    return ORDINALS[n - 1] if 0 < n <= len(ORDINALS) else "%dTH" % n


def fmt(b):
    return "%d_%03d..%d_%03d" % (b[0] // 1000, b[0] % 1000,
                                 b[1] // 1000, b[1] % 1000)


def owner_rows():
    return sorted(w for w, c in pf.N1_BANDS.items()
                  if (c or {}).get("engine_owner"))


def registry_points():
    pts = {}
    for w, c in pf.N1_BANDS.items():
        if not c:
            continue
        a0, a1 = c["a"]
        b0, b1 = c["b_exit"]
        for s in range(a0, a1 + 1):
            pts.setdefault(s, "W%dA" % w)
        for s in range(b0, b1 + 1):
            pts.setdefault(s, "W%dB" % w)
    # Registered non-N1 seeds are refusers too: the ADMIT gate refuses a band
    # containing any SEED_REGISTRY value, so the walk must hop past them instead
    # of walking clean and failing leg2 (r1230 W325 first REFUSE: B naive
    # 732_301..732_500 hit perpetual_n2_w18_gen=732500).
    try:
        import science_gates as sg  # noqa: E402
    except Exception:
        return pts
    for key, val in (getattr(sg, "SEED_REGISTRY", None) or {}).items():
        if isinstance(val, int) and not isinstance(val, bool):
            if not isinstance(key, str) or key.startswith("_"):
                continue
            pts.setdefault(val, "REG:%s" % key)
    return pts


def walk(pts, base, span):
    """Forward-monotone hop walk (r587): first window with zero refusers."""
    chain = []
    cur = base
    hop = 0
    while True:
        lo, hi = cur, cur + span - 1
        hits = {}
        for s in range(lo, hi + 1):
            lbl = pts.get(s)
            if lbl:
                hits.setdefault(lbl, []).append(s)
        if not hits:
            return [lo, hi], hop, chain
        hop += 1
        bands = sorted({(min(v), max(v)) for v in hits.values()})
        top = max(b[1] for b in bands)
        chain.append({"hop": hop, "window": [lo, hi], "jump_to": top + 1,
                      "refuser_bands": [list(b) for b in bands],
                      "refuser_pts_sample": [min(v) for v in hits.values()]})
        cur = top + 1


def _fail(msg):
    print(json.dumps({"verdict": "REFUSE", "error": msg}, ensure_ascii=False))
    return 2


def probe(wave, a_hop_ordinal=None, above_ordinal=None, out_dir=None,
          write=True):
    rows = owner_rows()
    wprev = wave - 1
    # ---- leg0: universe continuity ----
    if not rows:
        return None, _fail("empty registered universe")
    if max(rows) != wprev:
        return None, _fail("registry tail %d != wave-1 %d" % (max(rows), wprev))
    holes = [w for w in range(rows[0], wprev + 1) if w not in set(rows)]
    prev = pf.N1_BANDS[wprev]
    prevprev = pf.N1_BANDS[wprev - 1]
    fin_path = os.path.join(REPO, "results", "perpetual_faces",
                            "n1_w%d_results.json" % wprev)
    if not os.path.exists(fin_path):
        return None, _fail("prev finalize product missing: %s" % fin_path)
    fin = json.load(open(fin_path, encoding="utf-8"))
    led = (fin.get("science_gates") or {}).get("ledger") or {}
    ledger_total = led.get("total")
    merged_n = (fin.get("null_pool_cumulative") or {}).get(
        "merged", {}).get("n_values")
    if not isinstance(ledger_total, int) or not isinstance(merged_n, int):
        return None, _fail("prev finalize anchors missing")

    # ---- leg1: live walk ----
    pts = registry_points()
    arith_a = [prev["a"][1] + 1, prev["a"][1] + WIDTH_A]
    A_clean, hops_A, A_chain = walk(pts, arith_a[0], WIDTH_A)
    arith_b = [prev["b_exit"][1] + 1, prev["b_exit"][1] + WIDTH_B]
    B_naive, _, _ = walk(pts, arith_b[0], WIDTH_B)
    B_inside_A = not (B_naive[1] < A_clean[0] or B_naive[0] > A_clean[1])
    if B_inside_A:
        B_clean, _, _ = walk(pts, max(A_clean[1] + 1, arith_b[0]), WIDTH_B)
        B_chain = [{"hop": 1, "window": B_naive, "jump_to": B_clean[0],
                    "refuser_bands": [list(A_clean)],
                    "refuser_pts_sample": [],
                    "kind": "own-A reservation cascade"}]
        hops_B = 1
    else:
        B_clean, hops_B, B_chain = walk(pts, arith_b[0], WIDTH_B)
    A0, A1 = A_clean
    B0, B1 = B_clean

    # B is placed as the first clean window above own A.  Historically that window
    # starts exactly at own-A tail + 1; when a registered non-N1 seed sits directly
    # above own A the walk hops past it and the strict +1 form is impossible -- the
    # placement law is then "first clean window above own A", disclosed with the
    # intervening refusers (r1230 W325: perpetual_n2_w18_gen=732500 refused the
    # 732_301..732_500 window).
    b_alt, _, _ = walk(pts, A1 + 1, WIDTH_B)
    seed_hop_disclosure = []
    if B0 != A1 + 1:
        for s in range(A1 + 1, B0):
            lbl = pts.get(s)
            if lbl:
                seed_hop_disclosure.append({"seed": s, "refuser": lbl})

    relations = {
        "A_base_ge_priorB_tail_plus1": A0 >= prev["b_exit"][1] + 1,
        "B_lands_above_own_A": B0 > A1,
        "AB_mutual_exclusion": B0 > A1,
        "B_base_eq_own_A_tail_plus1": B0 == A1 + 1,
        "B_base_eq_first_clean_above_own_A": B0 == b_alt[0],
    }
    if not (relations["A_base_ge_priorB_tail_plus1"]
            and relations["B_lands_above_own_A"]
            and relations["AB_mutual_exclusion"]
            and (relations["B_base_eq_own_A_tail_plus1"]
                 or relations["B_base_eq_first_clean_above_own_A"])
            and (not relations["B_base_eq_first_clean_above_own_A"]
                 or relations["B_base_eq_own_A_tail_plus1"]
                 or bool(seed_hop_disclosure))):
        return None, _fail("band relation broken: %r" % relations)

    # ---- leg3: point-wise clear of every registered wave ----
    for w, c in pf.N1_BANDS.items():
        if not c:
            continue
        for lo, hi in ((A0, A1), (B0, B1)):
            for key in ("a", "b_exit"):
                r0, r1 = c[key]
                if not (hi < r0 or lo > r1):
                    return None, _fail("band overlap with registered W%d" % w)

    # ---- leg2: seed admit gate (both bands) ----
    gates = []
    for base, span in ((A0, WIDTH_A), (B0, WIDTH_B)):
        g = subprocess.run(
            [sys.executable, os.path.join(REPO, "Tools", "seed_admit_gate.py"),
             str(base), "--span", str(span)],
            cwd=REPO, capture_output=True, text=True, encoding="utf-8",
            errors="replace")
        if g.returncode != 0:
            return None, _fail("seed_admit_gate FAIL base=%d: %s %s"
                               % (base, g.stdout[-300:], g.stderr[-300:]))
        gates.append((g.stdout.strip().splitlines() or ["rc0 base=%d" % base])[-1])

    # ---- leg4: next-wave projection on the pre-<wave> universe ----
    pA, phA, _ = walk(pts, A1 + 1, WIDTH_A)
    pB, phB, _ = walk(pts, B1 + 1, WIDTH_B)
    proj = {
        "W%dp_A_naive" % (wave + 1): fmt(pA),
        "W%dp_A_first_clean" % (wave + 1): fmt(pA),
        "W%dp_B_naive" % (wave + 1): fmt(pB),
        "W%dp_B_first_clean" % (wave + 1): fmt(pB),
        "hops_A": phA,
        "hops_B": phB,
        "W%dp_B_lands_inside_W%dp_A_naive" % (wave + 1, wave + 1):
            not (pB[1] < pA[0] or pB[0] > pA[1]),
        "note": ("projection on the PRE-W%d universe; once W%d registers the "
                 "next freezer MUST re-derive live and reserve its own-wave A "
                 "window when deriving B -- never transcribe r587"
                 % (wave, wave)),
    }

    a_ord = a_hop_ordinal or 0
    b_ord = above_ordinal or 0
    receipt = {
        "probe": ("W%d pre-seat probe (generic Tools/n1_seat_probe.py; live walk "
                  "on the post-W%d-REGISTERED %d-owner universe; seat-first law "
                  "O-20261010-2350 sec.2)" % (wave, wprev, len(rows))),
        "legs": {
            "leg0": {
                "rows": len(rows), "tail": "W%d registered+finalized" % wprev,
                "wprev_bands": {"A": list(prev["a"]),
                                "B": list(prev["b_exit"])},
                "wprev_minus1_bands": {"A": list(prevprev["a"]),
                                       "B": list(prevprev["b_exit"])},
                "wprev_finalize_landed": True,
                "wprev_finalize_anchors": {
                    "ledger_total": ledger_total, "merged_n": merged_n,
                    "skill_line_delta_k_lift": led.get("skill_line_delta_k_lift")},
                "inflight_upstream": False,
                "owner_rows": len(rows),
                "bmc_rows": len([w for w in rows
                                 if pf.N1_BANDS[w]["engine_owner"] == "bm-c"]),
                "bma_rows": len([w for w in rows
                                 if pf.N1_BANDS[w]["engine_owner"] == "bm-a"]),
                "bmb_rows": len([w for w in rows
                                 if pf.N1_BANDS[w]["engine_owner"] == "bm-b"]),
                "ordinal": len(rows) + 1,
                "owner_row_holes": holes,
            },
            "leg1": {
                "ARITH_A": arith_a, "ARITH_B": arith_b,
                "A": [A0, A1], "hops_A": hops_A, "A_hop_chain": A_chain,
                "B": [B0, B1], "hops_B": hops_B, "B_hop_chain": B_chain,
                "B_naive": arith_b,
                "B_naive_refused_at_start": B_inside_A,
                "B_lands_above_own_A": True,
                "A_semantics": ("A arithmetic continuation %d..%d walked "
                                "forward-monotone (hops=%d, r587)"
                                % (arith_a[0], arith_a[1], hops_A)),
                "B_semantics": ("B arithmetic continuation %d..%d: "
                                "own-A-reservation=%s, hops=%d"
                                % (arith_b[0], arith_b[1], B_inside_A, hops_B)),
                "relation_asserts": relations,
                "B_seed_hop_disclosure": seed_hop_disclosure,
            },
            "leg2": {"AB_mutual_exclusion": True, "A": [A0, A1],
                     "B": [B0, B1], "seed_admit_gate": gates,
                     "note": "both bands FREE per seed_admit_gate"},
            "leg3": {"universe": "post-W%d-REGISTERED" % wprev,
                     "owner_rows": len(rows), "bands_clear": True},
            "leg4": dict(proj, candidate_bands={"A": [A0, A1],
                                                "B": [B0, B1]}),
        },
        "verdict": "ADMIT",
        "bands": {"A": [A0, A1], "B": [B0, B1], "a_lo": A0, "a_hi": A1,
                  "b_lo": B0, "b_hi": B1},
        "ordinals": {
            "a_hop": a_ord, "a_hop_word": ordinal_word(a_ord),
            "above_own_a": b_ord, "above_own_a_word": ordinal_word(b_ord),
            "authority": ("per r1170 the prereg BODY chain is the single source "
                          "of truth for ordinals; the seat window passes them in "
                          "explicitly (never derived from commit messages)"),
        },
    }
    if write:
        stem = os.path.join(out_dir or os.path.join(REPO, "results"),
                            "_w%dbmc_%s_probe_receipt.json"
                            % (wave, _today()))
        with open(stem, "w", encoding="utf-8") as fh:
            json.dump(receipt, fh, indent=1, ensure_ascii=False)
        receipt["_receipt_path"] = stem
    return receipt, 0


def _today():
    import datetime
    return datetime.date.today().strftime("%Y%m%d")


def selftest():
    """Offline: walk semantics + registry continuity on the live tree (read-only)."""
    legs = []

    def leg(name, ok, extra=""):
        legs.append((name, ok))
        print("%-58s %s %s" % (name, "PASS" if ok else "FAIL", extra))

    pts = {10: "WA", 11: "WA", 50: "WB"}
    w, h, ch = walk(pts, 8, 5)
    leg("walk hops past a refuser band", (w == [12, 16] and h == 1 and len(ch) == 1))
    w2, h2, ch2 = walk(pts, 100, 5)
    leg("walk clean at start -> zero hops", (w2 == [100, 104] and h2 == 0 and not ch2))
    rows = owner_rows()
    holes = [x for x in range(rows[0], max(rows) + 1) if x not in set(rows)]
    leg("owner rows contiguous to the tail (holes reported, not fatal)",
        len(holes) <= 1, "rows=%d tail=%d holes=%r" % (len(rows), max(rows), holes))
    leg("ordinal_word(FORTY-NINTH)", ordinal_word(49) == "FORTY-NINTH")
    leg("fmt band", fmt([666301, 666500]) == "666_301..666_500")
    rpts = registry_points()
    try:
        import science_gates as sg  # noqa: E402
        intvals = sorted(v for v in (getattr(sg, "SEED_REGISTRY", None) or {}).values()
                         if isinstance(v, int) and not isinstance(v, bool))
    except Exception:
        intvals = []
    leg("registered non-N1 seeds are walk refusers",
        all(v in rpts for v in intvals), "seeds=%d" % len(intvals))
    fails = [n for n, ok in legs if not ok]
    print("selftest: %d/%d PASS" % (len(legs) - len(fails), len(legs)))
    return 1 if fails else 0


def main(argv):
    args = argv[1:]
    if args and args[0] == "selftest":
        return selftest()
    wave = None
    a_ord = None
    b_ord = None
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--wave":
            wave = int(args[i + 1]); i += 2
        elif a == "--a-hop-ordinal":
            a_ord = int(args[i + 1]); i += 2
        elif a == "--above-ordinal":
            b_ord = int(args[i + 1]); i += 2
        elif a in ("--no-write", "--dry"):
            i += 1
        else:
            print("usage: n1_seat_probe.py [--wave N] [--a-hop-ordinal N] "
                  "[--above-ordinal N] [--no-write] | selftest")
            return 2
    rows = owner_rows()
    if wave is None:
        wave = max(rows) + 1
    rec, rc = probe(wave, a_ord, b_ord, write="--no-write" not in args
                    and "--dry" not in args)
    if rc != 0:
        return rc
    print(json.dumps({
        "verdict": rec["verdict"], "wave": wave,
        "bands": rec["bands"],
        "hops_A": rec["legs"]["leg1"]["hops_A"],
        "hops_B": rec["legs"]["leg1"]["hops_B"],
        "A_chain": rec["legs"]["leg1"]["A_hop_chain"],
        "B_chain": rec["legs"]["leg1"]["B_hop_chain"],
        "gates": rec["legs"]["leg2"]["seed_admit_gate"],
        "universe": {k: rec["legs"]["leg0"][k]
                     for k in ("owner_rows", "bma_rows", "bmb_rows",
                               "bmc_rows", "ordinal")},
        "anchors": rec["legs"]["leg0"]["wprev_finalize_anchors"],
        "proj": {k: v for k, v in rec["legs"]["leg4"].items()
                 if k.startswith("W%d" % (wave + 1)) or k.startswith("hops")},
        "receipt": rec.get("_receipt_path"),
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))