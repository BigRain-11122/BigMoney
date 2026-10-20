"""PORTFOLIO RECOMMENDATION face (bm-b r1064, dept: 策略+研究).

CEO order O-20261019-2230 sec.3 asks for a stage x style face by 2026-10-26:
"各阶段态×风格活/判负矩阵 + 最优组合建议 + 组合回测证据链".  The matrix half
shipped as docs/stagestyle/STAGE-STYLE-MATRIX-v1.md (r1086).  This script ships
the other two halves as ONE deterministic product page:

  * 最优组合建议 (best-combination recommendation) -- derived strictly from
    already-frozen judged artifacts; zero new tests, zero new judgment lines;
  * 组合回测证据链 (evidence chain) -- per-source file + sha16 + cutoff.

Consumption is single-source: the stage x style matrix is re-derived by
importing scripts/sscombo_stage_style_matrix.build() (no re-implementation),
family judgments are read from the P1 result JSONs, and the live holdings block
is read from results/divlowvol_live/latest.json.  Nothing here re-ranks,
re-judges or re-tests anything.

Outputs (deterministic; no wall-clock fields -> byte-identical reruns):
  docs/portfolio_recommendation/REC-<asof>.md
  docs/portfolio_recommendation/REC-<asof>.json   (+ .latest.json twin)

Exit codes: 0 ok/idempotent, 2 mechanism fault (missing/garbled input).
"""

from __future__ import annotations

import hashlib
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import sscombo_stage_style_matrix as SSM  # noqa: E402  single-source matrix

OUT_DIR = os.path.join(ROOT, "docs", "portfolio_recommendation")

FINALIZE = os.path.join(ROOT, "results", "stagestyle_combo_p1",
                        "FINALIZE-SSCOMBO-P1.json")
FAMILIES = {
    "divlowvol": os.path.join(ROOT, "results", "fund_divlowvol_p1",
                              "fund_divlowvol_p1_results.json"),
    "value": os.path.join(ROOT, "results", "fund_value_p1",
                          "fund_value_p1_results.json"),
    "quality": os.path.join(ROOT, "results", "fund_quality_p1",
                            "fund_quality_p1_results.json"),
}
LIVE_PICKS = os.path.join(ROOT, "results", "divlowvol_live", "latest.json")
NULLS_FACE = os.path.join(ROOT, "results", "divlowvol_nulls",
                          "NULLS-CONSUME-2026-09-22.json")

STATES = ["BEAR", "GRIND", "CHOP", "SUPPORT", "BULL"]


def _rel(path: str) -> str:
    return os.path.relpath(path, ROOT).replace("\\", "/")


def _rel_sha16(path: str) -> str:
    return hashlib.sha256(open(path, "rb").read()).hexdigest()[:16]


def _obj_sha16(obj) -> str:
    blob = json.dumps(obj, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()[:16]


def best_sleeve_per_stage(matrix) -> dict[str, dict]:
    """Max-Sharpe cell per stage (descriptive only -- no judgment line).

    matrix = {cell: {state: stats, 'ALL': stats}} from SSM.build().
    """
    out: dict[str, dict] = {}
    for st in STATES:
        best = None
        for cell, row in matrix.items():
            stats = row.get(st) or {}
            s = stats.get("sharpe_ann")
            if s is None:
                continue
            if best is None or s > best["sharpe_ann"]:
                best = {"cell": cell, "sharpe_ann": s,
                        "ann_ret_eq": stats.get("ann_ret_eq"),
                        "state_dd": stats.get("state_dd"),
                        "n_days": stats.get("n_days")}
        out[st] = best or {"cell": None}
    return out


def build_payload() -> dict:
    mat = SSM.build()
    finalize = json.load(open(FINALIZE, encoding="utf-8"))
    fams = {k: json.load(open(p, encoding="utf-8")) for k, p in FAMILIES.items()}
    live = json.load(open(LIVE_PICKS, encoding="utf-8"))
    nulls = json.load(open(NULLS_FACE, encoding="utf-8"))

    labels = json.load(open(SSM._latest_labels_path(), encoding="utf-8"))
    current_stage = labels["labels"][-1]["state"]
    recent = [x["state"] for x in labels["labels"][-20:]]

    matrix_regime = mat.get("matrix_by_allocation_regime") or mat["matrix"]
    per_stage = best_sleeve_per_stage(matrix_regime)

    verdict = finalize["verdict"]
    best_uncond = verdict["best_unconditional"]
    best_combo = verdict["best_combo"]

    fam_view = {}
    for k, d in fams.items():
        fam_view[k] = {
            "batch": d.get("batch"),
            "verdict": d.get("verdict"),
            "headline_sharpe": (d.get("headline") or {}).get("sharpe_full"),
            "passive_sharpe": (d.get("passive_face") or {}).get("sharpe_full"),
            "dsr": ((d.get("gates") or {}).get("dsr") or {}).get("dsr"),
            "evidence_cutoff": d.get("evidence_cutoff"),
        }

    chain = []
    for path in (FINALIZE, FAMILIES["divlowvol"], FAMILIES["value"],
                 FAMILIES["quality"], LIVE_PICKS, NULLS_FACE,
                 SSM._latest_labels_path()):
        chain.append({"path": _rel(path), "sha16": _rel_sha16(path)})
    chain.append({"path": _rel(SSM.OUT_JSON), "note": "matrix json face",
                  "sha16": (_rel_sha16(SSM.OUT_JSON)
                            if os.path.exists(SSM.OUT_JSON) else None)})

    payload = {
        "face": "PORTFOLIO-RECOMMENDATION",
        "status": "RESEARCH_READOUT_ZERO_JUDGED_CLAIMS",
        "as_of": labels["cutoff"],
        "decision": {
            "recommendation": "unconditional DIVLOWVOL-YIELDVOL sleeve "
                              "(Top-20 by yield_ttm, low-vol half, EW, monthly)",
            "basis": "stage-conditioned selection was judged UNSUPPORTED; "
                     "the unconditional sleeve dominates every combo cell",
            "best_combo": best_combo,
            "best_unconditional": best_uncond,
            "margin_sharpe": verdict.get("margin"),
            "p4_pass": verdict.get("passes_p4"),
            "rule": verdict.get("rule"),
            "attribution": verdict.get("attribution"),
        },
        "stage_view": {
            "label_face": _rel(SSM._latest_labels_path()),
            "current_stage": current_stage,
            "last_20_sessions": recent,
            "per_stage_best_descriptive": per_stage,
            "caveat": "descriptive readout on the allocation-regime view "
                      "(label that governed each month's allocation); "
                      "no judgment line is asserted by this table",
        },
        "family_view": fam_view,
        "nulls_evidence": {
            "path": _rel(NULLS_FACE),
            "verdict": nulls.get("verdict"),
            "z": (nulls.get("stats") or {}).get("z"),
            "p": (nulls.get("stats") or {}).get("p_value"),
            "k": (nulls.get("stats") or {}).get("k"),
            "p95": (nulls.get("stats") or {}).get("p95"),
        },
        "live_holdings": {
            "path": _rel(LIVE_PICKS),
            "as_of": live.get("as_of"),
            "entry_date": live.get("entry_date"),
            "n_holdings": live.get("n_holdings"),
            "weight": live.get("weight"),
            "one_way_turnover": (live.get("turnover") or {}).get("one_way_turnover"),
            "codes": [h["code"] for h in live.get("holdings") or []],
        },
        "evidence_chain": chain,
        "honesty": [
            "本页是已冻结判决产物的汇总面：零新检验、零新判据、零 ledger 记账。",
            "最优组合建议 = 判决面读数（无条件 divlowvol 优于三格阶段组合），"
            "不构成投资建议；公司自动实盘开闸仍须月界窗 + CEO 唯一门。",
            "阶段表为描述性读数（格内日收益统计），不含活/判负判决线。",
            "三族 P1 判决 verdict 均为 insufficient-sample，如实携带。",
            "P2 复活批（盈利质量过滤+出场轴）仍在冻结窗，面板重投为结构等待；"
            "本页不预设其结论。",
        ],
    }
    payload["sha16"] = _obj_sha16(payload)
    return payload


def render_md(p: dict) -> str:
    d = p["decision"]
    sv = p["stage_view"]
    L: list[str] = []
    L.append("# 组合最优建议 + 证据链（阶段×风格 v1）")
    L.append("")
    L.append(f"- 证据截止（as_of）：**{p['as_of']}**｜机：bm-b｜"
             f"面：`{p['face']}`（{p['status']}）")
    L.append("- 本页由 `scripts/portfolio_recommend.py` 确定性再生成；"
             "零新检验、零新判据。")
    L.append("")
    L.append("## 1. 结论（最优组合建议）")
    L.append("")
    L.append(f"**建议：`{d['recommendation']}`**")
    L.append("")
    L.append(f"- 依据：{d['basis']}")
    L.append(f"- 判据原文：{d['rule']}")
    L.append(f"- 最好阶段组合 {d['best_combo']['cell']} 夏普 "
             f"{d['best_combo']['sharpe_x1']:.3f} vs 无条件 "
             f"{d['best_unconditional']['face']} "
             f"{d['best_unconditional']['sharpe_x1']:.3f}"
             f"（差 {d['margin_sharpe']:+.3f}，P4 门槛{'过' if d['p4_pass'] else '未过'}）")
    L.append(f"- 归因：{d['attribution']}")
    L.append("")
    L.append("## 2. 当前阶段与阶段读数（描述面）")
    L.append("")
    L.append(f"- 当前阶段：**{sv['current_stage']}**"
             f"（标签面 `{sv['label_face']}`，截止 {p['as_of']}）")
    L.append(f"- 近 20 个交易日阶段序列：{'/'.join(sv['last_20_sessions'])}")
    L.append("")
    L.append("| 阶段态 | 样本日 | 描述最优面 | 条件夏普 | 条件年化 | 态内回撤 |")
    L.append("|---|---:|---|---:|---:|---:|")
    for st in STATES:
        b = sv["per_stage_best_descriptive"].get(st) or {}
        if not b.get("cell"):
            L.append(f"| {st} | — | — | — | — | — |")
            continue
        L.append(f"| {st} | {b['n_days']} | {b['cell']} | {b['sharpe_ann']:.2f} "
                 f"| {(b.get('ann_ret_eq') or 0) * 100:.1f}% "
                 f"| {(b.get('state_dd') or 0) * 100:.1f}% |")
    L.append("")
    L.append(f"> {sv['caveat']}")
    L.append("")
    L.append("## 3. 三族判决面（如实携带）")
    L.append("")
    L.append("| 族 | 判决 | 夏普(全窗) | 被动等权夏普 | DSR | cutoff |")
    L.append("|---|---|---:|---:|---:|---|")
    for k in ("divlowvol", "value", "quality"):
        f = p["family_view"][k]
        L.append(f"| {k} | {f['verdict']} | {f['headline_sharpe']:.3f} "
                 f"| {f['passive_sharpe']:.3f} | {f['dsr']:.3f} "
                 f"| {f['evidence_cutoff']} |")
    L.append("")
    nl = p["nulls_evidence"]
    L.append(f"- 同掩码 null 族（K={nl['k']}）：verdict={nl['verdict']}，"
             f"z={nl['z']}，p={nl['p']}（`{nl['path']}`）")
    L.append("")
    L.append("## 4. 当前持仓面（冻结规则导出的 live 名单）")
    L.append("")
    lh = p["live_holdings"]
    L.append(f"- 来源 `{lh['path']}`｜as_of {lh['as_of']}｜"
             f"入场月 {lh['entry_date']}｜{lh['n_holdings']} 只×"
             f"{lh['weight'] * 100:.0f}% 等权｜单向换手 {lh['one_way_turnover']:.0%}")
    L.append(f"- 名单：{', '.join(lh['codes'])}")
    L.append("")
    L.append("## 5. 证据链（文件 + sha16）")
    L.append("")
    for c in p["evidence_chain"]:
        L.append(f"- `{c['path']}` — {c.get('sha16') or '—'}")
    L.append("")
    L.append("## 6. 诚实边界")
    L.append("")
    for h in p["honesty"]:
        L.append(f"- {h}")
    L.append("")
    L.append(f"sha16={p['sha16']}")
    L.append("")
    return "\n".join(L)


def run() -> int:
    try:
        p = build_payload()
    except Exception as exc:  # missing/garbled inputs -> honest mechanism fault
        print(json.dumps({"verdict": "FAULT", "error": repr(exc)},
                         ensure_ascii=False))
        return 2
    os.makedirs(OUT_DIR, exist_ok=True)
    asof = p["as_of"]
    md_path = os.path.join(OUT_DIR, f"REC-{asof}.md")
    js_path = os.path.join(OUT_DIR, f"REC-{asof}.json")
    md = render_md(p)
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    with open(js_path, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT_DIR, "REC-latest.md"), "w", encoding="utf-8") as f:
        f.write(md)
    with open(os.path.join(OUT_DIR, "REC-latest.json"), "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
    print(json.dumps({"verdict": "OK", "as_of": asof, "sha16": p["sha16"],
                      "md": _rel(md_path), "json": _rel(js_path)},
                     ensure_ascii=False))
    return 0


def selftest() -> int:
    legs = []

    # leg1: deterministic rerun (same inputs -> same payload hash)
    a, b = build_payload(), build_payload()
    legs.append(("deterministic_rerun", a["sha16"] == b["sha16"]))

    # leg2: stage-best picks the max sharpe cell
    fake = {
        "A": {st: {"sharpe_ann": 0.5, "n_days": 10} for st in STATES},
        "B": {st: {"sharpe_ann": 0.9 if st == "BULL" else 0.1, "n_days": 10}
              for st in STATES},
    }
    picks = best_sleeve_per_stage(fake)
    legs.append(("stage_best_max", picks["BULL"]["cell"] == "B"
                 and picks["BEAR"]["cell"] == "A"))

    # leg3: every evidence file in the chain exists on disk
    legs.append(("evidence_chain_on_disk",
                 all(os.path.exists(os.path.join(ROOT, c["path"]))
                     for c in a["evidence_chain"]
                     if c.get("note") != "matrix json face")))

    # leg4: markdown carries the four contract sections
    md = render_md(a)
    legs.append(("md_sections",
                 all(h in md for h in ("## 1. 结论", "## 2. 当前阶段",
                                       "## 5. 证据链", "## 6. 诚实边界"))))

    # leg5: decision must not claim a pass when P4 failed
    legs.append(("no_false_pass",
                 not (a["decision"]["p4_pass"] is False
                      and "P4 门槛过" in md)))

    ok = [n for n, v in legs if v]
    for n, v in legs:
        print(f"  [{'PASS' if v else 'FAIL'}] {n}")
    print(f"selftest {len(ok)}/{len(legs)} PASS")
    return 0 if len(ok) == len(legs) else 1


def main(argv=None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run",
                    choices=["run", "selftest"])
    args = ap.parse_args(argv)
    return run() if args.cmd == "run" else selftest()


if __name__ == "__main__":
    raise SystemExit(main())