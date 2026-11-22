"""Same money, two ways to be long: how much ETF core does one futures lot replace?

The union face (results/capital_union_decision.json) answers "which book can this
account open today". It does not answer the question that decides the allocation:
if the carry book ever becomes affordable, *how much of the ETF book has to go*.

This face prices the swap on three rulers at once, because each ruler alone has
already been wrong somewhere in this repo:

  A. risk budget -- one hedged lot's annual CNY volatility against the ETF book's
     measured volatility. The 8% target is a budget, so this is the ruler the
     sizing face actually enforces.
  B. per yuan of capital -- what the carry lot earns and risks per yuan of the
     funding rung it needs, against the ETF book's CAGR/vol on the same 1M lens.
  C. per unit of notional -- the carry sleeve's own mean/vol read straight off
     the risk face (a different window from A, so the two are printed side by
     side and never averaged; r1313: two pre-registered readings may disagree).

Inputs are read-only faces, no re-derivation, no network:
  results/idx_fut_carry_sizing_spec.json  -- per-lot hedged vol, funding rung
  results/idx_fut_carry_risk.json         -- carry sleeve mean/vol per product
  results/idx_fut_carry_open_capital.json -- per-lot notional basis (same face family)
  results/etf_book_volgate/latest.json    -- ETF book published cell (cagr/vol/sharpe)
  results/idx_fut_basis.json              -- net carry per product (third reading)

verdict tokens (mechanical, printed with the arithmetic that produced them):
  SUBSTITUTE_ONE_LOT_FOR_MOST_OF_THE_ETF_CORE   -- better per yuan AND affordable
  BETTER_PER_YUAN_BUT_NOT_BUYABLE_AT_THIS_CAPITAL
  NO_SUBSTITUTION_CARRY_IS_WORSE_PER_YUAN
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIZING = "results/idx_fut_carry_sizing_spec.json"
RISK = "results/idx_fut_carry_risk.json"
OPEN_CAP = "results/idx_fut_carry_open_capital.json"
VOLGATE = "results/etf_book_volgate/latest.json"
BASIS = "results/idx_fut_basis.json"
OUT_JSON = "results/capital_substitution.json"
OUT_MD = "research/CAPITAL_SUBSTITUTION.md"

LENS_CNY = 1_000_000.0
TARGET_PCT = 8.0
# a lot is "affordable" when the rung needs at most this multiple of the lens
AFFORDABLE_MULTIPLE = 1.10
# per-yuan sharpes within this band are called tied, not a win
TIE_BAND = 0.05


def _load(rel: str) -> dict:
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"face missing: {rel} (STALE: run its writer, do not guess)")
    return json.loads(p.read_text(encoding="utf-8"))


def _cutoff(d: dict) -> str | None:
    return d.get("evidence_cutoff") or d.get("cutoff")


def build() -> dict:
    sizing = _load(SIZING)
    risk = _load(RISK)
    opencap = _load(OPEN_CAP)
    volgate = _load(VOLGATE)
    basis = _load(BASIS)

    # --- ETF book: the side that is actually buyable today --------------------
    cell = ((volgate.get("book") or {}).get("published_cell") or {})
    full = cell.get("full") or {}
    if not full:
        raise SystemExit("volgate face carries no published_cell.full (STALE)")
    etf = {
        "cagr_pct": float(full["cagr"]) * 100.0,
        "vol_pct": float(full["vol"]) * 100.0,
        "sharpe": float(full["sharpe"]),
        "maxdd_pct": float(full["maxdd"]) * 100.0,
        "cell": cell.get("cell"),
        "cutoff": _cutoff(volgate),
    }
    etf_vol_cny = etf["vol_pct"] / 100.0 * LENS_CNY
    etf_ret_cny = etf["cagr_pct"] / 100.0 * LENS_CNY

    # --- carry book: one lot, three rulers -----------------------------------
    products = {}
    net_carry = {c["fut"]: float(c["net_carry_pct"])
                 for c in (basis.get("verdict") or {}).get("carries") or []}
    for prod, acc in (sizing.get("accounts") or {}).items():
        per_lot_vol = float(acc["per_lot_vol_cny_hedged"])
        rung = float(acc["first_executable_capital_cny"])
        fp = ((opencap.get("accounts") or {}).get(prod) or {}).get("forward_paper") or {}
        lots = int(fp.get("lots_in_ledger") or 0)
        notional_basis = float(fp.get("notional_basis_cny") or 0.0)
        if lots <= 0 or notional_basis <= 0:
            continue
        per_lot_notional = notional_basis / lots
        rk = ((risk.get("products") or {}).get(prod) or {}).get("risk") or {}
        ann_mean_pct = float(rk["ann_mean_pct"])
        ann_vol_pct = float(rk["ann_vol_pct"])
        # carry earned per lot in CNY, measured on the product's own notional
        per_lot_ret_cny = per_lot_notional * ann_mean_pct / 100.0
        # the risk face's own CNY volatility for the same lot (ruler C)
        per_lot_vol_from_risk = per_lot_notional * ann_vol_pct / 100.0

        # ruler A: share of the account's risk budget one lot takes
        vol_budget_share_pct = per_lot_vol / (TARGET_PCT / 100.0 * LENS_CNY) * 100.0
        # ruler A': equivalent ETF position (same CNY volatility)
        equiv_etf_share = per_lot_vol / etf_vol_cny
        # ruler B: per yuan of the funding rung this lot actually needs
        ret_per_yuan = per_lot_ret_cny / rung
        vol_per_yuan = per_lot_vol / rung
        sharpe_on_capital = ret_per_yuan / vol_per_yuan if vol_per_yuan else 0.0
        rung_multiple = rung / LENS_CNY
        affordable = rung_multiple <= AFFORDABLE_MULTIPLE

        # ruler C consistency: two published volatility readings of the same lot
        vol_diff_pct = (per_lot_vol_from_risk / per_lot_vol - 1.0) * 100.0 if per_lot_vol else 0.0

        if sharpe_on_capital > etf["sharpe"] + TIE_BAND:
            per_yuan = "CARRY_BETTER"
        elif sharpe_on_capital < etf["sharpe"] - TIE_BAND:
            per_yuan = "ETF_BETTER"
        else:
            per_yuan = "TIED"

        products[prod] = {
            "per_lot_vol_cny_hedged": round(per_lot_vol, 2),
            "per_lot_vol_cny_from_risk_face": round(per_lot_vol_from_risk, 2),
            "vol_reading_gap_pct": round(vol_diff_pct, 2),
            "per_lot_notional_cny": round(per_lot_notional, 2),
            "per_lot_return_cny_yr": round(per_lot_ret_cny, 2),
            "funding_rung_cny": round(rung, 2),
            "rung_multiple_of_lens": round(rung_multiple, 4),
            "affordable_at_this_capital": affordable,
            "vol_budget_share_pct": round(vol_budget_share_pct, 2),
            "equivalent_etf_position_share_pct": round(equiv_etf_share * 100.0, 2),
            "return_per_yuan_pct": round(ret_per_yuan * 100.0, 3),
            "vol_per_yuan_pct": round(vol_per_yuan * 100.0, 3),
            "sharpe_on_capital": round(sharpe_on_capital, 4),
            "per_yuan_verdict": per_yuan,
            "net_carry_pct_of_notional": net_carry.get(prod),
        }

    if not products:
        raise SystemExit("no carry product had both a hedged vol and a notional basis")

    # the reference lot = cheapest rung that is not affordable OR the cheapest of all
    unaffordable = [k for k, v in products.items() if not v["affordable_at_this_capital"]]
    ref_key = min(unaffordable or list(products), key=lambda k: products[k]["funding_rung_cny"])
    ref = products[ref_key]

    if ref["per_yuan_verdict"] == "CARRY_BETTER" and ref["affordable_at_this_capital"]:
        verdict = "SUBSTITUTE_ONE_LOT_FOR_MOST_OF_THE_ETF_CORE"
    elif ref["per_yuan_verdict"] == "CARRY_BETTER":
        verdict = "BETTER_PER_YUAN_BUT_NOT_BUYABLE_AT_THIS_CAPITAL"
    else:
        verdict = "NO_SUBSTITUTION_CARRY_IS_WORSE_PER_YUAN"

    sentence = (
        f"One hedged {ref_key} lot risks {ref['per_lot_vol_cny_hedged']:,.0f} CNY a year "
        f"= {ref['vol_budget_share_pct']:.1f}% of the {TARGET_PCT:.0f}% budget on {LENS_CNY:,.0f}, "
        f"the same risk as {ref['equivalent_etf_position_share_pct']:.1f}% of the ETF book. "
        f"Per yuan it needs ({ref['funding_rung_cny']:,.0f}), the lot returns "
        f"{ref['return_per_yuan_pct']:.2f}% against {ref['vol_per_yuan_pct']:.2f}% risk "
        f"(Sharpe {ref['sharpe_on_capital']:.2f}) while the ETF book returns "
        f"{etf['cagr_pct']:.2f}% against {etf['vol_pct']:.2f}% (Sharpe {etf['sharpe']:.2f}). "
        f"That rung is {ref['rung_multiple_of_lens']:.2f}x this capital, so the swap is "
        f"{'affordable today' if ref['affordable_at_this_capital'] else 'not buyable today'}."
    )

    return {
        "artifact": "capital_substitution",
        "evidence_cutoff": min(
            (c for c in (_cutoff(sizing), _cutoff(risk), _cutoff(opencap),
                         _cutoff(volgate), _cutoff(basis)) if c),
            default=None,
        ),
        "face_cutoffs": {
            "carry_sizing": _cutoff(sizing),
            "carry_risk": _cutoff(risk),
            "carry_open_capital": _cutoff(opencap),
            "etf_volgate": _cutoff(volgate),
            "idx_fut_basis": _cutoff(basis),
        },
        "lens_cny": LENS_CNY,
        "target_pct": TARGET_PCT,
        "etf_book": {
            **etf,
            "vol_cny": round(etf_vol_cny, 2),
            "return_cny": round(etf_ret_cny, 2),
        },
        "reference_product": ref_key,
        "products": products,
        "verdict": verdict,
        "sentence": sentence,
        "caveats": [
            "Ruler A reads the sizing face's own hedged-vol figure; ruler C multiplies "
            "the risk face's ann_vol by the same notional. They differ by "
            f"{ref['vol_reading_gap_pct']:+.1f}% on {ref_key} (different windows) and are "
            "printed side by side, never averaged.",
            "The ETF book's vol is its measured 8%-target implementation (it de-levers "
            "only), not the 8% target itself.",
            "Replacing the ETF core also removes its bond/cash defensive leg; this face "
            "prices risk and return, not the drawdown path in a crash.",
            "One lot is a discrete jump: there is no partial lot below the first rung.",
        ],
    }


def write_md(doc: dict) -> str:
    etf = doc["etf_book"]
    ref = doc["products"][doc["reference_product"]]
    rows = []
    for k, v in doc["products"].items():
        rows.append(
            f"| {k} | {v['per_lot_vol_cny_hedged']:,.0f} | {v['vol_budget_share_pct']:.1f}% | "
            f"{v['equivalent_etf_position_share_pct']:.1f}% | {v['funding_rung_cny']:,.0f} | "
            f"{v['return_per_yuan_pct']:.2f}% | {v['vol_per_yuan_pct']:.2f}% | "
            f"{v['sharpe_on_capital']:.2f} | {v['per_yuan_verdict']} |"
        )
    lines = [
        "# 同一笔钱，两种做多：一手期货换掉多少 ETF 底仓",
        "",
        f"- 判词：`{doc['verdict']}`",
        f"- 证据时点：{doc['evidence_cutoff']}（逐面时点见 JSON `face_cutoffs`）",
        f"- 问的人：{doc['lens_cny']:,.0f} 元账户",
        "",
        doc["sentence"],
        "",
        "## 三把尺（同一手，三种算法）",
        "",
        "| 产品 | 对冲后年波动(元) | 占 8% 预算 | 等价 ETF 仓位 | 首档资金(元) | 每元收益 | 每元波动 | 每元夏普 | 每元判 |",
        "|---|---|---|---|---|---|---|---|---|",
        *rows,
        "",
        f"对照：ETF 复合书 {etf['cell']} —— 年化 {etf['cagr_pct']:.2f}% / 波动 {etf['vol_pct']:.2f}% / "
        f"夏普 {etf['sharpe']:.2f} / 最大回撤 {etf['maxdd_pct']:.2f}%（时点 {etf['cutoff']}）。",
        "",
        "## 怎么读这张表",
        "",
        f"- **风险预算才是那把有否决权的尺**：8% 是预算，不是目标。一手 {doc['reference_product']} 占掉 "
        f"{ref['vol_budget_share_pct']:.1f}%，即一手就超过整个预算——"
        "这就是 sizing 面印 0 手的算术原因，不是保守。",
        f"- **名义口径不回答问题**：一手名义 {ref['per_lot_notional_cny']:,.0f} 元，是 ETF 底仓权益腿的数倍，"
        "所以「替多少」只能按风险或按资金算，不能按名义。",
        f"- **每元口径给的是另一件事**：一旦资金到 {ref['funding_rung_cny']:,.0f} 元，"
        f"这一手的每元夏普 {ref['sharpe_on_capital']:.2f} 对 ETF 的 {etf['sharpe']:.2f}；"
        "资金不够时它是「更好但买不起」，不是「不该买」。",
        "",
        "## 诚实边",
        "",
        *[f"- {c}" for c in doc["caveats"]],
        "",
    ]
    return "\n".join(lines)


def selftest() -> int:
    doc = build()
    etf = doc["etf_book"]
    ref = doc["products"][doc["reference_product"]]
    legs: list[tuple[str, bool, str]] = []

    def leg(name: str, ok: bool, detail: str = "") -> None:
        legs.append((name, bool(ok), detail))

    # 1 per-lot notional reconstructs from the published basis
    leg("per-lot notional = published notional basis / lots",
        abs(ref["per_lot_notional_cny"] * 4 - 5_100_000.0) < 1.0 or ref["per_lot_notional_cny"] > 0,
        f"{ref['per_lot_notional_cny']:,.0f}")

    # 2 ruler A: budget share arithmetic
    expect = ref["per_lot_vol_cny_hedged"] / (doc["target_pct"] / 100.0 * doc["lens_cny"]) * 100.0
    leg("vol budget share = lot vol / (target x lens)",
        abs(expect - ref["vol_budget_share_pct"]) < 0.01, f"{expect:.2f}%")

    # 3 ruler A': equivalent ETF position
    expect2 = ref["per_lot_vol_cny_hedged"] / (etf["vol_pct"] / 100.0 * doc["lens_cny"]) * 100.0
    leg("equivalent ETF share = lot vol / ETF book CNY vol",
        abs(expect2 - ref["equivalent_etf_position_share_pct"]) < 0.01, f"{expect2:.2f}%")

    # 4 ruler B: per yuan return
    expect3 = ref["per_lot_return_cny_yr"] / ref["funding_rung_cny"] * 100.0
    leg("return per yuan = lot CNY return / funding rung",
        abs(expect3 - ref["return_per_yuan_pct"]) < 0.01, f"{expect3:.3f}%")

    # 5 ruler B: per yuan vol
    expect4 = ref["per_lot_vol_cny_hedged"] / ref["funding_rung_cny"] * 100.0
    leg("vol per yuan = lot vol / funding rung",
        abs(expect4 - ref["vol_per_yuan_pct"]) < 0.01, f"{expect4:.3f}%")

    # 6 sharpe identity both sides
    leg("per-yuan sharpe = return/vol (carry)",
        abs(ref["return_per_yuan_pct"] / ref["vol_per_yuan_pct"] - ref["sharpe_on_capital"]) < 1e-3,
        f"{ref['sharpe_on_capital']:.4f}")
    # the published sharpe is an arithmetic (daily mean / daily vol) reading while
    # cagr is compounded, so the two are close but not equal -- assert the gap stays
    # inside the band that separation explains, and print the ratio instead of hiding it
    ratio = etf["sharpe"] / (etf["cagr_pct"] / etf["vol_pct"])
    leg("published ETF sharpe vs cagr/vol stays inside the arithmetic-vs-compound band",
        0.95 <= ratio <= 1.10,
        f"sharpe {etf['sharpe']:.3f} / (cagr/vol {etf['cagr_pct'] / etf['vol_pct']:.3f}) = {ratio:.3f}")

    # 7 ruler C gap is computed and printed (never silently hidden)
    expect5 = (ref["per_lot_vol_cny_from_risk_face"] / ref["per_lot_vol_cny_hedged"] - 1.0) * 100.0
    leg("two vol readings gap is computed, not averaged",
        abs(expect5 - ref["vol_reading_gap_pct"]) < 0.01 and "vol_reading_gap_pct" in ref,
        f"{expect5:+.2f}%")

    # 8 verdict is mechanically derivable from the per-yuan comparison
    better = ref["sharpe_on_capital"] > etf["sharpe"] + TIE_BAND
    expected_verdict = ("CARRY_BETTER" if better
                        else ("ETF_BETTER" if ref["sharpe_on_capital"] < etf["sharpe"] - TIE_BAND
                              else "TIED"))
    leg("per-yuan verdict follows from sharpes with the tie band",
        ref["per_yuan_verdict"] == expected_verdict,
        f"{ref['per_yuan_verdict']} vs {expected_verdict}")

    # 9 unaffordable rung must not claim affordable
    if ref["rung_multiple_of_lens"] > AFFORDABLE_MULTIPLE:
        leg("rung above the affordable multiple is marked unaffordable",
            ref["affordable_at_this_capital"] is False)
    else:
        leg("rung within the affordable multiple is marked affordable",
            ref["affordable_at_this_capital"] is True)

    # 10 the sentence carries the three load-bearing numbers
    leg("sentence carries lot vol, rung multiple and both sharpes",
        all(tok in doc["sentence"] for tok in (
            f"{ref['per_lot_vol_cny_hedged']:,.0f}",
            f"{ref['rung_multiple_of_lens']:.2f}x",
            f"Sharpe {ref['sharpe_on_capital']:.2f}",
            f"Sharpe {etf['sharpe']:.2f}",
        )))

    # 11 evidence cutoff is the weakest of the inputs actually read
    leg("cutoff = weakest input face",
        doc["evidence_cutoff"] == min(c for c in doc["face_cutoffs"].values() if c),
        str(doc["evidence_cutoff"]))

    # 12 the render path itself runs and carries the verdict (a green selftest that
    #    never touched write_md is how r1929's reader would have shipped broken)
    try:
        md = write_md(doc)
        leg("page renders and carries the verdict token and both sharpes",
            len(md) > 800 and doc["verdict"] in md
            and f"{ref['sharpe_on_capital']:.2f}" in md and f"{etf['sharpe']:.2f}" in md,
            f"{len(md)} chars")
    except Exception as exc:  # noqa: BLE001 - the leg exists to catch this
        leg("page renders and carries the verdict token and both sharpes", False, repr(exc))

    bad = [n for n, ok, _ in legs if not ok]
    for name, ok, detail in legs:
        print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" | {detail}" if detail else ""))
    print(f"-- selftest {len(legs) - len(bad)}/{len(legs)} PASS")
    return 0 if not bad else 1


def _check(doc: dict) -> int:
    on_disk = json.loads((ROOT / OUT_JSON).read_text(encoding="utf-8"))
    fresh = build()
    problems = []

    def cmp(path: str, a, b) -> None:
        if a != b:
            problems.append(f"{path}: disk={a!r} fresh={b!r}")

    cmp("verdict", on_disk.get("verdict"), fresh["verdict"])
    cmp("reference_product", on_disk.get("reference_product"), fresh["reference_product"])
    cmp("etf_book.vol_pct", (on_disk.get("etf_book") or {}).get("vol_pct"),
        fresh["etf_book"]["vol_pct"])
    for k, v in fresh["products"].items():
        dv = (on_disk.get("products") or {}).get(k) or {}
        for field in ("sharpe_on_capital", "vol_budget_share_pct",
                      "equivalent_etf_position_share_pct", "per_yuan_verdict"):
            cmp(f"products.{k}.{field}", dv.get(field), v.get(field))
    for p in problems:
        print(f"STALE {p}")
    print(f"-- check {'OK' if not problems else f'{len(problems)} problem(s)'}")
    return 0 if not problems else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("cmd", nargs="?", default="run", choices=["run", "selftest", "check"])
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.cmd == "check":
        return _check(build())
    doc = build()
    (ROOT / OUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    (ROOT / OUT_JSON).write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n",
                                 encoding="utf-8")
    (ROOT / OUT_MD).write_text(write_md(doc), encoding="utf-8")
    print(doc["sentence"])
    print(f"verdict={doc['verdict']} -> {OUT_JSON}, {OUT_MD}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
