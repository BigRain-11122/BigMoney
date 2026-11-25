#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""negative controls for results/idx_fut_carry_ladder_stability.json (r2109).

Every control answers one question: *would this face notice if the thing it claims were
different?*  A face that only agrees with itself is not evidence (r1935).

1. positive        real face vs a fresh derivation -> CHECK_OK
2. number          one published number changed -> CHECK FAILED, and the word STALE absent
3. ladder drift     lattice digest changed -> STALE
4. leg drift        leg span/days changed -> STALE
5. sibling drift    sibling risk face digest changed -> STALE
6. token drift      verdict token changed -> CHECK FAILED
7. no cross-face    reconciliation block removed -> CHECK FAILED
8. formula          the ladder's own constants reproduce the published declared number
9. reader face      the page carries the verdict tokens a reader was promised
"""
from __future__ import annotations

import copy
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_ladder_stability as S  # noqa: E402

OUT = os.path.join(ROOT, "results", "idx_fut_carry_ladder_stability.json")
DOC = os.path.join(ROOT, "research", "IDX_FUT_CARRY_LADDER_STABILITY.md")

results = []


def ctl(name, cond, detail=""):
    results.append((name, bool(cond), detail))


def main():
    face = json.load(io.open(OUT, encoding="utf-8"))
    lattice = S.read_json(S.LATTICE)
    nav = float(lattice["nav_cny"])
    legs = {p: S.spread_leg(p) for p in ("IC", "IM")}
    leg_meta = {p: {"span": legs[p]["span"], "days": legs[p]["days"]} for p in legs}
    fresh, refusal = S.measure(legs, lattice, nav)
    assert not refusal, refusal
    fresh["cross_face"] = S.cross_face(fresh)

    lat_sha = S.digest(S.LATTICE)
    sib_sha = S.digest(S.SIBLING) if os.path.exists(S.SIBLING) else None

    # 1. positive control: the published face must pass against a fresh derivation
    rc, word, detail = S.classify(face, lat_sha, leg_meta, fresh, sib_sha)
    ctl("real face passes a fresh derivation", rc == 0 and word == "CHECK_OK", detail)

    # 2. a changed number must be a defect, not a drift -- and must not borrow STALE
    bad = copy.deepcopy(face)
    bad["headline"]["block_vol_full_pct"] = round(face["headline"]["block_vol_full_pct"] - 1.0, 3)
    rc, word, detail = S.classify(bad, lat_sha, leg_meta, fresh, sib_sha)
    ctl("tampered number -> CHECK FAILED without STALE",
        rc == 3 and word == "CHECK FAILED" and "STALE" not in word, detail)

    # 3/4/5. input drift is STALE, because the question it must answer is "is this the input
    # I priced", which no self-consistent recompute can answer
    rc, word, _d = S.classify(face, lat_sha + "0", leg_meta, fresh, sib_sha)
    ctl("ladder drift -> STALE", rc == 3 and word == "STALE")
    moved = {"IC": {"span": [leg_meta["IC"]["span"][0], leg_meta["IC"]["span"][1]], "days": 0},
             "IM": leg_meta["IM"]}
    rc, word, _d = S.classify(face, lat_sha, moved, fresh, sib_sha)
    ctl("leg drift -> STALE", rc == 3 and word == "STALE")
    rc, word, _d = S.classify(face, lat_sha, leg_meta, fresh, "deadbeef")
    ctl("sibling drift -> STALE", rc == 3 and word == "STALE")

    # 6/7. a flipped verdict or a dropped reconciliation is a defect
    tok = copy.deepcopy(face)
    tok["judgment"]["rho_stability"] = S.V_RHO_TIGHT
    rc, word, _d = S.classify(tok, lat_sha, leg_meta, fresh, sib_sha)
    ctl("token drift -> CHECK FAILED", rc == 3 and word == "CHECK FAILED")
    nocf = copy.deepcopy(face)
    nocf.pop("cross_face", None)
    rc, word, _d = S.classify(nocf, lat_sha, leg_meta, fresh, sib_sha)
    ctl("missing cross-face -> CHECK FAILED", rc == 3 and word == "CHECK FAILED")

    # 8. the declared number is the ladder's own formula, re-derived from its own notionals
    n = S.per_lot_notional(lattice)
    declared = (n["IC"] / nav + n["IM"] / nav) * S.DECLARED_L2_VOL_PCT
    ctl("ladder formula reproduces the declared block vol",
        abs(declared - face["headline"]["declared_block_vol_pct"]) <= 0.002,
        "%.4f vs %.3f" % (declared, face["headline"]["declared_block_vol_pct"]))

    # 9. the page a reader opens must carry the tokens, not only the JSON
    page = io.open(DOC, encoding="utf-8").read()
    j = face["judgment"]
    ctl("page carries all three tokens",
        all(t in page for t in (j["rho_stability"], j["stress_concentration"],
                                j["declaration_coverage"])))
    ctl("page carries the cross-face reconciliation",
        (face.get("cross_face") or {}).get("status", "?") in page)

    passed = sum(1 for _n, c, _d in results if c)
    for name, cond, detail in results:
        print(("%-52s %s %s" % (name, "PASS" if cond else "FAIL", detail)).rstrip())
    print("negative controls %d/%d %s"
          % (passed, len(results), "ALL_CONTROLS_PASS" if passed == len(results) else "CONTROLS_FAILED"))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
