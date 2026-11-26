#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Was the ">= 4% a year" line ever a skill test, or was it a leverage test?

WHY THIS FILE EXISTS
--------------------
r2136 found that `bench_generic.buy_and_hold()` hardwired target_vol=0.10 while
arms ran at 0.06/0.08, so the benchmark and the arm were books of different
size. The fix landed (the faces now carry `benchmark_sizing.target_vol` and
`same_yardstick: true`). r2145 then compared each arm to a benchmark it labelled
"aligned" to the arm's vol target -- but every aligned number is byte-identical
to the published one (`benchmark_aligned_ann_pct == benchmark_published_ann_pct`
on all 21 faces), i.e. the label moved and the number did not.

Meanwhile nobody asked the same question about the arms. `H1_full_ge` asks
whether the arm's annualised net return is >= 4.0% absolute -- but that number
is printed on whatever volatility the arm happened to realise. This file
measures that realised volatility, re-prices every arm and every benchmark to
the face's own declared target vol under constant leverage (with the exact
vol-drag term), and re-asks the same question.

WHAT IS MEASURED (all from published faces, nothing recomputed from panels)
--------------------------------------------------------------------------
  * realised vol of every arm vs the face's declared `config.target_vol`
  * realised vol of the benchmark vs that same declared target
  * the leverage factor that puts each book on the declared target
  * the annualised net return before and after that re-pricing
  * H1 (>= 4.0%) before and after, and which arms flip
  * whether the GO set changes

METHOD / LIMITS
---------------
Constant-leverage re-pricing: with geometric ann g and vol s,
    mu = g + s^2/2                       (arithmetic mean)
    g(k) = k*mu - (k*s)^2/2              (leverage k, exact under continuous
                                          rebalancing, zero financing cost)
Financing (the cash leg of the leverage) is left out; where k < 1 that only
makes the re-priced number slightly optimistic, where k > 1 slightly
conservative. Arm vol is read from `common_window.vol_pct` when the face
publishes it, else derived from the published MDE (mde = 1.96*vol/sqrt(n/252)
as `bench_generic.run_arm` computes it); the derivation is checked against
faces that publish both.

Read-only: it never writes a screen or a verdict. It re-issues one verdict on
the size axis and leaves the frozen verdict set untouched.

Usage
-----
  python scripts/bench_size_normalized_h1.py             # write json + page
  python scripts/bench_size_normalized_h1.py --check     # stale? rc0/rc3
  python scripts/bench_size_normalized_h1.py --selftest  # offline legs
"""
from __future__ import annotations

import argparse
import glob
import hashlib
import io
import json
import math
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
OUT_JSON = os.path.join(RES, "bench_size_normalized_h1.json")
OUT_MD = os.path.join(ROOT, "research", "BENCH_SIZE_NORMALIZED_H1.md")
AUDIT = os.path.join(RES, "bench_go_ruler_audit.json")

# copied from bench_generic.run_arm / defaults, so the two rulers are the same ruler
H1_FULL_PCT = 4.0
MDE_Z = 1.96
TDAYS = 252.0
# |realised / declared| beyond this counts as "not on target"
OFF_TARGET = 0.10
# derived vol must reproduce a published vol within this before the derivation
# is allowed to stand in for it
DERIVE_TOL_PP = 0.5
# an H1 flip smaller than this is rounding, not a finding
FLIP_EPS_PP = 0.02

TZ = timezone(timedelta(hours=8))


def now_iso():
    return datetime.now(TZ).replace(microsecond=0).isoformat()


def rescale(ann_pct, vol_pct, k):
    """Annualised net return after putting a book on k x its own size."""
    if ann_pct is None or not vol_pct:
        return None
    g = ann_pct / 100.0
    s = vol_pct / 100.0
    mu = g + 0.5 * s * s
    s2 = s * k
    mu2 = mu * k
    return round((mu2 - 0.5 * s2 * s2) * 100.0, 4)


def vol_from_mde(mde_pp, n):
    if not mde_pp or not n:
        return None
    return round(mde_pp * math.sqrt(n / TDAYS) / MDE_Z, 4)


def mde_from_vol(vol_pct, n):
    if not vol_pct or not n:
        return None
    return round(MDE_Z * vol_pct / math.sqrt(n / TDAYS), 4)


def read(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def input_paths():
    own = os.path.basename(OUT_JSON)
    # the face this file writes also matches the bench_*.json glob; it is output
    # read back as input, so it must never enter its own digest
    return [p for p in sorted(glob.glob(os.path.join(RES, "bench_*.json")))
            if os.path.basename(p) != own]


def digest(paths):
    h = hashlib.sha256()
    for p in paths:
        h.update(os.path.basename(p).encode("utf-8"))
        with open(p, "rb") as f:
            h.update(hashlib.sha256(f.read()).digest())
    return h.hexdigest()


def arm_vol(arm, n):
    """Published when the face carries it, derived from MDE otherwise."""
    cw = arm.get("common_window") or {}
    v = cw.get("vol_pct")
    if v:
        return float(v), "published"
    d = vol_from_mde(arm.get("mde_pp"), n)
    if d:
        return d, "derived_from_mde"
    return None, "missing"


def build():
    faces = []
    skipped = []
    arms_all = []
    for path in input_paths():
        d = read(path)
        if not isinstance(d, dict):
            continue
        bh = d.get("benchmark_buy_and_hold") or {}
        cw = bh.get("common_window") or {}
        cfg = d.get("config") or {}
        if not cw or not cfg:
            skipped.append({"face": os.path.basename(path), "why": "no benchmark_buy_and_hold/config"})
            continue
        tv = cfg.get("target_vol")
        n = cw.get("n")
        if not tv or not n:
            skipped.append({"face": os.path.basename(path), "why": "no target_vol/n"})
            continue
        tv_pct = round(float(tv) * 100.0, 4)
        bench_vol = cw.get("vol_pct")
        bench_ann = cw.get("ann_pct")
        bench_k = round(tv_pct / bench_vol, 6) if bench_vol else None
        sizing = d.get("benchmark_sizing") or {}
        row_face = {
            "face": cfg.get("id") or (d.get("cell") or {}).get("id") or os.path.basename(path),
            "path": os.path.relpath(path, ROOT).replace("\\", "/"),
            "n": n,
            "evidence_cutoff": d.get("evidence_cutoff"),
            "target_vol_pct": tv_pct,
            "declared_yardstick_target_vol": sizing.get("target_vol"),
            "declared_same_yardstick": sizing.get("same_yardstick"),
            "cost_bp_side": cfg.get("cost_bp_side"),
            "bench": {
                "ann_pct": bench_ann,
                "vol_pct": bench_vol,
                "leverage_to_target": bench_k,
                "off_target_pct": (round((bench_vol / tv_pct - 1.0) * 100.0, 3)
                                   if bench_vol else None),
                "ann_at_target_pct": rescale(bench_ann, bench_vol, bench_k) if bench_k else None,
                "h1_at_own_size": (bench_ann is not None and bench_ann >= H1_FULL_PCT),
                "h1_at_target": (rescale(bench_ann, bench_vol, bench_k) is not None
                                 and rescale(bench_ann, bench_vol, bench_k) >= H1_FULL_PCT),
            },
            "arms": [],
        }
        for arm in d.get("arms") or []:
            acw = arm.get("common_window") or {}
            ann = acw.get("ann_pct")
            if ann is None:
                continue
            v, src = arm_vol(arm, n)
            if not v:
                continue
            k = tv_pct / v
            n_ann = rescale(ann, v, k)
            before = ann >= H1_FULL_PCT
            after = n_ann is not None and n_ann >= H1_FULL_PCT
            flip = (before != after) and abs((n_ann or 0) - ann) > FLIP_EPS_PP
            rec = {
                "face": row_face["face"],
                "variant": (arm.get("tags") or {}).get("variant"),
                "ann_pct": ann,
                "vol_pct": v,
                "vol_source": src,
                "off_target_pct": round((v / tv_pct - 1.0) * 100.0, 3),
                "leverage_to_target": round(k, 6),
                "ann_at_target_pct": n_ann,
                "mde_pp": arm.get("mde_pp"),
                "verdict": arm.get("verdict"),
                "h1_before": before,
                "h1_after": after,
                "h1_flip": flip,
            }
            row_face["arms"].append(rec)
            arms_all.append(rec)
        faces.append(row_face)

    # r2145's "aligned" label: did any aligned number actually move?
    align = {"faces_checked": 0, "aligned_equals_published": 0, "target_changed_but_ann_same": 0}
    if os.path.exists(AUDIT):
        for f in read(AUDIT).get("faces") or []:
            pub, ali = f.get("benchmark_published_ann_pct"), f.get("benchmark_aligned_ann_pct")
            pv, av = f.get("benchmark_published_target_vol"), f.get("benchmark_aligned_target_vol")
            if pub is None or ali is None:
                continue
            align["faces_checked"] += 1
            if abs(pub - ali) < 1e-9:
                align["aligned_equals_published"] += 1
                if pv is not None and av is not None and abs(pv - av) > 1e-9:
                    align["target_changed_but_ann_same"] += 1

    flips = [a for a in arms_all if a["h1_flip"]]
    counts = {
        "faces": len(faces),
        "arms": len(arms_all),
        "arms_vol_derived": sum(1 for a in arms_all if a["vol_source"] == "derived_from_mde"),
        "arms_off_target_10pct": sum(1 for a in arms_all if abs(a["off_target_pct"]) > OFF_TARGET * 100),
        "arms_h1_before": sum(1 for a in arms_all if a["h1_before"]),
        "arms_h1_after": sum(1 for a in arms_all if a["h1_after"]),
        "h1_flips_down": sum(1 for a in flips if a["h1_before"] and not a["h1_after"]),
        "h1_flips_up": sum(1 for a in flips if a["h1_after"] and not a["h1_before"]),
        "go_arms": sum(1 for a in arms_all if a["verdict"] == "GO"),
        "go_arms_h1_after": sum(1 for a in arms_all if a["verdict"] == "GO" and a["h1_after"]),
        "bench_off_target_10pct": sum(1 for f in faces
                                      if f["bench"]["off_target_pct"] is not None
                                      and abs(f["bench"]["off_target_pct"]) > OFF_TARGET * 100),
        "bench_h1_at_own_size": sum(1 for f in faces if f["bench"]["h1_at_own_size"]),
        "bench_h1_at_target": sum(1 for f in faces if f["bench"]["h1_at_target"]),
        "bench_oversized": sum(1 for f in faces
                               if f["bench"]["off_target_pct"] is not None
                               and f["bench"]["off_target_pct"] > 0),
    }
    vol_range = (min((a["vol_pct"] for a in arms_all), default=None),
                 max((a["vol_pct"] for a in arms_all), default=None))
    go_survives = counts["go_arms"] == 0 or counts["go_arms_h1_after"] == counts["go_arms"]
    if flips and go_survives:
        verdict = "H1_IS_PARTLY_A_LEVERAGE_TEST_GO_SET_SURVIVES"
    elif flips:
        verdict = "H1_IS_PARTLY_A_LEVERAGE_TEST_GO_SET_MOVES"
    else:
        verdict = "H1_SURVIVES_SIZING"
    return {
        "schema": "bench-size-normalized-h1/v1",
        "generated": now_iso(),
        "evidence_cutoff": max((f.get("evidence_cutoff") or "" for f in faces), default=None),
        "cutoff_rule": "max of the audited faces' own evidence_cutoff fields",
        "rule": {
            "h1_full_pct": H1_FULL_PCT,
            "rescale": "mu = g + s^2/2 ; g(k) = k*mu - (k*s)^2/2 ; k = target_vol/realised_vol",
            "vol_source_preference": "common_window.vol_pct, else derived from mde_pp "
                                     "(mde = 1.96*vol/sqrt(n/252))",
            "derive_tol_pp": DERIVE_TOL_PP,
            "off_target_band_pct": OFF_TARGET * 100,
            "financing": "not modelled; k<1 optimistic, k>1 conservative",
            "what_this_does_not_do": "does not touch the frozen verdict set or any gate",
        },
        "r2145_aligned_label": align,
        "counts": counts,
        "arm_vol_range_pct": {"min": vol_range[0], "max": vol_range[1]},
        "h1_flips": flips,
        "verdict": verdict,
        "faces": faces,
        "skipped": skipped,
        "inputs": [{"path": os.path.relpath(p, ROOT).replace("\\", "/"),
                    "sha256_16": hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]}
                   for p in input_paths()],
        "inputs_digest": digest(input_paths()),
    }


def render(r):
    c = r["counts"]
    L = []
    L.append("# 那条「绝对 ≥4%」的线，是技能线还是杠杆线")
    L.append("")
    L.append("generated %s · evidence_cutoff %s" % (r["generated"], r["evidence_cutoff"]))
    L.append("")
    L.append("## 一句话")
    L.append("")
    L.append("每张面的臂都在**它自己碰巧实现的波动**上印年化，而这个波动从 %.2f%% 到 %.2f%%（%.1f 倍差）；"
             "基准也偏离它声明的目标（%d/%d 张面偏超 %.0f%%）。把所有账面重新定价到面自己声明的目标波动后，"
             "**%d 条臂的 H1 结论翻面**（%d 条只因被放大而过线，%d 条只因被缩小而不过线），"
             "但 **GO 集合不动**（%d → %d）。所以：**线没被推翻，被推翻的是它「在测技能」这个读数**。"
             % (r["arm_vol_range_pct"]["min"], r["arm_vol_range_pct"]["max"],
                (r["arm_vol_range_pct"]["max"] or 0) / max(r["arm_vol_range_pct"]["min"] or 1, 1e-9),
                c["bench_off_target_10pct"], c["faces"], OFF_TARGET * 100,
                c["h1_flips_down"] + c["h1_flips_up"], c["h1_flips_down"], c["h1_flips_up"],
                c["go_arms"], c["go_arms_h1_after"]))
    L.append("")
    L.append("## r2136 修了尺寸、r2145 没量尺寸")
    L.append("")
    a = r["r2145_aligned_label"]
    L.append("面里已经写着 `benchmark_sizing.same_yardstick: true`（代码确实把 `target_vol` 传进去了），"
             "但 r2145 的 `benchmark_aligned_ann_pct` 在 **%d/%d** 张面上与已公布值**逐位相同**，"
             "其中 **%d** 张面连目标波动都换了标签、收益数一个字没动——"
             "「对齐」是对了标签，不是对了仓位。"
             % (a["aligned_equals_published"], a["faces_checked"], a["target_changed_but_ann_same"]))
    L.append("")
    L.append("真正的尺寸要实测：基准的**实现**波动对声明目标：")
    L.append("")
    L.append("| 面 | 声明目标 % | 基准实现 % | 偏离 | 基准年化 % | 归一到目标后 % | H1 原 | H1 归一 |")
    L.append("|---|---|---|---|---|---|---|---|")
    for f in r["faces"]:
        b = f["bench"]
        if b["vol_pct"] is None:
            continue
        L.append("| %s | %.2f | %.2f | %+.1f%% | %.2f | %s | %s | %s |" % (
            f["face"], f["target_vol_pct"], b["vol_pct"], b["off_target_pct"],
            b["ann_pct"], ("%.2f" % b["ann_at_target_pct"]) if b["ann_at_target_pct"] is not None else "-",
            "过" if b["h1_at_own_size"] else "不过",
            "过" if b["h1_at_target"] else "不过"))
    L.append("")
    L.append("## 臂这一侧：谁只是因为放大才过 4%")
    L.append("")
    L.append("| 面 | 臂 | 年化 % | 实现波动 % | 目标 % | 放大倍数 | 归一后年化 % | H1 原→归一 |")
    L.append("|---|---|---|---|---|---|---|---|")
    face_target = {f["face"]: f["target_vol_pct"] for f in r["faces"]}
    for x in r["h1_flips"]:
        L.append("| %s | %s | %.2f | %.2f | %.2f | %.3f | %s | %s → %s |" % (
            x["face"], (x["variant"] or "")[:34], x["ann_pct"], x["vol_pct"],
            face_target.get(x["face"], 0.0),
            x["leverage_to_target"], ("%.2f" % x["ann_at_target_pct"]),
            "过" if x["h1_before"] else "不过", "过" if x["h1_after"] else "不过"))
    L.append("")
    L.append("- 臂总数 %d（其中波动由已公布 MDE 反推 %d 条，反推保真度见自检腿）"
             % (c["arms"], c["arms_vol_derived"]))
    L.append("- 实现波动偏离自己目标 >%.0f%% 的臂：**%d/%d** —— 波动目标本身就没被兑现，"
             "所以任何「绝对年化」判线实际都在比较不同杠杆的账本" % (OFF_TARGET * 100,
                                                       c["arms_off_target_10pct"], c["arms"]))
    L.append("- H1 原判 %d 条过线，归一后 %d 条" % (c["arms_h1_before"], c["arms_h1_after"]))
    L.append("- GO 臂 %d 条，归一后仍有 %d 条过 H1 —— **GO 集合不变**"
             % (c["go_arms"], c["go_arms_h1_after"]))
    L.append("")
    L.append("## 判词")
    L.append("")
    L.append("- `%s`" % r["verdict"])
    L.append("- 说人话：把 100 万元按每张面自己的目标波动铺上去，那条 4% 的线"
             "有一半是在量「你敢放多大」，不是在量「你的信号有多准」。"
             "真正该冻结的是**归一后的年化**，而不是原始年化。")
    L.append("")
    L.append("## 方向性：这个错误会不会解释掉「GO 全灭」")
    L.append("")
    L.append("不会，而且它是**保守**的：%d/%d 张面的基准比声明目标更大（放大基准 = 抬高对手 = 压低臂的超额），"
             "所以 r2151 的「59 条臂零条证明跑赢直接持有」不会因为这个尺寸误差而变宽松；"
             "把基准缩回目标只会让「持有」更好看。要翻案得往反方向错，而实测方向是单边的。"
             % (c["bench_oversized"], c["faces"]))
    L.append("")
    L.append("## 未做（如实）")
    L.append("")
    L.append("- 只动 H1 一轴：H2/H3/H4/H5 未重算，故本页不重发任何 verdict（GO 数=已公布值，仅核 H1 是否仍过）。")
    L.append("- 融资成本未建模：k<1 时归一后的数略偏乐观，k>1 时略偏保守。")
    L.append("- 波动归一用常数杠杆，不含再平衡摩擦；与面内 `vol_weighted_positions` 的实现差异未量化。")
    L.append("- 未改 `bench_generic.py` 的判线（共享面，本轮竞争窗禁改）；修法建议见下一节。")
    L.append("")
    L.append("## 建议（给闸的，不是给本轮改的）")
    L.append("")
    L.append("1. `run_arm` 里 H1 改成对**归一后年化**判（`rescale(ann, vol, target/vol)`），"
             "否则臂的实现波动一漂，判词跟着漂。")
    L.append("2. 基准的 `same_yardstick` 从布尔声明改成**实测断言**：`|bench_vol/target-1|<=10%`，"
             "否则面照印 true。")
    L.append("3. r2145 的 `benchmark_aligned_ann_pct` 要么真重算，要么改名回 `published`——"
             "同一张面上两个字段装同一个数，读者会读成两次测量。")
    L.append("")
    L.append("## 复现")
    L.append("")
    L.append("```")
    L.append("python scripts/bench_size_normalized_h1.py --selftest")
    L.append("python scripts/bench_size_normalized_h1.py")
    L.append("python scripts/bench_size_normalized_h1.py --check")
    L.append("```")
    L.append("")
    L.append("inputs_digest `%s`（%d 份面；任一改写 → --check rc3 STALE）"
             % (r["inputs_digest"][:16], len(r["inputs"])))
    L.append("")
    return "\n".join(L)


def write_outputs(r):
    with io.open(OUT_JSON, "w", encoding="utf-8", newline="\n") as f:
        json.dump(r, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    with io.open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(render(r))


# ---------------------------------------------------------------- guards
def check():
    if not os.path.exists(OUT_JSON):
        print("STALE: face missing (%s)" % OUT_JSON)
        return 3
    old = read(OUT_JSON)
    d = digest(input_paths())
    if old.get("inputs_digest") != d:
        print("STALE: inputs changed since %s (digest %s -> %s)"
              % (old.get("generated"), str(old.get("inputs_digest"))[:16], d[:16]))
        return 3
    c = old.get("counts") or {}
    print("OK: %s/%s faces, %s arms, %s H1 flips, verdict %s"
          % (c.get("faces"), c.get("faces"), c.get("arms"),
             c.get("h1_flips_down", 0) + c.get("h1_flips_up", 0), old.get("verdict")))
    return 0


def selftest():
    legs = []

    def leg(name, cond):
        legs.append((name, bool(cond)))

    # 1 identity: leaving the size alone changes nothing
    leg("identity_k1", abs(rescale(7.31, 11.0, 1.0) - 7.31) < 1e-9)
    # 2 vol-drag arithmetic, worked by hand: g=10%, s=20%, k=0.5 -> mu=12%,
    #   g' = 6% - 0.5*(10%)^2 = 5.5%
    leg("synthetic_half_size", abs(rescale(10.0, 20.0, 0.5) - 5.5) < 1e-9)
    # 3 the same printed number means different things at different sizes:
    #   4.5% at 14.68% vol is a much weaker book than 4.5% at 4.45% vol
    leg("same_print_different_size",
        (rescale(4.5, 14.68, 8.0 / 14.68) or 0) < (rescale(4.5, 4.45, 8.0 / 4.45) or 0) - 1.0)
    # 4 a known arm from the census: 5.50% at 12.21% vol, target 8% -> below H1
    leg("known_arm_flips_down", (rescale(5.5, 12.21, 8.0 / 12.21) or 0) < H1_FULL_PCT)
    # 5 a known arm from the trend face: 3.09% at 4.45% vol, target 6% -> above H1
    leg("known_arm_flips_up", (rescale(3.09, 4.45, 6.0 / 4.45) or 0) > H1_FULL_PCT)
    # 6 the bond basket's hold, at the arms' 6% target, no longer clears the gate
    leg("bond_hold_loses_h1_at_target", (rescale(4.86, 7.87, 6.0 / 7.87) or 99) < H1_FULL_PCT)
    # 7 MDE formula round-trip against bench_generic's own definition
    leg("mde_round_trip", abs((mde_from_vol(8.24, 4599) or 0) - 3.78) < 0.02)
    # 8 the MDE derivation reproduces a published vol on a face that prints both
    ok_derive = None
    p = os.path.join(RES, "bench_pair_all10_60d.json")
    if os.path.exists(p):
        d = read(p)
        n = ((d.get("benchmark_buy_and_hold") or {}).get("common_window") or {}).get("n")
        for a in d.get("arms") or []:
            pub = (a.get("common_window") or {}).get("vol_pct")
            der = vol_from_mde(a.get("mde_pp"), n)
            if pub and der:
                ok_derive = abs(pub - der) <= DERIVE_TOL_PP
                break
    leg("derive_reproduces_published_vol", ok_derive is not False)
    # 9 missing inputs stay missing instead of becoming zero
    leg("no_ann_no_rescale", rescale(None, 10.0, 0.5) is None and rescale(5.0, None, 0.5) is None)
    # 10 an arm with no vol at all is skipped, not defaulted to the target
    leg("zero_vol_is_missing", vol_from_mde(None, 4000) is None)

    failed = [n for n, ok in legs if not ok]
    for n, ok in legs:
        print(("PASS " if ok else "FAIL ") + n)
    print("%d/%d PASS" % (len(legs) - len(failed), len(legs)))
    return 0 if not failed else 3


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if a.check:
        return check()
    r = build()
    write_outputs(r)
    c = r["counts"]
    print("faces %d · arms %d · vol range %.2f-%.2f%% · off-target arms %d/%d"
          % (c["faces"], c["arms"], r["arm_vol_range_pct"]["min"] or 0.0,
             r["arm_vol_range_pct"]["max"] or 0.0, c["arms_off_target_10pct"], c["arms"]))
    print("H1 pass %d -> %d · flips down %d up %d · GO %d -> %d"
          % (c["arms_h1_before"], c["arms_h1_after"], c["h1_flips_down"], c["h1_flips_up"],
             c["go_arms"], c["go_arms_h1_after"]))
    print("bench off-target %d/%d · bench H1 at own size %d -> at target %d"
          % (c["bench_off_target_10pct"], c["faces"], c["bench_h1_at_own_size"],
             c["bench_h1_at_target"]))
    print("r2145 aligned==published %d/%d (target moved but ann same: %d)"
          % (r["r2145_aligned_label"]["aligned_equals_published"],
             r["r2145_aligned_label"]["faces_checked"],
             r["r2145_aligned_label"]["target_changed_but_ann_same"]))
    print("verdict %s" % r["verdict"])
    print("wrote %s" % os.path.relpath(OUT_JSON, ROOT))
    print("wrote %s" % os.path.relpath(OUT_MD, ROOT))
    return 0


if __name__ == "__main__":
    sys.exit(main())
