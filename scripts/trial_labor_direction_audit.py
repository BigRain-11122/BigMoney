#!/usr/bin/env python
"""Trial-labor REFORM gate direction audit (read-only census).

Why this face exists
--------------------
`trial_labor_w20.py judge-finalize` publishes a REFORM face whose
`eligible_reform` list is decided by `science_gates.g2_reform_fdr4d`:
batch BH-FDR over `batch_p_values` AND a complete four-dimension
composite score.  The p-values come from `tl2._dual_nulls_w2`, whose
sign-flip leg is **two-sided**:

    p_two = mean(|perms| >= |mu|)

so a strategy that loses money *reliably* has p -> 0 exactly like one
that makes money reliably.  The composite dimensions
(`reform_composite_scores`) are batch-internal percentile scores, so
"composite 0.24" is a *relative rank*, not an absolute bar.

Consequence: the reform channel has no sign test at all.  W20 is the
first wave in W17..W21 where `eligible_reform` is non-empty, and both
of its members are negative-carry arms:

    W20-A-0003  sharpe_full_L -1.2957  annualized -10.81%
    W20-B-0019  sharpe_full_L -1.4119  annualized -12.45%

and `trial_labor_w20.py intake` then puts them on the paper-probation
onboarding list (TRIAL-ENTRYGRM-01/02).  That is a real defect in the
funnel, not a modelling disagreement: the gate answered "this arm is
different from zero" and the funnel read it as "this arm is worth
watching".

This face does not change any frozen verdict and does not touch the
reform gate.  It is the cheap missing question, asked mechanically
across every wave that has a reform face:

    of the members the reform gate admitted, how many carry a
    non-positive expected return?

Output is descriptive; the defect line names wave + cell + magnitudes
so a human can decide whether to bind a direction gate into the prereg
template (that decision is a science-gate change, not this script's).

Exit codes: `run` returns 0 whenever the face was published -- a named
defect is *content* (verdict + `known_defect`), never a process failure,
because a leg that stays red every round trains readers to ignore red
(r1789 family).  `check` returns 3 on face/fresh disagreement.
`build()` still returns 3 internally so selftest can prove it speaks.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

OUT_JSON = "results/trial_labor_direction_audit.json"
OUT_MD = "research/TRIAL-LABOR-DIRECTION-AUDIT.md"

# Absolute-return read: the `ret` block written by every w1x/w2x runner
# (same key names across W17..W21 -- verified by this face's own scan).
SHARPE_KEY = "sharpe_full_L"
ANN_KEY = "annualized_ret_L"


def _j(obj):
    return json.loads(json.dumps(obj, ensure_ascii=False, default=float))


def _reform_faces():
    pat = os.path.join(ROOT, "results", "trial_labor_w*", "w*_reform_face.json")
    return sorted(glob.glob(pat))


def _wave_of(path):
    # .../results/trial_labor_w20/w20_reform_face.json -> TRIAL_LABOR_W20
    d = os.path.basename(os.path.dirname(path))
    tag = d.replace("trial_labor_", "").upper()
    return f"TRIAL_LABOR_{tag}"


def audit_face(path):
    """One reform face -> row dict.  Never raises on absent optional keys;
    a missing ret dimension is a REFUSE-worthy face bug, reported as
    `dim_missing` so the caller can exit 2 instead of silently counting
    zero negatives."""
    with open(path, encoding="utf-8") as fh:
        face = json.load(fh)
    eligible = list(face.get("eligible_reform") or [])
    metrics = face.get("member_metrics") or {}
    g2 = (face.get("g2_reform") or {}).get("members") or {}
    rows, dim_missing = [], []
    for cid in eligible:
        m = metrics.get(cid) or {}
        ret = m.get("ret")
        if not isinstance(ret, dict) or SHARPE_KEY not in ret:
            dim_missing.append(cid)
            rows.append({"cell_id": cid, "sharpe_full_L": None,
                         "annualized_ret_L": None,
                         "composite": (g2.get(cid) or {}).get("composite"),
                         "bh_q": (g2.get(cid) or {}).get("bh_q"),
                         "sign": "UNKNOWN"})
            continue
        sh = ret.get(SHARPE_KEY)
        ann = ret.get(ANN_KEY)
        if sh is None:
            sign = "UNKNOWN"
        elif float(sh) > 0:
            sign = "POSITIVE"
        elif float(sh) == 0:
            sign = "FLAT"
        else:
            sign = "NEGATIVE"
        rows.append({"cell_id": cid,
                     "sharpe_full_L": float(sh) if sh is not None else None,
                     "annualized_ret_L": float(ann) if ann is not None else None,
                     "composite": (g2.get(cid) or {}).get("composite"),
                     "bh_q": (g2.get(cid) or {}).get("bh_q"),
                     "sign": sign})
    onboarding = [a.get("cell_id") for a in (face.get("onboard_list") or [])]
    n_neg = sum(1 for r in rows if r["sign"] == "NEGATIVE")
    n_pos = sum(1 for r in rows if r["sign"] == "POSITIVE")
    n_unk = sum(1 for r in rows if r["sign"] == "UNKNOWN")
    return {"wave": _wave_of(path),
            "face": os.path.relpath(path, ROOT).replace("\\", "/"),
            "evidence_cutoff": face.get("evidence_cutoff"),
            "n_eligible_reform": len(eligible),
            "n_negative": n_neg,
            "n_positive": n_pos,
            "n_unknown": n_unk,
            "dim_missing": dim_missing,
            "onboard_cells": onboarding,
            "onboard_are_negative": [c for c in onboarding
                                     if any(r["cell_id"] == c
                                            and r["sign"] == "NEGATIVE"
                                            for r in rows)],
            "members": rows}


def build():
    faces = _reform_faces()
    if not faces:
        return {"verdict": "REFUSE_NO_REFORM_FACES", "faces": [],
                "n_faces": 0}, 2
    rows = [audit_face(p) for p in faces]
    total_elig = sum(r["n_eligible_reform"] for r in rows)
    total_neg = sum(r["n_negative"] for r in rows)
    total_unk = sum(r["n_unknown"] for r in rows)
    offenders = [r for r in rows if r["n_negative"] > 0]
    onboarding_neg = [r for r in rows if r["onboard_are_negative"]]
    dim_missing = [r["wave"] for r in rows if r["dim_missing"]]
    if any(r["n_eligible_reform"] for r in rows) and total_neg == 0 \
            and total_unk == 0 and not dim_missing:
        verdict = "REFORM_ADMITTED_MEMBERS_ARE_ALL_POSITIVE"
    elif offenders:
        verdict = "DIRECTION_BLIND_MEMBERS_NAMED"
    elif dim_missing:
        verdict = "REFUSE_REFORM_FACE_MISSING_RET_DIMENSION"
    else:
        verdict = "NO_REFORM_ADMISSIONS_IN_WINDOW"
    cuts = sorted({r["evidence_cutoff"] for r in rows if r["evidence_cutoff"]})
    out = {
        "tool": "trial_labor_direction_audit",
        "verdict": verdict,
        "known_defect": verdict in ("DIRECTION_BLIND_MEMBERS_NAMED",
                                    "REFUSE_REFORM_FACE_MISSING_RET_DIMENSION"),
        "n_faces": len(rows),
        "n_eligible_reform_total": total_elig,
        "n_negative_total": total_neg,
        "n_positive_total": sum(r["n_positive"] for r in rows),
        "n_unknown_total": total_unk,
        "waves_with_negative_admissions": [r["wave"] for r in offenders],
        "waves_onboarding_negative": [r["wave"] for r in onboarding_neg],
        "faces_missing_ret_dimension": dim_missing,
        "evidence_cutoff": cuts[-1] if cuts else None,
        "why_it_matters": (
            "g2_reform_fdr4d's p-values are two-sided (tl2._dual_nulls_w2: "
            "p = mean(|perms| >= |mu|)) and reform_composite_scores are "
            "batch-internal percentiles, so a reliably-losing arm passes "
            "FDR and ranks inside the batch. No sign test exists anywhere "
            "in the reform funnel."),
        "faces": rows,
    }
    rc = 3 if (offenders or dim_missing) else 0
    return out, rc


def render_md(out):
    L = []
    L.append("# 试用劳动力 reform 通道方向审计")
    L.append("")
    L.append(f"- 判词：**{out['verdict']}**")
    L.append(f"- 生成口径：{out['n_faces']} 张 reform 面；"
             f"admitted={out['n_eligible_reform_total']}、"
             f"负向={out['n_negative_total']}、"
             f"正向={out['n_positive_total']}、"
             f"读不出={out['n_unknown_total']}")
    L.append(f"- evidence_cutoff：{out['evidence_cutoff']}")
    L.append("")
    L.append("## 为什么会有这张面")
    L.append("")
    L.append(out["why_it_matters"])
    L.append("")
    L.append("## 逐波读数")
    L.append("")
    L.append("| wave | admitted | 负 | 正 | 读不出 | 上名单的负向 cell | cutoff |")
    L.append("|---|---|---|---|---|---|---|")
    for r in out["faces"]:
        L.append(f"| {r['wave']} | {r['n_eligible_reform']} | "
                 f"{r['n_negative']} | {r['n_positive']} | {r['n_unknown']} | "
                 f"{', '.join(r['onboard_are_negative']) or '—'} | "
                 f"{r['evidence_cutoff']} |")
    L.append("")
    neg = [r for r in out["faces"] if r["n_negative"]]
    if neg:
        L.append("## 负向成员逐笔")
        L.append("")
        L.append("| wave | cell | sharpe_full_L | annualized | composite | BH q | 在名单上 |")
        L.append("|---|---|---|---|---|---|---|")
        for r in neg:
            for m in r["members"]:
                if m["sign"] != "NEGATIVE":
                    continue
                on = "是" if m["cell_id"] in r["onboard_cells"] else "否"
                L.append(f"| {r['wave']} | {m['cell_id']} | "
                         f"{m['sharpe_full_L']} | {m['annualized_ret_L']} | "
                         f"{m['composite']} | {m['bh_q']} | {on} |")
        L.append("")
    L.append("## 边界（如实）")
    L.append("")
    L.append("- 只读：不改任何已冻结判决、不碰 reform 门、不改 intake 面。")
    L.append("- 判据只读 `ret.sharpe_full_L` / `ret.annualized_ret_L` 两块，"
             "不重算成本、不重算 null —— 方向是这张面唯一要回答的问题。")
    L.append("- `sharpe == 0` 记 FLAT 不计入负向（本窗口未出现）。")
    L.append("- 修不修 = 科学门改动（给 prereg 模板加方向门），须 GM 署名，"
             "不在本脚本射程。")
    L.append("")
    return "\n".join(L) + "\n"


def cmd_run():
    out, rc = build()
    p = os.path.join(ROOT, OUT_JSON)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(_j(out), fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    mp = os.path.join(ROOT, OUT_MD)
    with open(mp, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(render_md(out))
    print(f"verdict: {out['verdict']}")
    print(f"faces {out['n_faces']} | admitted {out['n_eligible_reform_total']} "
          f"| negative {out['n_negative_total']} | positive "
          f"{out['n_positive_total']} | unknown {out['n_unknown_total']}")
    if out["waves_onboarding_negative"]:
        print("onboarding-negative waves: "
              + ", ".join(out["waves_onboarding_negative"]))
    print(f"products: {OUT_JSON} + {OUT_MD}")
    # named defect is content, not process failure (see module docstring)
    return 0


def cmd_check():
    p = os.path.join(ROOT, OUT_JSON)
    if not os.path.exists(p):
        print(f"CHECK FAILED: {OUT_JSON} missing -- run first", flush=True)
        return 2
    with open(p, encoding="utf-8") as fh:
        old = json.load(fh)
    fresh, rc = build()
    diffs = []
    for k in ("verdict", "n_faces", "n_eligible_reform_total",
              "n_negative_total", "n_positive_total", "n_unknown_total"):
        if old.get(k) != fresh.get(k):
            diffs.append(f"{k}: face={old.get(k)!r} fresh={fresh.get(k)!r}")
    old_m = {(r["wave"], m["cell_id"]): m["sign"]
             for r in old.get("faces", []) for m in r.get("members", [])}
    new_m = {(r["wave"], m["cell_id"]): m["sign"]
             for r in fresh["faces"] for m in r["members"]}
    if old_m != new_m:
        only_old = sorted(set(old_m) - set(new_m))
        only_new = sorted(set(new_m) - set(old_m))
        flip = sorted(k for k in set(old_m) & set(new_m)
                      if old_m[k] != new_m[k])
        diffs.append(f"member rows drift: gone={only_old[:5]} "
                     f"new={only_new[:5]} flipped={flip[:5]}")
    if diffs:
        print("CHECK FAILED: " + " | ".join(diffs), flush=True)
        return 3
    print(f"CHECK OK: {old['verdict']} | faces {old['n_faces']} | "
          f"admitted {old['n_eligible_reform_total']} | negative "
          f"{old['n_negative_total']}")
    return 0


def cmd_selftest():
    import tempfile
    legs, fails = [], []

    def leg(name, cond, detail=""):
        legs.append((name, bool(cond), detail))
        if not cond:
            fails.append(name)

    def synth(tmp, wave, members, eligible, onboard=None):
        face = {"wave": wave, "evidence_cutoff": "2026-01-02",
                "member_metrics": members,
                "eligible_reform": eligible,
                "onboard_list": onboard or [],
                "g2_reform": {"members": {c: {"composite": 0.2, "bh_q": 0.01}
                                          for c in eligible}}}
        p = os.path.join(tmp, "results", f"trial_labor_{wave.lower()}",
                         f"{wave.lower()}_reform_face.json")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as fh:
            json.dump(face, fh)
        return p

    pos = {"ret": {SHARPE_KEY: 1.5, ANN_KEY: 0.12}}
    neg = {"ret": {SHARPE_KEY: -1.4, ANN_KEY: -0.12}}
    flat = {"ret": {SHARPE_KEY: 0.0, ANN_KEY: 0.0}}
    no_ret = {"robust": {}}

    with tempfile.TemporaryDirectory() as tmp:
        global ROOT
        keep = ROOT
        ROOT = tmp
        try:
            # leg 1: a negative admission is named, not silently counted
            synth(tmp, "W90", {"C1": neg, "C2": pos}, ["C1"],
                  [{"cell_id": "C1"}])
            out, rc = build()
            leg("negative admission -> verdict names it",
                out["verdict"] == "DIRECTION_BLIND_MEMBERS_NAMED" and rc == 3,
                str(out["verdict"]))
            leg("negative admission -> onboard flagged",
                out["waves_onboarding_negative"] == ["TRIAL_LABOR_W90"])

            # leg 2: all-positive admissions are clean, rc 0
            synth(tmp, "W91", {"C1": pos}, ["C1"], [{"cell_id": "C1"}])
            for f in glob.glob(os.path.join(tmp, "results", "trial_labor_w9*",
                                            "*_reform_face.json")):
                if "w90" in f:
                    os.remove(f)
            out2, rc2 = build()
            leg("all-positive -> clean verdict",
                out2["verdict"] == "REFORM_ADMITTED_MEMBERS_ARE_ALL_POSITIVE"
                and rc2 == 0, f"{out2['verdict']} rc={rc2}")

            # leg 3: flat (sharpe == 0) is not negative
            synth(tmp, "W92", {"C1": flat}, ["C1"])
            for f in glob.glob(os.path.join(tmp, "results", "trial_labor_w91",
                                            "*_reform_face.json")):
                os.remove(f)
            out3, rc3v = build()
            leg("flat is not counted as negative",
                out3["n_negative_total"] == 0 and out3["n_unknown_total"] == 0)

            # leg 4: missing ret dimension refuses instead of counting zero
            synth(tmp, "W93", {"C1": no_ret}, ["C1"])
            for f in glob.glob(os.path.join(tmp, "results", "trial_labor_w92",
                                            "*_reform_face.json")):
                os.remove(f)
            out4, rc4 = build()
            leg("missing ret dim -> REFUSE verdict + rc!=0",
                out4["verdict"] == "REFUSE_REFORM_FACE_MISSING_RET_DIMENSION"
                and rc4 == 3 and out4["faces_missing_ret_dimension"],
                out4["verdict"])

            # leg 5: no faces at all -> REFUSE_NO_REFORM_FACES rc 2
            for f in glob.glob(os.path.join(tmp, "results", "trial_labor_w93",
                                            "*_reform_face.json")):
                os.remove(f)
            out5, rc5 = build()
            leg("no faces -> REFUSE_NO_REFORM_FACES rc 2",
                out5["verdict"] == "REFUSE_NO_REFORM_FACES" and rc5 == 2)

            # leg 6: empty eligible list on an existing face is a legal
            # zero wave, not a refuse
            synth(tmp, "W94", {"C1": pos}, [])
            out6, rc6 = build()
            leg("empty eligible on a real face -> legal zero wave",
                out6["verdict"] == "NO_REFORM_ADMISSIONS_IN_WINDOW"
                and rc6 == 0, out6["verdict"])
        finally:
            ROOT = keep

    # leg 7: the real repo scan reproduces the published face verbatim
    real, _ = build()
    p = os.path.join(ROOT, OUT_JSON)
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            pub = json.load(fh)
        leg("published face agrees with a fresh build",
            pub.get("verdict") == real["verdict"]
            and pub.get("n_eligible_reform_total")
            == real["n_eligible_reform_total"]
            and pub.get("n_negative_total") == real["n_negative_total"])
    else:
        leg("published face exists", False, "run first")

    # leg 8: the direction-blind reason actually names the two-sided math
    leg("why_it_matters names the two-sided test",
        "two-sided" in real["why_it_matters"]
        and "|perms|" in real["why_it_matters"])

    for name, ok, detail in legs:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}"
              + (f"  ({detail})" if detail and not ok else ""))
    print(f"selftest {len(legs) - len(fails)}/{len(legs)} PASS")
    return 0 if not fails else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("run")
    sub.add_parser("check")
    sub.add_parser("selftest")
    a = ap.parse_args(argv)
    if a.cmd == "run":
        return cmd_run()
    if a.cmd == "check":
        return cmd_check()
    if a.cmd == "selftest":
        return cmd_selftest()
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
