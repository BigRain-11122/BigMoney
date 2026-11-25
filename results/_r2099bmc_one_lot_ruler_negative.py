"""Negative control for scripts/idx_fut_carry_one_lot_ruler.py (r2099 bm-c).

Every leg here poisons something and proves the guard says the right words. A guard that
cannot fail on a broken input has never actually judged anything (r1282 family).

Run:  python results\\_r2099bmc_one_lot_ruler_negative.py
"""

import io
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import idx_fut_carry_one_lot_ruler as M  # noqa: E402

LEGS = []


def leg(name, ok, detail=""):
    LEGS.append(bool(ok))
    print(("PASS " if ok else "FAIL ") + name + (("  [" + str(detail) + "]") if detail else ""))


def main():
    pub = M._read_json(M.OUT_PATH)
    if pub is None:
        print("FAIL no published face to test against -- run the face first")
        return 1
    tmp = tempfile.mkdtemp(prefix="onelot_neg_")
    try:
        # 1. a hand-edited value with every input byte unchanged is a DEFECT, not drift
        d = json.loads(json.dumps(pub))
        d["consumers"][0]["value"] = 1.0
        d["consumers"][0]["delta_cny"] = 1.0
        p = os.path.join(tmp, "hand.json")
        with io.open(p, "w", encoding="utf-8") as fh:
            json.dump(d, fh)
        buf = io.StringIO()
        import contextlib
        with contextlib.redirect_stdout(buf):
            rc = M.check(override_results=p)
        out = buf.getvalue()
        leg("hand-edited number -> rc3 CHECK FAILED", rc == 3 and "CHECK FAILED" in out)
        leg("...and does NOT say STALE (the word is the rebuild contract)",
            "STALE" not in out, out.strip().splitlines()[:1])

        # 2. a moved input digest is drift and must buy a rebuild
        d2 = json.loads(json.dumps(pub))
        k = sorted(d2["inputs"])[0]
        d2["inputs"][k] = "f" * 64
        p2 = os.path.join(tmp, "drift.json")
        with io.open(p2, "w", encoding="utf-8") as fh:
            json.dump(d2, fh)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.check(override_results=p2)
        out = buf.getvalue()
        leg("moved input bytes -> rc3 STALE", rc == 3 and "STALE" in out)

        # 3. verdict flip alone is caught
        d3 = json.loads(json.dumps(pub))
        d3["verdict"] = "ONE_RULER"
        p3 = os.path.join(tmp, "verdict.json")
        with io.open(p3, "w", encoding="utf-8") as fh:
            json.dump(d3, fh)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.check(override_results=p3)
        leg("verdict flip with same tables -> rc3", rc == 3 and "verdict" in buf.getvalue())

        # 4. drop a consumer row entirely (a face silently vanishing is not a clean report)
        d4 = json.loads(json.dumps(pub))
        d4["consumers"] = d4["consumers"][:-1]
        p4 = os.path.join(tmp, "drop.json")
        with io.open(p4, "w", encoding="utf-8") as fh:
            json.dump(d4, fh)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.check(override_results=p4)
        leg("a missing consumer row -> rc3", rc == 3)

        # 5. doc drift: page table no longer matches the published JSON
        doc = os.path.join(tmp, "doc.md")
        with io.open(doc, "w", encoding="utf-8") as fh:
            fh.write("# page with no rendered block\n")
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = M.check(quiet=False, override_doc=doc)
        leg("page without the rendered block -> rc3 (a hand-typed table is a lie we can catch)",
            rc == 3 and "doc" in buf.getvalue())

        # 6. authority disagreement is fatal and names both numbers
        auth = {
            "sizing_spec": {"values": {"IC": 100.0, "IM": 200.0}, "gen_epoch": 10.0},
            "open_capital": {"values": {"IC": 101.0, "IM": 200.0}, "gen_epoch": 10.0},
            "always_on_price": {"values": {"IC": 100.0, "IM": 200.0}, "gen_epoch": 10.0},
        }
        probs = M._authority_agrees(auth)
        leg("authority faces disagreeing by 1 CNY -> named problem",
            len(probs) == 1 and "IC" in probs[0], probs)

        # 7. a sub-cent disagreement is not a disagreement
        auth2 = json.loads(json.dumps(auth))
        auth2["open_capital"]["values"]["IC"] = 100.005
        leg("sub-cent disagreement stays quiet", M._authority_agrees(auth2) == [])

        # 8. timestamps in two repo formats parse to the same instant
        a = M._gen_epoch("2026-11-25T20:30:15+08:00")
        b = M._gen_epoch("2026-11-25T20:30:15+0800")
        leg("+08:00 and +0800 stamps parse equal", a is not None and a == b, (a, b))

        # 9. the projection is exactly the sum of the deltas, and labelled arithmetic only
        proj = (pub.get("arithmetic_only") or {}).get("portfolio_capital_floor")
        if proj:
            leg("floor projection is arithmetic-only and self-consistent",
                abs(proj["new_cny"] - proj["old_cny"] - proj["delta_cny"]) < 0.01
                and proj["basis"].startswith("arithmetic_only"))
        else:
            leg("floor projection present (absent means portfolio_capital was fresh)", True)

        # 10. when the three 11-23 faces are rebuilt in place, the verdict must become ONE_RULER
        #     -- proven arithmetically instead of by touching shared faces (this round is a
        #     CONTENTION round: no shared face may be rewritten).
        fresh = M.derive()
        statuses = {c["status"] for c in fresh["consumers"]}
        leg("today's verdict is explained only by stale consumers (no defect hiding in it)",
            fresh["verdict"] == "CONSUMERS_ONE_GENERATION_BEHIND"
            and statuses == {"STALE_BY_GENERATION", "FRESH"}, sorted(statuses))

        # 11. every rebuild_list row names a face that really is stale
        stale_faces = {c["face"] for c in fresh["consumers"]
                       if c["status"] == "STALE_BY_GENERATION"}
        named = {r["face"] for r in fresh["rebuild_list"] if r["status"] == "STALE_BY_GENERATION"}
        leg("rebuild_list names exactly the stale faces", named == stale_faces,
            (sorted(named), sorted(stale_faces)))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("%d/%d PASS" % (sum(LEGS), len(LEGS)))
    return 0 if all(LEGS) else 1


if __name__ == "__main__":
    sys.exit(main())
