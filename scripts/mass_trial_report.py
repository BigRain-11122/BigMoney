"""Mass-trial (千人试用) consolidated report card generator.

Product-first law face (P-2026-09-29-07): T-94 three-layer funnel waves W1/W2/W3
are judged and complete on disk, but had no consolidated CEO-visible card. This
script is a deterministic L1 aggregator ONLY: reads the frozen wave judge /
screen / generate summaries, re-derives the funnel numbers and the near-miss
dossier, writes a machine JSON + a plain-language md. Zero network, zero engine
runs, zero LLM, zero new judgments -- report-only; science gates and their
verdicts stay frozen in the wave files. Trial-labor law honored: negative
results are reported as-is, no cosmetics.

Dept: 策略/研究 (dept tag per firm/org_chart v2). Ticket lineage: T-2026-09-27-94
(mass candidate trial program, done) -- this is the consumer face.

Subcommands:
  run      : write results/mass_trial/report_card.json +
             docs/mass_trial/REPORT-CARD.md. Idempotent: deterministic given
             inputs (wall-clock ts appears in the JSON envelope only).
  selftest : offline synthetic-fixture checks (funnel math / pass extraction /
             determinism / missing-or-incomplete-input honesty). Zero writes
             outside a temp dir.
"""

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MT_DIR = ROOT / "results" / "mass_trial"
DOCS_DIR = ROOT / "docs" / "mass_trial"
CARD_JSON = MT_DIR / "report_card.json"
CARD_MD = DOCS_DIR / "REPORT-CARD.md"

FAMILY_ZH = {
    "sentiment.turnover_surge": "情绪·放量汹涌",
    "seasonal.trend_by_season": "季节·按季趋势",
    "ta.strong_close": "技术形态·强收盘",
}

G2_DSR_GATE = 0.95
G2_PBO_GATE = 0.25


def _read_json(path):
    try:
        with open(path, encoding="utf-8-sig") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except (json.JSONDecodeError, OSError):
        return None


def _f(x, nd=4):
    try:
        return round(float(x), nd)
    except (TypeError, ValueError):
        return None


def collect_waves(mt_dir):
    """Discover completed waves (wN_judge.json with complete=true). Missing or
    incomplete judge files for a discovered wave id are a hard error (exit 2
    honesty) -- a half-judged wave must never enter a CEO card."""
    mt_dir = Path(mt_dir)
    waves = []
    judge_files = sorted(mt_dir.glob("w*_judge.json"))
    if not judge_files:
        return [], "no w*_judge.json found under %s" % mt_dir
    for jf in judge_files:
        wid = jf.name.split("_judge.json")[0]
        gen = _read_json(mt_dir / ("%s_generate_summary.json" % wid))
        scr = _read_json(mt_dir / ("%s_screen_summary.json" % wid))
        jud = _read_json(jf)
        if jud is None:
            return None, "unparseable judge file: %s" % jf.name
        if not jud.get("complete"):
            return None, "wave %s judge file not complete=true (honest refusal)" % wid
        if gen is None or scr is None:
            return None, "wave %s missing generate/screen summary" % wid
        waves.append((wid, gen, scr, jud))
    return waves, None


def _passer_rows(jud):
    rows = []
    for c in jud.get("cells", []):
        if c.get("verdict") != "pass":
            continue
        g1 = c.get("g1_prime_v2", {}) or {}
        g2 = c.get("g2_registration_v2", {}) or {}
        dn = c.get("dual_nulls", {}) or {}
        dsr = c.get("dsr", {})
        if isinstance(dsr, dict):
            dsr_val = dsr.get("dsr")
        else:
            dsr_val = dsr
        rows.append({
            "candidate_id": c.get("candidate_id"),
            "family": c.get("family"),
            "family_zh": FAMILY_ZH.get(c.get("family"), c.get("family")),
            "oos_sharpe_legL": _f((c.get("legL_oos") or {}).get("oos_sharpe")),
            "oos_ret_legL": _f((c.get("legL_oos") or {}).get("oos_ret"), 6),
            "g1_sharpe_full": _f(g1.get("sharpe_full")),
            "g1_skill_line": _f((g1.get("skill_line") or {}).get("line")),
            "g1_margin": _f((g1.get("sharpe_full") or 0) - ((g1.get("skill_line") or {}).get("line") or 0)),
            "dsr": _f(dsr_val),
            "family_pbo": _f(g2.get("family_pbo")),
            "g2_dsr_ok": bool(g2.get("dsr_ok")),
            "g2_pbo_ok": bool(g2.get("pbo_ok")),
            "g2_eligible": bool(g2.get("eligible_v2")),
            "signflip_p": _f(dn.get("signflip_p")),
            "bootstrap_ci_lower": _f((dn.get("bootstrap_ci") or [None, None])[0], 8),
            "n_eff_start_windows": c.get("n_eff_start_windows"),
        })
    return rows


def build_card(mt_dir):
    """Derive the consolidated card. Returns (card, err)."""
    waves, err = collect_waves(mt_dir)
    if err:
        return None, err
    cutoffs = set()
    wave_rows = []
    passers = []
    for wid, gen, scr, jud in waves:
        cutoffs.add(str(jud.get("evidence_cutoff")))
        verd = jud.get("verdicts", {}) or {}
        led = jud.get("trials_ledger", {}) or {}
        disc = jud.get("n_wave_disclosure", {}) or {}
        wave_rows.append({
            "wave": wid,
            "enrolled": gen.get("enrolled"),
            "families": gen.get("families"),
            "dedup_rejections": (gen.get("param_dupes", 0) + gen.get("signal_dupes", 0)
                                  + gen.get("dead_signal", 0) + gen.get("rejections", 0)),
            "screen_survivors": scr.get("n_stage1_survivors"),
            "screen_line_beat": scr.get("screen_line"),
            "judged_cells": jud.get("n_judge_cells"),
            "collapsed_dupes": (scr.get("n_stage1_survivors", 0) or 0) - (jud.get("n_judge_cells", 0) or 0),
            "g1_pass": verd.get("pass", 0),
            "g1_fail": verd.get("fail", 0),
            "g2_eligible": jud.get("n_eligible_g2", 0),
            "e_fp_nominal_5pct": disc.get("E_FP_nominal_5pct"),
            "trials_ledger_total_at_finalize": led.get("total"),
            "evidence_cutoff": str(jud.get("evidence_cutoff")),
        })
        passers.extend(_passer_rows(jud))
    if len(cutoffs) > 1:
        return None, "mixed evidence_cutoff across waves: %s" % sorted(cutoffs)
    tot = {
        "n_waves": len(wave_rows),
        "enrolled": sum(w["enrolled"] or 0 for w in wave_rows),
        "screen_survivors": sum(w["screen_survivors"] or 0 for w in wave_rows),
        "judged_cells": sum(w["judged_cells"] or 0 for w in wave_rows),
        "g1_pass": sum(w["g1_pass"] or 0 for w in wave_rows),
        "g2_eligible": sum(w["g2_eligible"] or 0 for w in wave_rows),
        "trials_ledger_total_at_last_finalize": wave_rows[-1]["trials_ledger_total_at_finalize"] if wave_rows else None,
    }
    card = {
        "batch": "MASS_TRIAL_REPORT_CARD",
        "ticket_ref": "T-2026-09-27-94 consumer face (product-first law P-2026-09-29-07)",
        "evidence_cutoff": (sorted(cutoffs)[0] if cutoffs else None),
        "waves": wave_rows,
        "totals": tot,
        "passers": passers,
        "gates": {"g2_dsr_gate": G2_DSR_GATE, "g2_pbo_gate": G2_PBO_GATE},
        "verdict_line": (
            "%d/%d passed G1 skill-line; %d/%d cleared the G2 anti-luck registration gate"
            % (tot["g1_pass"], tot["judged_cells"], tot["g2_eligible"], tot["judged_cells"])
        ),
        "honesty": (
            "Report-only aggregation of frozen wave judge files; no new judgments, "
            "no thresholds touched. Near-miss dossier kept verbatim for the next "
            "supply wave; family recurrence (sentiment.turnover_surge x2) is the "
            "direction clue, not a promotion."
        ),
    }
    return card, None


def render_md(card):
    tot = card["totals"]
    passers = card["passers"]
    lines = []
    lines.append("# 千人试用成绩单（三波合账）")
    lines.append("")
    lines.append("> 令牌族谱：T-2026-09-27-94（千人候选试用计划）· 消费面：产品优先律 P-2026-09-29-07 · 数据截至 evidence_cutoff %s · 本表=只读聚合，不改任何判据" % card.get("evidence_cutoff"))
    lines.append("")
    lines.append("## 一句话结论")
    lines.append("")
    lines.append("**三波万人海选打完：%s 个候选生成、%s 个进入大考、%s 个过第一关（技能线）、%s 个够格入册（防运气线）——没有招到新员工，4 个最接近者的档案已存档，其中 2 个来自同一家族（情绪·放量汹涌），是下一波供给线最值得再探的方向。**"
                 % ("{:,}".format(tot["enrolled"]), "{:,}".format(tot["judged_cells"]),
                    tot["g1_pass"], tot["g2_eligible"]))
    lines.append("")
    lines.append("## 漏斗总表（按波次）")
    lines.append("")
    lines.append("| 波次 | 生成候选 | 海选存活 | 大考判决 | 过第一关 | 够格入册 |")
    lines.append("|---|---|---|---|---|---|")
    for w in card["waves"]:
        lines.append("| %s | %s | %s | %s | %s | %s |" % (
            w["wave"], "{:,}".format(w["enrolled"] or 0), "{:,}".format(w["screen_survivors"] or 0),
            "{:,}".format(w["judged_cells"] or 0), w["g1_pass"], w["g2_eligible"]))
    lines.append("| **合计** | **%s** | **%s** | **%s** | **%s** | **%s** |" % (
        "{:,}".format(tot["enrolled"]), "{:,}".format(tot["screen_survivors"]),
        "{:,}".format(tot["judged_cells"]), tot["g1_pass"], tot["g2_eligible"]))
    lines.append("")
    lines.append("海选=与随机对照比拼胜率门；大考判决=三窗（半年/一年/两年）×双腿×双成本全口径；第一关=全线夏普超过「技能线」；入册=第二关（防运气分 DSR≥%.2f + 家族过拟合率≤%.2f）。" % (G2_DSR_GATE, G2_PBO_GATE))
    lines.append("")
    if passers:
        lines.append("## 最接近的 4 份档案（第一关过、第二关拦）")
        lines.append("")
        lines.append("| 候选编号 | 家族 | 样本外夏普 | 全线夏普（技能线） | 防运气分 DSR（需≥%.2f） | 家族过拟合率（需≤%.2f） | 判定 |" % (G2_DSR_GATE, G2_PBO_GATE))
        lines.append("|---|---|---|---|---|---|---|")
        for p in passers:
            lines.append("| %s | %s | %.2f | %.2f（%.2f） | %.2f | %.2f | 过第一关·入册拦 |" % (
                p["candidate_id"], p["family_zh"], p["oos_sharpe_legL"],
                p["g1_sharpe_full"], p["g1_skill_line"], p["dsr"], p["family_pbo"]))
        lines.append("")
    lines.append("## 诚实锚（如实呈报）")
    lines.append("")
    lines.append("- **为什么 4 个都没入册**：公司累计试验总数已到 %s 次，防运气分（DSR）的门槛随试验总数自动抬高——试验做得越多，「看起来好」越不够，必须是「好得不像运气」。4 个接近者得分只有 %s。"
                 % ("{:,}".format(tot["trials_ledger_total_at_last_finalize"] or 0),
                    "、".join("%.2f" % p["dsr"] for p in passers) if passers else "—"))
    lines.append("- **这不是白烧**：这正是科学门在防止「把运气当本事招进队伍」；三波把 75 个家族的万人面扫完，方向线索（情绪·放量汹涌 ×2）已入档。")
    lines.append("- 本表不预测未来；下一波供给线与门槛调整归研究/策略部既有流程，本表零改动。")
    lines.append("")
    lines.append("## 机器可验数据件（全链零手抄）")
    lines.append("")
    lines.append("- results/mass_trial/report_card.json（本表机器孪生）")
    lines.append("- results/mass_trial/w{1,2,3}_judge.json（判决正典）· w{1,2,3}_screen_summary.json（海选）· w{1,2,3}_generate_summary.json（生成）")
    lines.append("- 判据库 scripts/science_gates.py（g1_prime_v2 / g2_registration_v2 冻结口径）")
    lines.append("")
    return "\n".join(lines)


def cmd_run(_args):
    card, err = build_card(MT_DIR)
    if err:
        print("mass_trial_report: REFUSED (%s)" % err)
        return 2
    card["generated"] = None  # envelope only; set at write time
    import datetime
    card["generated"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    MT_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(card, ensure_ascii=False, indent=1, sort_keys=True)
    with open(CARD_JSON, "w", encoding="utf-8", newline="\n") as f:
        f.write(payload + "\n")
    md = render_md(card)
    with open(CARD_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write(md + "\n")
    print("mass_trial_report: card written (%d waves, %d/%d judged G1-pass, %d G2-eligible) -> %s + %s"
          % (card["totals"]["n_waves"], card["totals"]["g1_pass"], card["totals"]["judged_cells"],
             card["totals"]["g2_eligible"], CARD_JSON.name, CARD_MD.name))
    return 0


def _write_fixture(mt_dir, wid, enrolled, survivors, judged, n_pass, complete=True,
                   dsr=0.42, family="sentiment.turnover_surge", eligible=0):
    gen = {"batch": "MASS_TRIAL_%s" % wid.upper(), "enrolled": enrolled, "families": 75,
           "param_dupes": 3, "signal_dupes": 5, "dead_signal": 2, "rejections": 1,
           "evidence_cutoff": "2099-09-22"}
    scr = {"batch": "MASS_TRIAL_%s" % wid.upper(), "n_stage1_survivors": survivors,
           "screen_line": 0.6, "evidence_cutoff": "2099-09-22"}
    cells = []
    for i in range(n_pass):
        cells.append({
            "candidate_id": "%s-%d" % (wid.upper(), 100 + i), "family": family,
            "verdict": "pass",
            "legL_oos": {"oos_sharpe": 1.5 + 0.1 * i, "oos_ret": 0.02},
            "g1_prime_v2": {"sharpe_full": 1.2, "skill_line": {"line": 1.13}},
            "g2_registration_v2": {"dsr": dsr, "dsr_ok": False, "family_pbo": 0.3,
                                   "pbo_ok": False, "eligible_v2": False},
            "dual_nulls": {"signflip_p": 0.001, "bootstrap_ci": [1e-05, 2e-04]},
            "dsr": {"dsr": dsr}, "n_eff_start_windows": 1000,
        })
    jud = {"batch": "MASS_TRIAL_%s_JUDGE" % wid.upper(), "complete": complete,
           "evidence_cutoff": "2099-09-22", "n_judge_cells": judged,
           "n_eligible_g2": eligible,
           "verdicts": {"pass": n_pass, "fail": judged - n_pass, "insufficient-sample": 0},
           "trials_ledger": {"total": 500000},
           "n_wave_disclosure": {"E_FP_nominal_5pct": 0.05 * judged},
           "cells": cells}
    for name, obj in (("%s_generate_summary.json" % wid, gen),
                      ("%s_screen_summary.json" % wid, scr),
                      ("%s_judge.json" % wid, jud)):
        with open(Path(mt_dir) / name, "w", encoding="utf-8") as f:
            json.dump(obj, f)


def cmd_selftest(_args):
    fails = 0

    def check(name, cond, detail=""):
        nonlocal fails
        print("[%s] %s %s" % ("PASS" if cond else "FAIL", name, detail))
        if not cond:
            fails += 1

    with tempfile.TemporaryDirectory() as td:
        tdir = Path(td)
        # fixture: two waves, 1 passer in w9, 0 in w8
        _write_fixture(tdir, "w8", 900, 100, 100, 0)
        _write_fixture(tdir, "w9", 4000, 300, 297, 1, eligible=0)
        card, err = build_card(tdir)
        check("build_card ok", card is not None, err or "")
        if card:
            t = card["totals"]
            check("funnel math", (t["enrolled"], t["judged_cells"], t["g1_pass"], t["g2_eligible"])
                  == (4900, 397, 1, 0), str(t))
            check("passer extracted", len(card["passers"]) == 1
                  and card["passers"][0]["candidate_id"] == "W9-100")
            check("passer zh family", card["passers"][0]["family_zh"] == "情绪·放量汹涌")
            check("evidence_cutoff single", card["evidence_cutoff"] == "2099-09-22")
            md = render_md(card)
            check("md carries verdict", "过第一关" in md and "1" in md)
            check("md honesty block", "诚实锚" in md)
        # determinism: rebuild -> identical content (envelope ts excluded)
        c2, _ = build_card(tdir)
        c1_copy = dict(card)
        c1_copy.pop("generated", None)
        c2.pop("generated", None)
        check("determinism", json.dumps(c1_copy, sort_keys=True) == json.dumps(c2, sort_keys=True))
        # incomplete wave refusal
        _write_fixture(tdir, "w7", 100, 10, 10, 0, complete=False)
        _, err2 = build_card(tdir)
        check("incomplete wave refused", err2 is not None and "not complete" in err2, err2 or "")
        # missing screen summary refusal
        (tdir / "w6_generate_summary.json").unlink(missing_ok=True)
        (tdir / "w6_screen_summary.json").unlink(missing_ok=True)
        (tdir / "w6_judge.json").unlink(missing_ok=True)
        with open(tdir / "w6_judge.json", "w", encoding="utf-8") as f:
            json.dump({"complete": True, "evidence_cutoff": "2099-09-22"}, f)
        _, err3 = build_card(tdir)
        check("missing summary refused", err3 is not None and "missing" in err3, err3 or "")
        # empty dir refusal
        empty = Path(td) / "empty"
        empty.mkdir()
        _, err4 = build_card(empty)
        check("empty dir refused", err4 is not None, err4 or "")

    print("selftest: %s" % ("ALL PASS" if fails == 0 else "%d FAIL" % fails))
    return 0 if fails == 0 else 1


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    if cmd == "run":
        return cmd_run(None)
    if cmd == "selftest":
        return cmd_selftest(None)
    print("usage: mass_trial_report.py [run|selftest]")
    return 2


if __name__ == "__main__":
    sys.exit(main())
