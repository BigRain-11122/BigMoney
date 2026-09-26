"""T-85 s1 NAV HARVEST (CEO order O-20260926-2320, 24h saturation directive).

Full-history daily NAV series for every fusion-tournament candidate member
under the frozen engine:
  - 28 base members = 6 CE employees + 22 PROSPECT (t27 FROZEN_ROSTER),
    specs pinned to the t56_caliber_registry snapshot (r256 A1 law: live
    registry may carry post-freeze wiring; the frozen snapshot is the
    reproducible basis).
  - 2 T-78 wired exit-overlay faces (ov_tp_ladder / ov_full) x 6 CE
    carriers (exit_overlay_p1 frozen CELLS specs).
Cost faces: x1 (COST_X1_RATE) and x2 (CostPatch(2)) per ticket s1.

Derivation face ONLY (zero judgment, zero paper eligibility): prereg freeze
is due BEFORE the s2/s3 fusion-grid judged runs (R99 law); ledger +0
(anchor-replay precedent, t24); every line carries provenance. NAVs are
hard-anchored fail-closed against the caliber snapshot recorded evidence
(CE: backtest.in_sample/out_sample/cost_x2 via p3.anchor_checks; PROSPECT:
prospect.recorded_*; overlay x2: results/exit_overlay_p1.json stress_x2) --
any drift = exit 2, zero products.

CLI: run | selftest   (idempotent: complete census on disk -> exit 0 no-op;
      FUSION_P1_NAV_REFINALIZE=1 = only redo)
"""
import hashlib
import json
import os
import sys
import time
from contextlib import nullcontext

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pandas as pd
import numpy as np

from config import PATHS
import ew6_portfolio as E
from iv6_portfolio import _init_worker
from parallel_runner import run_cells_parallel, worker_cap
from live import paper as lp
from live.paper import (OOS_START, evidence_cutoff, build_panels,
                        seg_metrics, _evidence_matches)
import p3_portfolio
from p3_portfolio import member_run, anchor_checks
from science_gates import CostPatch
from engine import run_backtest
from exit_overlay_p1 import CARRIERS, CELLS
from t27_blend_tournament import FROZEN_ROSTER

ROOT = PATHS.root
CAL_DIR = os.path.join(ROOT, "results", "t56_caliber_registry")
TRADER_DIR = os.path.join(CAL_DIR, "firm", "traders")
MANIFEST = os.path.join(CAL_DIR, "_manifest.json")
OUT_DIR = os.path.join(ROOT, "results", "fusion_p1")
NAVS_JSONL = os.path.join(OUT_DIR, "navs.jsonl")
SUMMARY_JSON = os.path.join(OUT_DIR, "navs_summary.json")
ANCHOR_JSON = os.path.join(OUT_DIR, "anchor_report.json")
OV_REF = os.path.join(ROOT, "results", "exit_overlay_p1.json")
BATCH = "FUSION-P1-NAV"
ANCHOR_TOL = lp.ANCHOR_TOL
CE6 = FROZEN_ROSTER[:6]
FUSION_FACES = ("ov_tp_ladder", "ov_full")   # ticket s1: T-78 wired faces
EVIDENCE_CUTOFF = "2026-09-22"   # operative per-member frozen truncation


def _sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _manifest_ok() -> dict:
    """Dual-gate hash verify (R253 law: raw first, LF-normalized second --
    git EOL transport must not fake-drift the pin). Manifest keys are bare
    filenames resolved under firm/traders/ (empirical r277 probe)."""
    with open(MANIFEST, encoding="utf-8") as f:
        man = json.load(f)
    files = man.get("files") or {}
    bad = []
    for rel, want in files.items():
        p = os.path.join(TRADER_DIR, rel)
        if not os.path.exists(p):
            bad.append({"file": rel, "reason": "absent"})
            continue
        raw = open(p, "rb").read()
        cands = {_sha(raw), _sha(raw.replace(b"\r\n", b"\n"))}
        if str(want) not in cands:
            bad.append({"file": rel, "reason": "hash-mismatch",
                        "got_lfnorm": _sha(raw.replace(b"\r\n", b"\n"))[:16]})
    return {"source_commit": man.get("source_commit"), "n_files": len(files),
            "bad": bad, "ok": not bad}


def _wired_overlay_cells() -> list:
    """T-78 WIRED overlay member-faces = exactly the combos recorded in the
    frozen judgment artifact results/exit_overlay_p1.json stress_x2
    (r256 wiring: C01/C02 tp_ladder + C02/ENGULF ov_full) restricted to the
    ticket's two faces. Zero invention: the recorded set IS the census."""
    with open(OV_REF, encoding="utf-8") as f:
        sx2 = json.load(f).get("stress_x2") or {}
    cells = []
    for key in sorted(sx2):
        if ":" not in key:
            continue
        carrier, face = key.split(":", 1)
        if face in FUSION_FACES and carrier in CARRIERS:
            cells.append((face, carrier))
    return cells


def _load_caliber_trader(tid: str) -> dict:
    with open(os.path.join(TRADER_DIR, tid + ".json"), encoding="utf-8") as f:
        return json.load(f)


def _close(a, b, tol=ANCHOR_TOL) -> bool:
    if a is None or b is None:
        return False
    return abs(float(a) - float(b)) < tol


def _member_anchor(t: dict, r1: dict, r2: dict) -> dict:
    """CE: p3.anchor_checks verbatim; PROSPECT: prospect.recorded_* face.

    ZERO-RUN AMENDMENT (r251 law; navs census never landed, crash pre-product
    2026-09-26 ~23:4x): 3 CE frozen specs (DROUGHT-CE-01 / ENGULF-CE-01 /
    NEEDLE-DE-01) registered their x2 evidence block as full-sharpe-only --
    cost_x2 = {sharpe, survive, note} with NO oos_sharpe key (live
    anchor_gate consumes the same face). p3.anchor_checks reads
    x2["oos_sharpe"] unconditionally (built for the oos-carrying specs) ->
    KeyError on those 3 members. For them the anchor runs the SAME verbatim
    legs (1x IS/OOS evidence match + x2 full-sharpe) with the x2 OOS leg an
    honest skip (want=None disclosed). No fabricated keys, no loosened tol."""
    bt = t.get("backtest") or {}
    if isinstance(bt, dict) and bt.get("in_sample") and bt.get("cost_x2"):
        x2 = bt["cost_x2"]
        if "oos_sharpe" in x2:
            ac = anchor_checks(t, r1, r2)
            return {"face": "backtest-block", "ok": bool(ac["anchor_ok"] and ac["x2_ok"]),
                    "got_is": ac["got_is"].get("sharpe"),
                    "want_is": bt["in_sample"].get("sharpe"),
                    "got_oos": ac["got_oos"].get("sharpe"),
                    "want_oos": bt["out_sample"].get("sharpe"),
                    "got_x2_full": ac["got_x2_full"], "want_x2_full": ac["want_x2_full"],
                    "got_x2_oos": ac["got_x2_oos"], "want_x2_oos": ac["want_x2_oos"]}
        got_is = {**seg_metrics(r1["eq"][r1["eq"].index < OOS_START]),
                  "trades": r1["n_trades"] - r1["oos_trades"]}
        got_oos = {**r1["oos"], "trades": r1["oos_trades"]}
        a_ok = (_evidence_matches(got_is, bt["in_sample"])
                and _evidence_matches(got_oos, bt["out_sample"]))
        x_ok = abs(r2["full"]["sharpe"] - x2["sharpe"]) < ANCHOR_TOL
        return {"face": "backtest-block-x2full-only", "ok": bool(a_ok and x_ok),
                "got_is": got_is.get("sharpe"),
                "want_is": bt["in_sample"].get("sharpe"),
                "got_oos": got_oos.get("sharpe"),
                "want_oos": bt["out_sample"].get("sharpe"),
                "got_x2_full": r2["full"]["sharpe"], "want_x2_full": x2["sharpe"],
                "got_x2_oos": r2["oos"]["sharpe"], "want_x2_oos": None,
                "x2_oos_leg": ("absent-in-frozen-spec: full-sharpe-only x2 "
                               "registration, honest skip disclosed")}
    pr = t.get("prospect") or {}
    ok = (_close(r1["full"]["sharpe"], pr.get("recorded_full_sharpe"))
          and _close(r1["oos"]["sharpe"], pr.get("recorded_oos_sharpe"))
          and _close(r2["full"]["sharpe"], pr.get("recorded_x2_full_sharpe")))
    return {"face": "prospect-recorded", "ok": bool(ok),
            "got_full": r1["full"]["sharpe"], "want_full": pr.get("recorded_full_sharpe"),
            "got_oos": r1["oos"]["sharpe"], "want_oos": pr.get("recorded_oos_sharpe"),
            "got_x2_full": r2["full"]["sharpe"], "want_x2_full": pr.get("recorded_x2_full_sharpe")}


def _nav_line(member, family, cost_face, cost_mult, r, cutoff, extra=None):
    eq = r["eq"]
    line = {
        "member": member, "family": family, "cost_face": cost_face,
        "cost_mult": cost_mult, "evidence_cutoff": cutoff,
        "n_trades": int(r["n_trades"]), "oos_trades": int(r["oos_trades"]),
        "sharpe_full": round(float(r["full"]["sharpe"]), 4),
        "sharpe_oos": round(float(r["oos"]["sharpe"]), 4),
        "dates": [str(d.date()) for d in eq.index],
        "eq": [round(float(v), 6) for v in eq],
        "provenance": {
            "spec": "results/t56_caliber_registry/firm/traders/%s.json (manifest sha verified)" % member,
            "engine": "p3_portfolio.member_run (frozen primitive, evidence_cutoff truncation)",
            "cost": "x1=COST_X1_RATE" if cost_mult is None else "x2=CostPatch(2)",
        },
    }
    if extra:
        line.update(extra)
    return line


def member_job(tid: str) -> dict:
    """Worker fn: one base member, both cost faces + hard anchor (fail-closed
    face; the census gate in main() refuses the batch on any anchor drift)."""
    t = _load_caliber_trader(tid)
    pf = E.PRICES_FULL
    r1 = member_run(t, pf)
    r2 = member_run(t, pf, 2.0)
    fam = "CE6" if tid in CE6 else "PROSPECT"
    return {"tid": tid, "family": fam,
            "lines": [_nav_line(tid, fam, "x1", 1, r1, r1["cutoff"]),
                      _nav_line(tid, fam, "x2", 2, r2, r2["cutoff"])],
            "anchor": _member_anchor(t, r1, r2)}


def overlay_job(face: str, carrier: str) -> dict:
    """Worker fn: one T-78 overlay cell on its CE carrier, both cost faces.
    run_carrier semantics verbatim (params/patch merge, engine_kw additive),
    truncated at the carrier's frozen evidence_cutoff."""
    t = _load_caliber_trader(carrier)
    spec = CELLS[face]
    pf = E.PRICES_FULL
    cutoff = evidence_cutoff(t, pf)
    ps = pd.Timestamp(cutoff)
    prices = {s: df[df.index <= ps] for s, df in pf.items()}
    P = build_panels(prices)
    idx = P["close"].index
    entry = lp.SIGNAL_BUILDERS[t["params"]["entry"]](P)
    params = {k: v for k, v in t["params"].items() if k != "entry"}
    params = {**params, **spec["params"]}
    patch = {**dict(t.get("exit_overrides") or {}), **spec["patch"]}
    lines, got = [], {}
    for cost_face, cm in (("x1", None), ("x2", 2.0)):
        cctx = CostPatch(cm) if cm else nullcontext()
        with cctx, lp.ExitPatch(patch):
            res = run_backtest(prices, params, entry_signal=entry,
                               exit_signal=(entry <= 0), **spec["engine_kw"])
        eq = pd.Series(res["equity_curve"], index=idx[:len(res["equity_curve"])])
        oos_tr = sum(1 for tr in res["trades"] if str(tr["date"]) >= OOS_START)
        r = {"eq": eq, "full": lp.seg_metrics(eq),
             "oos": lp.seg_metrics(eq, OOS_START),
             "n_trades": res["metrics"]["num_trades"], "oos_trades": oos_tr}
        got[cost_face] = r
        lines.append(_nav_line(f"{carrier}:{face}", "OVERLAY", cost_face,
                               cm or 1, r, cutoff,
                               extra={"overlay_face": face, "carrier": carrier,
                                      "overlay_spec": {k: spec[k] for k in
                                                       ("params", "patch", "engine_kw")},
                                      "provenance": {
                                          "spec": "results/t56_caliber_registry/firm/traders/%s.json + exit_overlay_p1.CELLS[%s]" % (carrier, face),
                                          "engine": "exit_overlay_p1.run_carrier semantics (engine.run_backtest, engine_kw additive)",
                                          "cost": "x1=COST_X1_RATE" if cm is None else "x2=CostPatch(2)"}}))
    with open(OV_REF, encoding="utf-8") as f:
        want = (json.load(f).get("stress_x2") or {}).get(f"{carrier}:{face}") or {}
    x2_ok = (_close(got["x2"]["full"]["sharpe"], want.get("full_x2"))
             and _close(got["x2"]["oos"]["sharpe"], want.get("oos_x2")))
    struct_ok = all(len(r["eq"]) > 0 and r["n_trades"] >= 0 for r in got.values())
    return {"face": face, "carrier": carrier, "lines": lines,
            "anchor": {"face": "stress_x2-recorded", "ok": bool(x2_ok and struct_ok),
                       "got_x2_full": got["x2"]["full"]["sharpe"],
                       "want_x2_full": want.get("full_x2"),
                       "got_x2_oos": got["x2"]["oos"]["sharpe"],
                       "want_x2_oos": want.get("oos_x2")}, "struct_ok": struct_ok}


def run() -> int:
    os.makedirs(OUT_DIR, exist_ok=True)
    wired = _wired_overlay_cells()
    census_lines = len(FROZEN_ROSTER) * 2 + len(wired) * 2
    if (os.path.exists(NAVS_JSONL) and os.path.exists(SUMMARY_JSON)
            and not os.environ.get("FUSION_P1_NAV_REFINALIZE")):
        n = 0
        with open(NAVS_JSONL, encoding="utf-8") as f:
            for _ in f:
                n += 1
        if n == census_lines:
            print("fusion_p1_nav: complete census on disk -> idempotent no-op exit 0")
            return 0
    mv = _manifest_ok()
    if not mv["ok"]:
        print("fusion_p1_nav: caliber manifest verify FAIL", mv["bad"][:3])
        return 2
    jobs = ([("m:" + tid, member_job, (tid,)) for tid in FROZEN_ROSTER]
            + [("ov:%s:%s" % (face, c), overlay_job, (face, c))
               for face, c in wired])
    t0 = time.time()
    res = run_cells_parallel(jobs, workers=min(worker_cap(), 12),
                             desc="fusion-navs", initializer=_init_worker)
    workers = res.pop("__workers__", None)          # r259 contract key
    anchors, lines, fails = {}, [], []
    for key, payload in sorted(res.items()):
        anchors[key] = payload.get("anchor")
        if not payload.get("anchor", {}).get("ok"):
            fails.append({"key": key, "anchor": payload.get("anchor")})
        lines.extend(payload.get("lines") or [])
    with open(ANCHOR_JSON, "w", encoding="utf-8") as f:
        json.dump({"batch": BATCH, "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
                   "all_ok": not fails, "fails": fails,
                   "anchors": anchors}, f, indent=1, ensure_ascii=False)
    if fails or len(lines) != census_lines:
        print("fusion_p1_nav: anchor/census FAIL (%d fails, %d/%d lines) "
              "-- zero products" % (len(fails), len(lines), census_lines))
        return 2
    tmp = NAVS_JSONL + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(json.dumps(line, ensure_ascii=False) + "\n")
    os.replace(tmp, NAVS_JSONL)
    summary = {
        "batch": BATCH,
        "ticket_ref": "T-2026-09-26-85 s1 (O-20260926-2320)",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "evidence_cutoff": EVIDENCE_CUTOFF,
        "cutoff_note": ("operative truncation = per-member frozen evidence_cutoff "
                        "(caliber r256 A1 pin law); ticket cites the 2026-09-24 panel "
                        "availability face -- NAVs exclude post-09-22 bars by member law"),
        "members_census": {"CE6": len(CE6), "PROSPECT": len(FROZEN_ROSTER) - len(CE6),
                           "OVERLAY_WIRED_CELLS": len(wired)},
        "wired_overlay_cells": [f"{c}:{f}" for f, c in wired],
        "lines": len(lines), "faces": {"x1": len(lines) // 2, "x2": len(lines) // 2},
        "anchor_all_ok": True, "manifest": {"source_commit": mv["source_commit"],
                                            "n_files": mv["n_files"]},
        "audit": {"workers": workers, "elapsed_sec": round(time.time() - t0, 1)},
        "ledger": "+0 derivation face (anchor-replay t24 precedent; s2/s3 judged "
                  "grid owes its own prereg + N bill)",
        "navs_file": "results/fusion_p1/navs.jsonl",
    }
    with open(SUMMARY_JSON, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1, ensure_ascii=False)
    print("fusion_p1_nav: %d/%d lines harvested, anchors all-ok, workers=%s, %.1fs"
          % (len(lines), census_lines, workers, time.time() - t0))
    return 0


def selftest() -> int:
    """Hermetic pre-pooling gate (r263 law: compile+selftest before burn):
    file census + manifest dual-gate + frozen-spec keys + reference-face keys
    + schema round-trip + pure anchor math. Zero panel loads, zero engine."""
    cases = []

    def check(name, got, want=True):
        cases.append((name, got == want, got, want))

    # [1] roster census: 28 members, 6 CE head, caliber files all present
    check("roster len 28", len(FROZEN_ROSTER), 28)
    check("CE6 head 6", tuple(FROZEN_ROSTER[:6]) == tuple(CARRIERS), True)
    missing = [t for t in FROZEN_ROSTER
               if not os.path.exists(os.path.join(TRADER_DIR, t + ".json"))]
    check("caliber member files present", missing, [])
    # [2] manifest dual-gate hash verify (live files, read-only)
    mv = _manifest_ok()
    check("manifest verify (29 files, dual-gate)", (mv["ok"], mv["n_files"]),
          (True, 29))
    # [3] frozen overlay spec keys
    for face in FUSION_FACES:
        spec = CELLS.get(face)
        check(f"CELLS[{face}] keys",
              bool(spec) and all(k in spec for k in ("params", "patch", "engine_kw")))
    check("carriers 6", len(CARRIERS), 6)
    # [4] wired overlay cells: frozen T-78 judgment artifact = census truth
    wired = _wired_overlay_cells()
    check("wired overlay cells non-empty", len(wired) > 0)
    check("wired cells faces legal",
          all(f in FUSION_FACES and c in CARRIERS for f, c in wired))
    with open(OV_REF, encoding="utf-8") as f:
        sx2 = json.load(f).get("stress_x2") or {}
    check("wired cells recorded in stress_x2",
          all(f"{c}:{f}" in sx2 for f, c in wired))
    # [5] anchor faces resolvable on spec files (backtest or prospect)
    no_face = []
    for tid in FROZEN_ROSTER:
        t = _load_caliber_trader(tid)
        bt, pr = t.get("backtest") or {}, t.get("prospect") or {}
        if not (bt.get("in_sample") and bt.get("cost_x2")) and not pr.get("recorded_full_sharpe"):
            no_face.append(tid)
    check("every member has an anchor face", no_face, [])
    # [5b] x2-key census truth (r278 crash regression leg, r261 law): the
    # frozen specs split into oos-carrying vs full-sharpe-only x2 blocks;
    # the full-only set is byte-stable under the manifest dual-gate [2].
    full_only = sorted(
        tid for tid in FROZEN_ROSTER[:6]
        if isinstance((_load_caliber_trader(tid).get("backtest") or {})
                      .get("cost_x2"), dict)
        and "oos_sharpe" not in _load_caliber_trader(tid)["backtest"]["cost_x2"])
    check("x2 full-sharpe-only set (frozen truth)",
          full_only, ["DROUGHT-CE-01", "ENGULF-CE-01", "NEEDLE-DE-01"])
    # [5c] amendment branch pure math (hermetic synthetic faces; seg_metrics
    # needs >=20 bars and nonzero variance, live.paper F4 honesty law)
    idx5 = pd.date_range("2020-01-01", periods=60, freq="D")
    steps = 1.0 + np.linspace(0.001, 0.003, 60)
    eq5 = pd.Series(np.cumprod(steps), index=idx5)
    m_is = seg_metrics(eq5)
    m_oss = seg_metrics(eq5)
    r1s = {"eq": eq5, "cutoff": "2026-09-22", "n_trades": 40, "oos_trades": 10,
           "full": {"sharpe": 0.55}, "oos": {**m_oss, "trades": 10}}
    r2s = {"eq": eq5, "cutoff": "2026-09-22", "n_trades": 40, "oos_trades": 10,
           "full": {"sharpe": 0.59}, "oos": {**m_oss, "trades": 10}}
    bt5 = {"in_sample": {**m_is, "trades": 30},
           "out_sample": {**m_oss, "trades": 10},
           "cost_x2": {"sharpe": 0.59, "survive": True}}
    am = _member_anchor({"backtest": bt5}, r1s, r2s)
    check("amendment branch pass face",
          (am["face"], am["ok"], am["want_x2_oos"]),
          ("backtest-block-x2full-only", True, None))
    bt5d = {"in_sample": {**m_is, "trades": 30},
            "out_sample": {**m_oss, "trades": 10},
            "cost_x2": {"sharpe": 0.80, "survive": True}}
    amd = _member_anchor({"backtest": bt5d}, r1s, r2s)
    check("amendment branch drift refusal", amd["ok"], False)
    # [6] schema round-trip + pure anchor math
    line = {"member": "X", "cost_face": "x1", "eq": [1.0, 1.1], "dates": ["2020-01-01"]}
    check("jsonl line round-trip",
          json.loads(json.dumps(line, ensure_ascii=False)), line)
    check("_close pass", _close(0.5000, 0.5019), True)
    check("_close drift", _close(0.5000, 0.5030), False)
    check("_close none-face", _close(None, 0.5), False)
    n_pass = sum(1 for _, ok, _, _ in cases if ok)
    print(f"fusion_p1_nav selftest: {n_pass}/{len(cases)} PASS")
    for name, ok, got, want in cases:
        if not ok:
            print(f"  FAIL {name}: got={got} want={want}")
    return 0 if n_pass == len(cases) else 1


if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "run"
    if mode == "selftest":
        sys.exit(selftest())
    if mode == "run":
        sys.exit(run())
    print("usage: fusion_p1_nav.py run|selftest")
    sys.exit(2)
