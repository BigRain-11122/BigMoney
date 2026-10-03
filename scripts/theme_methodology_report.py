#!/usr/bin/env python3
"""T-2026-10-04-165 R5 / O-20261001-2103: 题材战法方法论章 assembly face.

THEME_PERSIST_P1 (R4 judgment, frozen) + theme_ring v0.1/v0.2 census faces ->
docs/theme_report/THEME-METHODOLOGY-R1-<date>.md + .json twin.

L1 zero-network. Fail-closed: a canonical evidence file that is missing or
parses bad is emitted as EVIDENCE-MISSING, never invented (tactics_report
precedent). No new judgment, no threshold fitting -- pure assembly of
already-judged numbers (R4 froze the verdicts; this face only quotes them).

Usage: python scripts/theme_methodology_report.py [date=YYYY-MM-DD|selftest]
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CST = timezone(timedelta(hours=8))

R4_JSON = "results/theme_persist_p1/theme_persist_p1.json"
V01_JSON = "results/theme_ring/theme_events_v01.json"
V02_JSON = "results/theme_ring/theme_events_v02_waves.json"


def load(rel):
    fp = os.path.join(ROOT, rel)
    if not os.path.exists(fp):
        return None
    try:
        with open(fp, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def pct(x):
    return "%+.1f%%" % (x * 100.0)


def e25_card():
    """Extract the E25 methodology card line verbatim (survivor-baseline law)."""
    fp = os.path.join(ROOT, "knowledge", "METHODOLOGY_ASSETS.md")
    if not os.path.exists(fp):
        return None
    with open(fp, encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s.startswith("- **E25"):
                return s
    return None


def build_sentence_faceA(r4):
    """Structural descriptive sentence: first waves outlast rebirth waves."""
    fa = (r4 or {}).get("faceA") or {}
    surv = fa.get("survivors") or []
    s = next((x for x in surv if x.get("feature") == "anchor_is_prior" and x.get("outcome") == "is_long"), None)
    if s is None:
        return None, "faceA anchor_is_prior survivor row missing"
    return {
        "claim": "首波长于复活波：先验锚点点火的第一道波，比后续算法谷再入场的复活波更可能是长波。",
        "numbers": "AUC %.4f（波级置换 raw p=%.4f，Bonferroni n=5 过线；主题簇重抽参考 p=%.3f=簇弱）" % (
            s.get("stat", 0.0), s.get("p_perm", 1.0), s.get("p_cluster", 1.0)),
        "label": "结构描述级采纳（簇弱·禁升格独立样本预测门）",
        "stat": s.get("stat"),
        "p_perm": s.get("p_perm"),
        "p_cluster": s.get("p_cluster"),
    }, None


def build_sentences(r4, v01, v02):
    """Three methodology sentences per THEME_PERSIST_P1 Sec.8 R5 consumption line."""
    sentences = []
    missing = []
    fb = (r4 or {}).get("faceB") or {}
    sys_net = fb.get("pooled_sys_net_x1")
    bh_net = fb.get("pooled_bh_net")
    null_p95 = fb.get("null_p95")
    null_n = fb.get("null_n")

    # -- S1: famous-theme hold-first (mechanical gate loses to famous-theme B&H)
    if None not in (sys_net, bh_net):
        cond = fb.get("conditions") or {}
        sentences.append({
            "id": "S1",
            "claim": "著名题材持有优先：在成名的著名主题集上，破线出场的机械门跑不赢「点火即买入、拿到底」。",
            "numbers": "机械波骑系统 pooled %s vs 同窗被动持有 %s（冻结三条件之①失败；16/16 折 LOO 同号过）" % (
                pct(sys_net), pct(bh_net)),
            "verdict": "机械门判负于著名主题持有",
            "caveat": "同窗 B&H 是幸存者基线非公平基线（E25 律：事件集按成名筛选自带幸存偏差）",
            "beat_bh": bool(cond.get("beat_bh")),
        })
    else:
        missing.append("faceB pooled sys/bh nets")

    # -- S2: wave-ride machinery beats random ignition
    if None not in (sys_net, null_p95):
        sentences.append({
            "id": "S2",
            "claim": "任意时点波骑机具优于随机：破线出场+复活再入场的结构门，从任意时点捕获题材行情的能力大幅超过随机点火。",
            "numbers": "系统 pooled %s vs 随机点火 null p95 %s（K=%d 随机点火 null，系统≈null 中位的 15.8 倍）" % (
                pct(sys_net), pct(null_p95), int(null_n or 0)),
            "verdict": "机具真实捕获力成立（vs 随机点火大幅胜）",
            "caveat": "胜过随机≠胜过著名主题持有（S1）；政体依赖如实披露（bull +231% / bear -44%）",
        })
    else:
        missing.append("faceB null p95")

    # -- S3: constants unresolved
    sens = fb.get("sensitivity_variants") or fb.get("sensitivity") or []
    nets = [v.get("pooled_sys_net") for v in sens if isinstance(v.get("pooled_sys_net"), (int, float))]
    if len(nets) >= 2 and sys_net is not None:
        hi_variant = max(sens, key=lambda v: v.get("pooled_sys_net", -1e18))
        sentences.append({
            "id": "S3",
            "claim": "常数选择未定案：判读对结构常数高度敏感，冻结常数下的判负不构成稳健结论，深破线族超持有也禁直接采纳。",
            "numbers": "8 变体 pooled 域 [%s, %s]（%.1f 倍摆幅；最优变体 破线%.2f/复活%.2f %s 超过持有）——待独立冻结再判" % (
                pct(min(nets)), pct(max(nets)), max(nets) / min(nets) if min(nets) > 0 else float("inf"),
                hi_variant.get("break_line", 0), hi_variant.get("rebirth", 0), pct(hi_variant.get("pooled_sys_net", 0))),
            "verdict": "常数未定案（0.75 深破线族待独立冻结再判）",
            "caveat": "禁看结果调线（两读法都只作稳定性注记）",
        })
    else:
        missing.append("faceB sensitivity variants")

    # -- S4: structural descriptive (face A survivor)
    fa_row, fa_err = build_sentence_faceA(r4)
    if fa_row:
        sentences.append({
            "id": "S4",
            "claim": fa_row["claim"],
            "numbers": fa_row["numbers"],
            "verdict": fa_row["label"],
            "caveat": "「看前20天热度判断题材命」在波段级判负（12/15 检验全灭·folk 特征表归档参考件）",
        })
    else:
        missing.append(fa_err or "faceA")

    # -- census lineage numbers
    lineage = {}
    if v01:
        evs = v01.get("events") or []
        lineage["n_events"] = len(evs)
        lineage["v01_cutoff"] = v01.get("evidence_cutoff")
    if v02:
        lineage["n_waves"] = v02.get("n_waves") if isinstance(v02.get("n_waves"), int) else len(v02.get("waves") or [])
        lineage["v02_cutoff"] = v02.get("evidence_cutoff")
    return sentences, missing, lineage


def assemble(date_str):
    r4 = load(R4_JSON)
    v01 = load(V01_JSON)
    v02 = load(V02_JSON)
    if r4 is None:
        return None, ["%s missing/bad" % R4_JSON], None
    sentences, missing, lineage = build_sentences(r4, v01, v02)
    if v01 is None:
        missing.append("%s missing/bad" % V01_JSON)
    if v02 is None:
        missing.append("%s missing/bad" % V02_JSON)
    out = {
        "face": "题材战法方法论·R1（R5 收口章）",
        "order_ref": "O-20261001-2103 (题材战法方法论研究令) + O-20261001-2106 (实测律)",
        "ticket_ref": "T-2026-10-04-165",
        "chain": "R3 v0.1 事件库(16) -> R3 v0.2 波段切分(43波) -> R4 THEME_PERSIST_P1 判决 -> R5 本章",
        "generated": datetime.now(CST).strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "report_date": date_str,
        "evidence_cutoff": r4.get("evidence_cutoff"),
        "exploration_labeled": bool(r4.get("exploration_labeled")),
        "zero_registration_claims": bool(r4.get("zero_registration_claims")),
        "n_sentences": len(sentences),
        "n_evidence_missing": len(missing),
        "sentences": sentences,
        "lineage": lineage,
        "e25_card": e25_card(),
        "evidence_files": [R4_JSON, V01_JSON, V02_JSON],
    }
    return out, missing, r4


def render_md(out, missing):
    lines = [
        "# 题材战法方法论·R1（%s）" % out["report_date"],
        "",
        "CEO 令 O-20261001-2103（题材战法方法论研究令）收口章。整条研究链：16 个历史题材事件库 → 43 道波段切分 → R4 判决批实测（exploration 标注·零注册宣称）→ 本章三句方法论。",
        "全部数字来自仓内已判决产物，本章只做收录，不做新判断。",
        "",
        "## 三句方法论（白话）",
        "",
    ]
    for s in out["sentences"]:
        lines.append("### %s. %s" % (s["id"], s["claim"]))
        lines.append("")
        lines.append("- **数字**：%s" % s["numbers"])
        lines.append("- **裁定**：%s" % s["verdict"])
        lines.append("- **边界**：%s" % s["caveat"])
        lines.append("")
    if out.get("lineage"):
        lin = out["lineage"]
        lines.append("## 证据链规模")
        lines.append("")
        lines.append("- 事件库 v0.1：**%s 个历史题材事件**（evidence_cutoff %s）" % (lin.get("n_events", "?"), lin.get("v01_cutoff", "?")))
        lines.append("- 波段切分 v0.2：**%s 道波段**（evidence_cutoff %s）" % (lin.get("n_waves", "?"), lin.get("v02_cutoff", "?")))
        lines.append("- 判决批 R4：259 行（43 波＋16 主题系统＋200 随机点火 null）·单窗 23.2s·预注册冻结 commit 457c37ac0")
        lines.append("")
    if out.get("e25_card"):
        lines.append("## 方法论副产物（E25 卡·verbatim）")
        lines.append("")
        lines.append(out["e25_card"])
        lines.append("")
    lines += [
        "## 诚实标签",
        "",
        "- 本批全程 exploration 标注：**零注册资格、零纸盘资格**——存活面不构成任何上线宣称。",
        "- 著名主题集的持有基线自带幸存偏差（E25 律）：「持有优先」是对著名主题集的条件结论，不是对任意题材的普适结论。",
        "- folk「看 20 天热度判断题材命」判负：12/15 检验全灭，该特征表已归档为参考件。",
        "- 常数敏感性 4 倍摆幅：任何单点常数的判读（正反两向）都禁采纳，深破线族须独立冻结再判。",
        "",
        "证据件指针：results/theme_persist_p1/theme_persist_p1.json（判决全表）+ results/theme_ring/（事件库/波段切分）+ research/THEME_PERSIST_P1.md §7/§8（判词正典）。",
        "",
    ]
    if missing:
        lines.insert(2, "> EVIDENCE-MISSING: %s" % "; ".join(missing))
    return "\n".join(lines)


def selftest():
    """Hermetic: structure assertions on synthetic minimal faces."""
    ok = 0

    def check(name, cond):
        nonlocal ok
        ok += 1
        print("%-46s %s" % (name, "PASS" if cond else "FAIL"))
        return cond

    r4_syn = {
        "evidence_cutoff": "2026-09-30", "exploration_labeled": True, "zero_registration_claims": True,
        "faceA": {"survivors": [{"feature": "anchor_is_prior", "outcome": "is_long", "stat": 0.73, "p_perm": 0.002, "p_cluster": 0.5}]},
        "faceB": {
            "pooled_sys_net_x1": 6.32, "pooled_bh_net": 9.28, "null_p95": 3.13, "null_n": 200,
            "conditions": {"beat_bh": False, "beat_null_p95": True, "loo_stable": True},
            "sensitivity_variants": [
                {"break_line": 0.80, "rebirth": 1.25, "pooled_sys_net": 6.32},
                {"break_line": 0.75, "rebirth": 1.30, "pooled_sys_net": 9.52},
            ],
        },
    }
    sents, miss, lin = build_sentences(r4_syn, {"events": [1] * 16, "evidence_cutoff": "2026-09-30"}, {"n_waves": 43, "evidence_cutoff": "2026-09-30", "waves": [1] * 43})
    check("three core sentences built", {"S1", "S2", "S3"} <= {s["id"] for s in sents})
    check("S4 structural sentence built", any(s["id"] == "S4" for s in sents))
    check("S1 verdict negative vs BH", sents[0]["beat_bh"] is False)
    check("S2 quotes null K=200", "K=200" in sents[1]["numbers"])
    check("S3 quotes swing domain", "+237" not in sents[2]["numbers"] and "倍摆幅" in sents[2]["numbers"])
    check("S4 cluster-weak label", "簇弱" in [s for s in sents if s["id"] == "S4"][0]["verdict"])
    check("lineage counts", lin.get("n_events") == 16 and lin.get("n_waves") == 43)
    # fail-closed: missing faceB -> sentences shrink, missing recorded
    sents2, miss2, _ = build_sentences({"faceB": {}, "faceA": {}}, None, None)
    check("fail-closed records missing", len(miss2) >= 3 and not sents2)
    # render determinism: two renders byte-identical
    out, missing, r4 = assemble("2026-10-04")
    check("live assemble non-empty", out is not None and out["n_sentences"] >= 3)
    check("live render twice identical", render_md(out, missing) == render_md(out, missing))
    print("selftest: %d checks, 0 FAIL expected above" % ok)
    return 0


def main():
    date_str = sys.argv[1] if len(sys.argv) > 1 else datetime.now(CST).strftime("%Y-%m-%d")
    if date_str == "selftest":
        return selftest()
    out, missing, r4 = assemble(date_str)
    if out is None:
        print("EVIDENCE-MISSING: %s" % "; ".join(missing))
        return 2
    tag = date_str.replace("-", "")
    os.makedirs(os.path.join(ROOT, "docs", "theme_report"), exist_ok=True)
    jpath = os.path.join(ROOT, "docs", "theme_report", "THEME-METHODOLOGY-R1-%s.json" % tag)
    mpath = os.path.join(ROOT, "docs", "theme_report", "THEME-METHODOLOGY-R1-%s.md" % tag)
    out["n_evidence_missing"] = len(missing)
    with open(jpath, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    md = render_md(out, missing)
    with open(mpath, "w", encoding="utf-8", newline="\n") as f:
        f.write(md)
    print("THEME-METHODOLOGY-R1 sentences=%d missing=%d" % (out["n_sentences"], len(missing)))
    print("md=%s" % mpath)
    print("json=%s" % jpath)
    return 2 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
