"""Bench cell 6: how much money can the index-basis carry actually absorb?

The question (four-gate test (b): how big)
------------------------------------------
`idx_fut_basis` showed the discount pays (IC +4.15pp/yr net, IM +5.89pp, IC/IF/IM
admitted). A carry with no capacity is a hobby: at some size your own roll moves
the basis and you are the one paying. This cell prices that limit from the
contracts themselves -- daily volume and open interest per active contract --
and prints, in CNY, what the line can hold under two hard rules:

  1. never trade more than 1% of a contract's median daily volume on any day
  2. never hold more than 5% of its median open interest

Those are deliberately conservative conventions, stated so a reader can redo the
arithmetic with their own numbers. The verdict is a multiple of the book we
actually run (1M): below 10x, the line is a sleeve, not a business.

Carry rates are READ from results/idx_fut_basis.json (never re-typed), so this
cell cannot drift away from the published premium.
"""
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bench_core as bc  # noqa: E402

OUT_JSON = os.path.join(bc.RESULTS, "bench_basis_capacity.json")
OUT_MD = os.path.join(bc.RESEARCH, "BENCH-BASIS-CAPACITY.md")
CONTRACTS = os.path.join(bc.DATA, "futures_contracts")
BASIS = os.path.join(bc.RESULTS, "idx_fut_basis.json")

MULT = {"IC": 200.0, "IM": 200.0, "IF": 300.0, "IH": 300.0}
ADV_SHARE = 0.01
OI_SHARE = 0.05
BOOK_CNY = 1_000_000.0
MIN_MULTIPLE = 10.0
LOOKBACK = 120


def active_contract_series(code):
    """Per date: the contract with the largest volume, plus its own stats."""
    rows = []
    for f in os.listdir(CONTRACTS):
        if not f.startswith(code) or not f.endswith(".csv"):
            continue
        p = os.path.join(CONTRACTS, f)
        try:
            df = pd.read_csv(p)
        except Exception:
            continue
        if df.empty or "volume" not in df:
            continue
        df = df[df["volume"] > 0]
        if df.empty:
            continue
        df["contract"] = f[:-4]
        rows.append(df[["date", "contract", "close", "volume", "hold"]])
    if not rows:
        return None
    allc = pd.concat(rows, ignore_index=True)
    allc["date"] = pd.to_datetime(allc["date"])
    idx = allc.groupby("date")["volume"].idxmax()
    act = allc.loc[idx].sort_values("date").set_index("date")
    act["roll"] = act["contract"].ne(act["contract"].shift())
    return act


def run():
    bc.weight_priority()
    if not os.path.exists(BASIS):
        return {"ok": False, "error": "results/idx_fut_basis.json missing"}
    basis = json.load(open(BASIS, encoding="utf-8"))
    carry = {c["fut"]: c.get("net_carry_pct") for c in
             (basis.get("verdict", {}).get("carries") or []) if c.get("fut")}

    products = {}
    for code in ("IC", "IM"):
        act = active_contract_series(code)
        if act is None or len(act) < LOOKBACK:
            products[code] = {"state": "NO_CONTRACT_DATA"}
            continue
        tail = act.tail(LOOKBACK)
        mult = MULT[code]
        price = float(tail["close"].median())
        med_vol = float(tail["volume"].median())
        med_oi = float(tail["hold"].median()) if "hold" in tail else float("nan")
        notional_per_contract = price * mult
        daily_cap = ADV_SHARE * med_vol * notional_per_contract
        oi_cap = OI_SHARE * med_oi * notional_per_contract if np.isfinite(med_oi) else None
        cap = min(x for x in (daily_cap, oi_cap) if x is not None and np.isfinite(x))
        rolls = int(tail["roll"].sum())
        rate = carry.get(code)
        products[code] = {
            "active_contract": str(tail["contract"].iloc[-1]),
            "last_bar": str(pd.Timestamp(tail.index[-1]).date()),
            "price_median": round(price, 2),
            "multiplier_cny_per_point": mult,
            "notional_cny_per_contract": round(notional_per_contract, 0),
            "median_daily_volume_contracts": int(med_vol),
            "median_open_interest_contracts": (int(med_oi) if np.isfinite(med_oi) else None),
            "rolls_in_window": rolls,
            "cap_1pct_adv_cny": round(daily_cap, 0),
            "cap_5pct_oi_cny": (round(oi_cap, 0) if oi_cap and np.isfinite(oi_cap) else None),
            "capacity_cny": round(cap, 0),
            "capacity_multiple_of_book": round(cap / BOOK_CNY, 1),
            "carry_pct_net": rate,
            "annual_cny_at_1m": (round(BOOK_CNY * rate / 100.0, 0) if rate is not None else None),
            "annual_cny_at_10m": (round(10 * BOOK_CNY * rate / 100.0, 0)
                                  if rate is not None else None),
            "print_in_cny": {
                "1M": round(BOOK_CNY * (rate or 0) / 100.0, 0),
                "10M": round(10 * BOOK_CNY * (rate or 0) / 100.0, 0),
            },
        }

    usable = [p for p in products.values() if "capacity_cny" in p]
    total_cap = sum(p["capacity_cny"] for p in usable) if usable else 0.0
    total_carry_cny_10m = sum(p["annual_cny_at_10m"] or 0 for p in usable)
    checks = {
        "C1_contract_data": bool(usable),
        "C2_each_capacity_ge_10x_book": bool(usable and all(
            p["capacity_multiple_of_book"] >= MIN_MULTIPLE for p in usable)),
        "C3_carry_read_not_typed": bool(carry),
    }
    payload = {
        "cell": "basis_capacity",
        "generated": pd.Timestamp.now(tz="Asia/Shanghai").isoformat(timespec="seconds"),
        "evidence_cutoff": max((p.get("last_bar") for p in products.values()
                                if p.get("last_bar")), default="n/a"),
        "rules": {"adv_share": ADV_SHARE, "oi_share": OI_SHARE,
                  "book_cny": BOOK_CNY, "min_multiple": MIN_MULTIPLE,
                  "lookback_bars": LOOKBACK},
        "carry_source": "results/idx_fut_basis.json (net_carry_pct, read not re-typed)",
        "products": products,
        "total_capacity_cny": round(total_cap, 0),
        "total_capacity_multiple_of_book": round(total_cap / BOOK_CNY, 1),
        "total_annual_cny_if_10m": round(total_carry_cny_10m, 0),
        "checks": checks,
        "verdict": ("CAPACITY_OK_AND_SIZED" if all(checks.values())
                    else ("CAPACITY_LIMITED" if usable else "DATA_BLOCKED")),
        "limits": [
            "impact is modelled as a fixed share of median volume, not from a market-impact curve",
            "margin funding cost is not charged (futures margin earns nothing here)",
            "OI is taken as a 120-bar median; a crowded quarter would be smaller",
        ],
    }
    os.makedirs(bc.BENCH_OUT, exist_ok=True)
    bc.write_json(OUT_JSON, payload)

    lines = ["# 股指基差能吃多少钱（bench cell 6）", "",
             f"generated {payload['generated']} | 判决 **{payload['verdict']}**", "",
             f"规则：单日不超过该合约中位成交量的 {ADV_SHARE:.0%}；持仓不超过中位持仓量的 "
             f"{OI_SHARE:.0%}；书规模按 {BOOK_CNY/1e6:.0f}M 计。", "",
             "| 品种 | 活跃合约 | 中位日成交(手) | 中位持仓(手) | 每手名义(元) | 1%ADV 容量 | 5%OI 容量 | 容量(取小) | 是书的几倍 | 净carry | 10M 下年收 |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for code, p in products.items():
        if "capacity_cny" not in p:
            lines.append(f"| {code} | 无合约数据 | — | — | — | — | — | — | — | — | — |")
            continue
        lines.append(
            f"| {code} | {p['active_contract']} | {p['median_daily_volume_contracts']} | "
            f"{p['median_open_interest_contracts']} | {p['notional_cny_per_contract']:,.0f} | "
            f"{p['cap_1pct_adv_cny']:,.0f} | "
            f"{(p['cap_5pct_oi_cny'] or 0):,.0f} | {p['capacity_cny']:,.0f} | "
            f"{p['capacity_multiple_of_book']}x | {p['carry_pct_net']}% | "
            f"{(p['annual_cny_at_10m'] or 0):,.0f} |")
    lines += ["", f"合计容量 {payload['total_capacity_cny']:,.0f} 元 = "
                  f"{payload['total_capacity_multiple_of_book']}x 书规模。"
                  f"若每腿各买 10M（合计名义 20M、按 12% 保证金约占用 2.4M），"
                  f"两腿年收合计约 {payload['total_annual_cny_if_10m']:,.0f} 元（毛，未扣资金成本）。", "",
              "## 没有回答的问题", ""] + [f"- {x}" for x in payload["limits"]]
    with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({"ok": True, "verdict": payload["verdict"],
                      "per_product": {k: v.get("capacity_multiple_of_book") for k, v in products.items()},
                      "total_capacity_multiple": payload["total_capacity_multiple_of_book"],
                      "annual_cny_at_10m": payload["total_annual_cny_if_10m"]},
                     ensure_ascii=False, indent=1))
    return payload


if __name__ == "__main__":
    res = run()
    sys.exit(0 if isinstance(res, dict) and res.get("ok", True) else 1)
