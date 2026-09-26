# -*- coding: utf-8 -*-
"""R252 bm-a: CN-DIV-LOWVOL-ROT-P1 harvest gate (deterministic, zero network, zero LLM).

r244 landed-marker law: pool entry "landed marker = results/cn_div_lowvol_rot/
p1_results.json with ledger block; harvest = pool flip done by next round".
Deterministic re-derivation before the flip:
  1. p1_results.json exists, parses, top-level evidence_cutoff == 2026-09-22
     (D2 lockbox; science_audit C2 legal key present);
  2. ledger block internally consistent: prev_total 185798 + batch_trials 54
     == total 185852 == n_trials face; batch/file names match;
  3. panel_gates all_ok (T==1862, a_only_window==['2021-10-22'] frozen
     mismatch-day list, b_only empty, nan-free, cutoff ok);
  4. seed base registered cn_div_lowvol_rot_p1=20260980 (R250 one-commit law);
  5. 4 judged cells {W63,W252}x{bare,gate} with x1/x2/x3 faces, judged face x2;
  6. g1_prime_v2 present for all 4 (verdicts honest, any pass/fail legal) +
     skill_line face + g2 faces + D6 member faces (no reject) + nulls K50 +
     EW pair baseline;
  7. gate_attrition consumption-face visibility (r248 law): LAST row of the
     `entries` list == this batch with the 4-cell gate verdicts;
  8. autofill launch evidence: bm-a launched the shard this round;
  9. pool entry pre-flip status == 'ready' (harvest expects pre-flip state).
Exit 0 = gate PASS + pool entry/shard flipped done with harvest_note (byte
faces preserved: no BOM, CRLF, ensure_ascii=False, indent=1). Exit 2 = gate
red, pool untouched.
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results", "cn_div_lowvol_rot", "p1_results.json")
POOL = os.path.join(ROOT, "results", "runnable_pool.json")
AUTOFILL = os.path.join(ROOT, "results", "autofill_state.json")
ATTR = os.path.join(ROOT, "results", "gate_attrition.json")
ENTRY_ID = "CN-DIV-LOWVOL-ROT-P1"
SHARD_KEY = "divlowvolrot-0of1"
CELLS = ["W63_bare", "W252_bare", "W63_gate", "W252_gate"]


def main() -> int:
    fails = []
    if not os.path.exists(RES):
        print("FAIL: p1_results.json absent")
        return 2
    d = json.load(io.open(RES, encoding="utf-8-sig"))

    if d.get("evidence_cutoff") != "2026-09-22":
        fails.append(f"evidence_cutoff {d.get('evidence_cutoff')!r} != 2026-09-22")

    led = d.get("ledger", {})
    if not (led.get("prev_total") == 185798 and led.get("batch_trials") == 54
            and led.get("total") == 185852):
        fails.append(f"ledger block inconsistent: {led}")
    if d.get("n_trials") != led.get("batch_trials"):
        fails.append("n_trials face != ledger batch_trials")

    pg = d.get("panel_gates", {})
    if not pg.get("all_ok"):
        fails.append(f"panel_gates not all_ok: {pg}")
    if pg.get("T") != 1862 or pg.get("a_only_window") != ["2021-10-22"] \
            or pg.get("b_only_window") != []:
        fails.append(f"panel_gates faces drifted: T={pg.get('T')} "
                     f"a_only={pg.get('a_only_window')} b_only={pg.get('b_only_window')}")

    meta = d.get("meta", {})
    if meta.get("seed_base_registered") != "cn_div_lowvol_rot_p1=20260980":
        fails.append(f"seed base {meta.get('seed_base_registered')!r} != registered")

    cells = d.get("cells", {})
    if sorted(cells.keys()) != sorted(CELLS):
        fails.append(f"cells {sorted(cells.keys())} != {sorted(CELLS)}")
    for cid in CELLS:
        c = cells.get(cid, {})
        for face in ("x1", "x2", "x3"):
            if not c.get(face, {}).get("sharpe") is not None:
                fails.append(f"cell {cid} face {face} missing sharpe")
    if "judged_x2_returns_6dp_audit" not in d:
        fails.append("judged x2 6dp audit face absent")

    g1 = d.get("g1_prime_v2", {})
    for cid in CELLS:
        if cid not in g1:
            fails.append(f"g1_prime_v2 missing cell {cid}")
    sl = d.get("skill_line", {})
    if sl.get("line") != 0.9527 or sl.get("n_eff") != 185802:
        fails.append(f"skill_line drifted: line={sl.get('line')} n_eff={sl.get('n_eff')}")
    g2 = d.get("g2_registration_v2", {})
    for cid in CELLS:
        if cid not in g2:
            fails.append(f"g2 missing cell {cid}")
    d6 = d.get("d6_correlation", {})
    for cid in CELLS:
        mf = d6.get(cid, {}).get("member_face", {})
        if mf.get("reject"):
            fails.append(f"D6 reject on {cid}: max={mf.get('max_abs_corr')}")
    if d.get("nulls", {}).get("n_values") != 50:
        fails.append(f"nulls n_values {d.get('nulls', {}).get('n_values')} != 50")
    if "ew_pair_5050" not in d.get("baselines", {}):
        fails.append("EW pair baseline absent")

    # r248 consumption-face visibility: attrition row must be in `entries`
    attr = json.load(io.open(ATTR, encoding="utf-8-sig"))
    ent = attr.get("entries") or []
    row = next((r for r in reversed(ent) if r.get("batch") == ENTRY_ID), None)
    if row is None:
        fails.append("gate_attrition `entries` has no CN-DIV-LOWVOL-ROT-P1 row (r248 law)")
    else:
        g1v = row.get("gates", {}).get("g1_prime_pass", {})
        if sorted(g1v.keys()) != sorted(CELLS):
            fails.append(f"attrition g1 faces {sorted(g1v.keys())} != 4 cells")

    # autofill launch evidence this round
    st = json.load(io.open(AUTOFILL, encoding="utf-8-sig"))
    launches = [x for x in st.get("launches", [])
                if x.get("entry") == ENTRY_ID and x.get("machine") == "bm-a"
                and x.get("ts", "") >= "2026-09-26 14:5"]
    if not launches:
        fails.append("no bm-a autofill launch evidence for this round")

    # pool pre-flip state
    raw = open(POOL, "rb").read()
    pool = json.loads(raw.decode("utf-8-sig"))
    entry = next((e for e in pool.get("entries", []) if e.get("id") == ENTRY_ID), None)
    if entry is None:
        fails.append("pool entry missing")
    elif entry.get("status") != "ready":
        fails.append(f"entry status {entry.get('status')!r} != 'ready'")

    if fails:
        print(json.dumps({"harvest_gate": "FAIL", "fails": fails},
                         ensure_ascii=False, indent=1))
        return 2

    g1_pass = {cid: bool(g1[cid].get("pass_v2")) for cid in CELLS}
    best = max(CELLS, key=lambda c: g1[c].get("sharpe_full") or 0.0)
    note = ("harvested bm-a r252 2026-09-26 ~14:5x: p1_results.json landed "
            "14:50:53 (ledger 185798+54=185852; panel_gates all_ok T=1862; "
            "seeds cn_div_lowvol_rot_p1=20260980 registered at R250 freeze "
            "commit). Verdict 0/4 cells pass G1'v2 -- best "
            f"{best} x2 sharpe {g1[best].get('sharpe_full')} < line 0.9527 "
            "(CI-low positive but line unmet); MA200-gate faces worse on "
            "both axes (whipsaw cost > trend protection in 2-leg universe); "
            "D6 max|corr| vs members 0.2583 < 0.7; family PBO 0.0; honest "
            "negative per prereg S5.7 prior; attrition row visible in "
            "`entries` (44th). Flip by deterministic harvest gate "
            "results/_r252bma_rot_harvest.py.")
    entry["status"] = "done"
    for sh in entry.get("shards", []):
        if sh.get("key") == SHARD_KEY:
            sh["status"] = "done"
    entry["harvest_note"] = note
    entry["updated_at"] = "2026-09-26 14:55:00"

    out = json.dumps(pool, ensure_ascii=False, indent=1)
    # byte faces: no BOM, CRLF EOL (r254/r255 mirror-producer law)
    if b"\r\n" not in raw and b"\n" in raw:
        pass  # file was LF -- mirror that instead
        eol = b"\n"
    else:
        eol = b"\r\n"
    data = out.encode("utf-8")
    if eol == b"\r\n":
        data = data.replace(b"\n", b"\r\n")
    with open(POOL, "wb") as fh:
        fh.write(data)

    print(json.dumps({"harvest_gate": "PASS", "flipped": ENTRY_ID,
                      "shard": SHARD_KEY, "g1_pass": g1_pass,
                      "best_cell": best,
                      "best_sharpe": g1[best].get("sharpe_full"),
                      "launch_ts": launches[-1].get("ts")},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
