"""REGIME-STYLE MATRIX v1 skeleton + switching law engine (O-20261007-2215
bm-c deliverable ①, engineering lane).

Law: O-20261007-2215 §三 @bm-c ①策略-阶段矩阵规格件+切换律（防抖窗+滞后成本）
v1 ≤10-16 12:00. CEO direction quote: 不同风格策略适配不同市场阶段（牛市/震荡/
阴跌/熊市/护盘期）。

Honest scope (v1 skeleton):
- Five-state input CONTRACT is frozen here; labels are produced upstream by
  bm-a REGIME-5 discriminator (due ≤10-14) + bm-b five-state router spec
  (due ≤10-16). Until labels land, `run` = honest awaiting_upstream no-op.
- MATRIX_V1 numeric weights are FROZEN v1.0 instantiation with AMENDMENT
  WINDOW until the first REGIME-5-labeled switch event lands (mirror
  ROUTE_TABLE_V1 amendment-window law in system_v1_paper.py). Structural
  rules (specialists >= 2 or honest gap marker, disable-list weight == 0,
  sum(weights) <= cap) are enforced by selftest -- those are NOT amendable.
- COST_X1 imported from rev_osc_stock_p1 (frozen 13.041bp/side constant,
  zero re-implementation, same source as system_v1_paper).
- Pure engineering face: zero engine/admission/live touches; this module
  computes weight timelines + switch events + transition costs from labels.
  It does NOT trade, does NOT write member/registration files, does NOT
  touch REGIME_GUARD v3 (four-state risk ladder, different law face).

Switching law three pieces (O-2215 §一.3):
1. 确认窗防抖: raw label must persist N_CONF consecutive days before the
   flip is acted on (hysteresis; bootstrap = first label).
2. 切换滞后成本入判据: each confirmed flip charges transition cost
   = sum(|Δw_i|) * COST_X1 (same |dw|*COST_X1 form as SYSTEM-V1 glide law).
3. 翻面权重切换: weight change takes effect the FIRST DAY AFTER the
   confirmed flip day (w_eff glide law mirror; flip day itself still runs
   previous weights and carries the one-time transition cost).

Exit codes: 0 = normal / no-op awaiting_upstream; 2 = mechanism failure.
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from rev_osc_stock_p1 import COST_X1  # noqa: E402  (frozen 13.041bp/side)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LABELS_DIR = os.path.join(ROOT, "results", "regime5_labels")
OUT_DIR = os.path.join(ROOT, "results", "regime_style_matrix")

STATES = ("BULL", "CHOP", "GRIND", "BEAR", "SUPPORT")
STATE_CN = {"BULL": "牛市", "CHOP": "震荡", "GRIND": "阴跌",
            "BEAR": "熊市", "SUPPORT": "护盘期"}

SLEEVES = ("defensive_six", "grid", "lowvol", "dip_rebound", "cta_trend")

# Specialists roster (O-2215 §二 现状盘点, verbatim mapping):
#   defensive_six = 现役六员 COMPOSITE-CE-01（熊市主场·CEO 亲评防守强项）
#   grid          = GRID 族 5 活 cells（震荡收割）
#   lowvol        = 低波红利家族（2675 格显著·p=0.0018）
#   dip_rebound   = 超跌反弹淬炼版（-41%→+20.9%·胜率 61%·熊市闸三件套）
#   cta_trend     = CTA_P1 趋势线（牛市第一候选·10-08 起纸盘试用期）
MATRIX_V1 = {
    "BULL":     {"defensive_six": 0.20, "grid": 0.00, "lowvol": 0.10,
                 "dip_rebound": 0.00, "cta_trend": 0.50, "cap": 0.80},
    "CHOP":     {"defensive_six": 0.30, "grid": 0.30, "lowvol": 0.20,
                 "dip_rebound": 0.00, "cta_trend": 0.00, "cap": 0.80},
    "GRIND":    {"defensive_six": 0.40, "grid": 0.00, "lowvol": 0.20,
                 "dip_rebound": 0.20, "cta_trend": 0.00, "cap": 0.80},
    "BEAR":     {"defensive_six": 0.50, "grid": 0.00, "lowvol": 0.20,
                 "dip_rebound": 0.20, "cta_trend": 0.00, "cap": 0.90},
    "SUPPORT":  {"defensive_six": 0.40, "grid": 0.10, "lowvol": 0.30,
                 "dip_rebound": 0.10, "cta_trend": 0.00, "cap": 0.90},
}

# Per-state disable list (structural, evidence-backed O-2215 §二; NOT part
# of the amendment window). Enforced: disabled sleeve weight == 0.
#   BULL:  dip_rebound 禁用（超跌反弹=熊市闸设计件·牛市无其主场）
#   CHOP:  cta_trend 禁用（区间市趋势反复打脸·whipsaw）
#   GRIND: cta_trend+grid 禁用（缓步阴跌=趋势伪信号+网格漏底）
#   BEAR:  cta_trend 禁用 v1（ETF 多头趋势件熊市失主场·期货空腿属独立账户）
#   SUPPORT: 无禁用 v1（护盘期=空白新建·判据面归 bm-b 10-16 供给）
DISABLE_V1 = {
    "BULL": ("dip_rebound",),
    "CHOP": ("cta_trend",),
    "GRIND": ("cta_trend", "grid"),
    "BEAR": ("cta_trend",),
    "SUPPORT": (),
}

# Specialist gaps (honest): states whose non-zero sleeves < 2 must appear
# here with the in-flight supplier, else selftest fails.
SPECIALIST_GAPS = {
    "BULL": "第二专精员缺口=牛市进攻策略供给扫描（bm-a 研究车道·≤10-14 交付）",
}

N_CONF = 3  # 确认窗 3 交易日（v1 缺省；上游判别器全史回放 K≥1000 律校准后冻结）


def confirm_window(raw, n_conf=N_CONF):
    """Piece 1 确认窗防抖: effective regime series. Bootstrap = raw[0];
    a flip to a new state is confirmed only after n_conf consecutive raw
    labels of the new state; until then previous confirmed state holds."""
    if not raw:
        return []
    eff = [raw[0]]
    cand, run = None, 0
    for lab in raw[1:]:
        if lab == eff[-1]:
            cand, run = None, 0
            eff.append(eff[-1])
            continue
        if lab == cand:
            run += 1
        else:
            cand, run = lab, 1
        eff.append(lab if run >= n_conf else eff[-1])
    return eff


def switch_events(dates, eff):
    """Confirmed flip events with dwell time of the previous state."""
    events = []
    for i in range(1, len(eff)):
        if eff[i] != eff[i - 1]:
            j = i - 1
            while j > 0 and eff[j] == eff[i - 1]:
                j -= 1
            events.append({"date": dates[i], "from": eff[i - 1],
                           "to": eff[i], "prev_state_days": i - j})
    return events


def transition_cost(state_from, state_to, cost=COST_X1):
    """Piece 2 切换滞后成本: sum(|Δw_i|) * COST_X1 (SYSTEM-V1 |dw| form)."""
    dw = sum(abs(MATRIX_V1[state_to][s] - MATRIX_V1[state_from][s])
             for s in SLEEVES)
    return dw * cost, dw


def weights_on_day(eff, day_idx):
    """Piece 3 翻面权重切换 (w_eff glide law mirror): flip day itself still
    runs PREVIOUS state weights; the day AFTER the flip runs new weights."""
    if day_idx == 0:
        return MATRIX_V1[eff[0]]
    return MATRIX_V1[eff[day_idx - 1]] if eff[day_idx] != eff[day_idx - 1] \
        else MATRIX_V1[eff[day_idx]]


def validate_contract(doc):
    """Frozen input contract for bm-a REGIME-5 labels (adapter-at-wiring OK)."""
    if not isinstance(doc, dict) or not isinstance(doc.get("labels"), list) \
            or not doc["labels"]:
        return "labels array missing/empty"
    for row in doc["labels"]:
        if not isinstance(row, dict) or set(row) != {"date", "state"}:
            return "label row must be exactly {date, state}"
        if row["state"] not in STATES:
            return "state %r not in %s" % (row["state"], STATES)
    return None


def find_labels_file():
    if not os.path.isdir(LABELS_DIR):
        return None
    cands = sorted(f for f in os.listdir(LABELS_DIR) if f.endswith(".json"))
    return os.path.join(LABELS_DIR, cands[-1]) if cands else None


def cmd_run():
    path = find_labels_file()
    if path is None:
        print("regime_style_matrix: awaiting_upstream no-op "
              "(bm-a REGIME-5 labels due <=10-14; contract frozen in "
              "research/REGIME_STYLE_MATRIX_V1.md)")
        return 0
    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    err = validate_contract(doc)
    if err:
        print("regime_style_matrix: contract violation: %s" % err)
        return 2
    rows = doc["labels"]
    dates = [r["date"] for r in rows]
    raw = [r["state"] for r in rows]
    eff = confirm_window(raw)
    events = switch_events(dates, eff)
    costs = []
    for ev in events:
        c, dw = transition_cost(ev["from"], ev["to"])
        ev["dw_sum"] = round(dw, 6)
        ev["transition_cost"] = round(c, 8)
        costs.append(c)
    timeline = [{"date": d, "state_eff": e,
                 "weights": weights_on_day(eff, i)}
                for i, (d, e) in enumerate(zip(dates, eff))]
    out = {"cutoff": doc.get("cutoff", dates[-1]), "source": doc.get("source"),
           "n_conf": N_CONF, "cost_x1": COST_X1,
           "states_seen": sorted(set(eff)), "switch_events": events,
           "total_transition_cost": round(sum(costs), 8),
           "timeline": timeline}
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "MATRIX-%s.json" % out["cutoff"])
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("regime_style_matrix: %d labels -> %d confirmed switches, "
          "total transition cost %.8f -> %s"
          % (len(rows), len(events), out["total_transition_cost"], out_path))
    return 0


def _mat_sum(state):
    return sum(MATRIX_V1[state][s] for s in SLEEVES)


def cmd_selftest():
    fails = []
    n_checks = [0]

    def check(name, cond):
        n_checks[0] += 1
        if not cond:
            fails.append(name)

    # t1 hysteresis basic: flip confirmed only at 3rd consecutive new label
    eff = confirm_window(["BEAR"] * 5 + ["BULL"] * 3)
    check("t1-early-hold", eff[5] == "BEAR" and eff[6] == "BEAR")
    check("t1-confirm", eff[7] == "BULL")
    # t2 jitter: alternating labels never flip after bootstrap
    alt = ["BEAR"]
    for i in range(20):
        alt.append("BULL" if alt[-1] == "BEAR" else "BEAR")
    eff = confirm_window(alt)
    check("t2-jitter-zero-flip", switch_events(list(range(len(eff))), eff) == [])
    # t3 transition cost known value: BEAR->BULL dw precomputed
    c, dw = transition_cost("BEAR", "BULL")
    expect_dw = abs(0.20 - 0.50) + abs(0.00 - 0.10) + abs(0.20 - 0.20) \
        + abs(0.20 - 0.00) + abs(0.00 - 0.50)
    check("t3-cost-form", abs(dw - expect_dw) < 1e-12
          and abs(c - expect_dw * COST_X1) < 1e-12)
    # t4 matrix integrity: five states, sums <= cap <= 1, consistent keys
    check("t4-states", set(MATRIX_V1) == set(STATES))
    for st in STATES:
        check("t4-keys-" + st, set(MATRIX_V1[st]) == set(SLEEVES) | {"cap"})
        check("t4-sum-" + st, _mat_sum(st) <= MATRIX_V1[st]["cap"] + 1e-12)
        check("t4-cap-" + st, 0 < MATRIX_V1[st]["cap"] <= 1.0)
        check("t4-nonneg-" + st, all(MATRIX_V1[st][s] >= 0 for s in SLEEVES))
    # t5 disable enforcement: disabled sleeve weight == 0
    for st in STATES:
        for s in DISABLE_V1[st]:
            check("t5-disable-%s-%s" % (st, s), MATRIX_V1[st][s] == 0.0)
    # t6 glide: confirmation day keeps previous weights, day after new ones
    eff = confirm_window(["BEAR"] * 5 + ["BULL"] * 4)
    check("t6-glide-flipday", weights_on_day(eff, 7) == MATRIX_V1["BEAR"])
    check("t6-glide-after", weights_on_day(eff, 8) == MATRIX_V1["BULL"])
    # t7 specialists >= 2 per state OR honest gap marker on file
    for st in STATES:
        n = sum(1 for s in SLEEVES if MATRIX_V1[st][s] > 0)
        check("t7-specialists-" + st, n >= 2 or st in SPECIALIST_GAPS)
    # t8 contract validator rejects junk
    check("t8-contract-bad", validate_contract({"labels": []}) is not None)
    check("t8-contract-unknown",
          validate_contract({"labels": [{"date": "d", "state": "MOON"}]})
          is not None)
    check("t8-contract-good",
          validate_contract({"labels": [{"date": "2026-10-08",
                                         "state": "CHOP"}]}) is None)

    for f in fails:
        print("SELFTEST FAIL: %s" % f)
    print("regime_style_matrix selftest: %s (%d checks)"
          % ("PASS" if not fails else "FAIL", n_checks[0]))
    return 0 if not fails else 1


def main(argv):
    if len(argv) < 2:
        print("usage: regime_style_matrix.py <run|selftest>")
        return 2
    if argv[1] == "run":
        return cmd_run()
    if argv[1] == "selftest":
        return cmd_selftest()
    print("unknown subcommand %r" % argv[1])
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
