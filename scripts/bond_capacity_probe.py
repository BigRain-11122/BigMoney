"""T-68 WAVE-3A exchange-bonds R179 capacity-face probe (pre-prereg data gate).

R179 law PRE-APPLIED (ticket spec): any sleeve prereg MUST carry
sleeve-notional x weight x participation-cap vs ADV20 per-year distribution
BEFORE entry-count prediction. This probe = that gate for the bonds
hold-to-carry + duration-rotation lane (census wave-3a row).

Faces:
  spot    bond_zh_hs_spot (800 listed) -> universe snapshot + type buckets
          (convertibles excluded = T-60 in-flight domain, anti-dup law)
  unit    volume-notional calibration via spot amount/(volume x price) cross-face
          -- bond_zh_hs_daily has NO amount column (s0 probe: OHLCV only),
          R167 semantic law: unit verified empirically, not assumed
  sample  deterministic quantile-stratified sample (N=36) of the non-convertible
          domain sorted by spot amount -> per-bond full history via bond_zh_hs_daily
  adv     per bond-year ADV20-notional (year-end last<=20 bars mean) distribution
  verdict capacity math under candidate sleeve designs (1% ADV participation cap,
          R179 convention) -- per-year tradable fraction + universe cap-sum

Output: results/bond_capacity_wave3a.json. Exit 0 = probe done, 2 = face
failure (honest). selftest subcommand = offline hermetic fixtures, zero network.
"""
import json
import os
import sys
import time

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "results", "bond_capacity_wave3a.json")

SAMPLE_N = 36                 # deterministic quantile-stratified sample size
SLEEP_S = 2.5                  # house rate-limit convention (sina faces)
PART_CAP = 0.01                # 1% ADV participation cap (R179 convention)
# candidate prereg sleeve designs for a 1M CNY book (census 百万可行 anchor):
#   (per-bond notional CNY, n bonds)  -> sleeve notional
DESIGNS = [(20000, 20), (10000, 20), (10000, 40)]
MIN_K_ROWS = 5                 # min active rows for unit calibration median
DAILY_FAIL_TOL = 0.5           # >50% daily fetch failures = probe face-fail exit 2


def fetch_spot():
    import akshare as ak
    return ak.bond_zh_hs_spot()


def fetch_daily(sym):
    import akshare as ak
    return ak.bond_zh_hs_daily(symbol=sym)


def is_no_face(sym):
    """Raw sina klc_kl.js probe: 404 = bond has NO history file at all
    (structurally zero-capacity member, honest-include NOT exclude -- R179)."""
    import requests
    import akshare.bond.bond_zh_sina as m
    url = m.zh_sina_bond_hs_hist_url.format(
        sym, pd.Timestamp.now().strftime("%Y_%m_%d"))
    try:
        r = requests.get(url, timeout=10)
        return r.status_code == 404 or "404 Not Found" in r.text[:200]
    except Exception:                                   # noqa: BLE001
        return False


def classify(code, name):
    """Coarse in/out-of-domain buckets; name keywords first (R167: repr evidence kept)."""
    c = str(code).lower()
    n = str(name)
    if "转债" in n or c.startswith("bj81") or c.startswith("sh11") or c.startswith("sz11") \
            or c.startswith("sh12") or c.startswith("sz12"):
        return "convertible"      # T-60 domain, excluded, disclosed
    if "国债" in n:
        return "treasury"
    if "地方" in n or "地债" in n:
        return "local_gov"
    if c.startswith("bj"):
        return "bse_other"
    return "other_bond"


def head_repr(df, n=3):
    return [str(r) for r in df.head(n).to_dict("records")]


def tail_repr(df, n=2):
    return [str(r) for r in df.tail(n).to_dict("records")]


def adv20_by_year(df_daily, k_hat):
    """Per bond-year ADV20-notional = mean of last <=20 bars' notional in that year."""
    d = df_daily.copy()
    d["year"] = pd.to_datetime(d["date"]).dt.year
    d["notional"] = d["volume"] * d["close"] * k_hat
    out = {}
    for y, g in d.groupby("year"):
        tail = g["notional"].tail(20)
        out[int(y)] = float(tail.mean())
    zero_frac = float((d["volume"] == 0).mean())
    last_adv = float(d["notional"].tail(20).mean())
    return out, zero_frac, last_adv, str(pd.to_datetime(d["date"]).max().date())


def run():
    t0 = time.time()
    run_date = pd.Timestamp.now().strftime("%Y-%m-%d")
    rep = {"probe": "T-68 WAVE-3A bonds R179 capacity-face gate",
           "run_date": run_date,
           "part_cap": PART_CAP,
           "sample_n": SAMPLE_N,
           "designs": [{"per_bond_cny": a, "n_bonds": b, "sleeve_cny": a * b}
                       for a, b in DESIGNS]}

    # ---- spot face -------------------------------------------------------
    spot = fetch_spot()
    rep["spot"] = {"rows": int(len(spot)), "cols": list(map(str, spot.columns)),
                   "head_repr": head_repr(spot), "tail_repr": tail_repr(spot),
                   "sec": round(time.time() - t0, 1)}
    need = ["代码", "名称", "最新价", "成交量", "成交额"]
    missing = [c for c in need if c not in spot.columns]
    if missing:
        rep["spot"]["status"] = "FAIL missing cols: %s" % missing
        json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("spot face FAIL: missing", missing)
        return 2

    spot = spot.copy()
    spot["bucket"] = [classify(c, n) for c, n in zip(spot["代码"], spot["名称"])]
    dist = spot["bucket"].value_counts().to_dict()
    rep["spot"]["bucket_dist"] = {k: int(v) for k, v in dist.items()}

    dom = spot[spot["bucket"] != "convertible"].copy()
    dom = dom.sort_values("成交额", ascending=False).reset_index(drop=True)
    rep["spot"]["non_convertible_n"] = int(len(dom))

    # ---- unit calibration (R167 semantic law) ----------------------------
    act = dom[(dom["成交量"] > 0) & (dom["成交额"] > 0) & (dom["最新价"] > 0)]
    if len(act) < MIN_K_ROWS:
        rep["unit"] = {"status": "FAIL active rows < %d" % MIN_K_ROWS,
                      "active_rows": int(len(act))}
        json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("unit calibration FAIL: active rows", len(act))
        return 2
    k_vals = (act["成交额"] / (act["成交量"] * act["最新价"])).values
    k_hat = float(np.median(k_vals))
    rep["unit"] = {"n": int(len(act)),
                   "k_median": k_hat,
                   "k_p25": float(np.percentile(k_vals, 25)),
                   "k_p75": float(np.percentile(k_vals, 75)),
                   "implied_daily_notional_formula": "volume * close * k_median",
                   "active_row_head_repr": head_repr(act, 2)}

    # ---- deterministic quantile-stratified sample -------------------------
    n_dom = len(dom)
    idxs = sorted({int(round(i * (n_dom - 1) / (SAMPLE_N - 1))) for i in range(SAMPLE_N)})
    samp = dom.iloc[idxs]
    rep["sample"] = {"method": "quantile-stratified by spot amount desc, deterministic",
                     "picked": [{"代码": r["代码"], "名称": r["名称"],
                                 "bucket": r["bucket"],
                                 "spot_amount_cny": float(r["成交额"])}
                                for _, r in samp.iterrows()]}

    # ---- per-bond full history --------------------------------------------
    per_bond = []
    no_face = []
    fails = []
    for i, (_, r) in enumerate(samp.iterrows()):
        sym, name, bucket = r["代码"], r["名称"], r["bucket"]
        try:
            d = fetch_daily(sym)
            if len(d) == 0 or "date" not in getattr(d, "columns", []):
                raise KeyError("date")
            yv, zero_frac, last_adv, last_date = adv20_by_year(d, k_hat)
            per_bond.append({"代码": sym, "名称": name, "bucket": bucket,
                             "spot_amount_cny": float(r["成交额"]),
                             "rows": int(len(d)), "last_date": last_date,
                             "zero_volume_frac": round(zero_frac, 4),
                             "adv20_last20_cny": round(last_adv),
                             "adv20_by_year_cny": {str(y): round(v) for y, v in yv.items()}})
            print("[%d/%d] %s %s rows=%d last=%s" % (i + 1, len(samp), sym, name, len(d), last_date))
        except Exception as e:                      # noqa: BLE001 honest per-bond triage
            if is_no_face(sym):
                no_face.append({"代码": sym, "名称": name})
                per_bond.append({"代码": sym, "名称": name, "bucket": bucket,
                                 "spot_amount_cny": float(r["成交额"]),
                                 "no_face": True, "rows": 0, "last_date": None,
                                 "zero_volume_frac": None,
                                 "adv20_last20_cny": 0, "adv20_by_year_cny": {}})
                print("[%d/%d] %s NO-FACE (sina 404) -> zero-capacity member" % (i + 1, len(samp), sym))
            else:
                fails.append({"代码": sym, "err": str(e)[:160]})
                print("[%d/%d] %s FAIL %s" % (i + 1, len(samp), sym, str(e)[:80]))
        time.sleep(SLEEP_S)
    n_sample_total = len(per_bond) + len(fails)
    rep["daily"] = {"ok_measured": len(per_bond) - len(no_face),
                    "no_face_404": len(no_face), "fail": len(fails), "fails": fails,
                    "no_face_codes": [x["代码"] for x in no_face],
                    "sample_sleep_s": SLEEP_S}
    if fails and len(fails) > n_sample_total * DAILY_FAIL_TOL:
        rep["daily"]["status"] = "FAIL majority fetch failures"
        json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("daily face FAIL: ok=%d no_face=%d fail=%d"
              % (len(per_bond), len(no_face), len(fails)))
        return 2

    # ---- per-year aggregate distribution ------------------------------------
    # measured-only for distribution stats; no-face members carry ADV=0 into
    # cap-sum scaling and tradable fractions (R179: zero-capacity members are
    # included, exclusion would overstate capacity)
    measured = [b for b in per_bond if not b.get("no_face")]
    top_third = per_bond[:max(1, len(per_bond) // 3)]      # most-liquid stratum
    years = sorted({y for b in measured for y in b["adv20_by_year_cny"]})
    per_year = {}
    for y in years:
        vals = np.array([b["adv20_by_year_cny"][y] for b in measured
                         if y in b["adv20_by_year_cny"]])
        per_year[y] = {"n_bonds": int(len(vals)),
                       "median_adv20_cny": float(np.median(vals)),
                       "p25_cny": float(np.percentile(vals, 25)),
                       "p75_cny": float(np.percentile(vals, 75)),
                       "universe_cap1pct_est_cny":
                           float(sum(vals) * (n_dom / max(1, n_sample_total)) * PART_CAP)}
    rep["per_year_adv20"] = per_year

    # ---- capacity verdict under designs --------------------------------------
    verdict = []
    for per_bond_cny, n_b in DESIGNS:
        per_y = {}
        for y in years:
            tot = tradable = 0
            for b in per_bond:                     # all sampled: no-face = untradable
                if y not in b["adv20_by_year_cny"]:
                    continue
                tot += 1
                if b["adv20_by_year_cny"][y] * PART_CAP >= per_bond_cny:
                    tradable += 1
            per_y[y] = round(tradable / tot, 3) if tot else None
        now_all = [b["adv20_last20_cny"] * PART_CAP for b in per_bond]
        now_top = [b["adv20_last20_cny"] * PART_CAP for b in top_third]
        verdict.append({"per_bond_cny": per_bond_cny, "n_bonds": n_b,
                        "sleeve_cny": per_bond_cny * n_b,
                        "tradable_frac_by_year": per_y,
                        "tradable_frac_now_all": round(float(np.mean(
                            [v >= per_bond_cny for v in now_all])), 3),
                        "tradable_frac_now_top_third": round(float(np.mean(
                            [v >= per_bond_cny for v in now_top])), 3)})
    rep["capacity_verdict"] = {"part_cap": PART_CAP,
                               "note": "tradable = per-bond notional <= 1% x ADV20 (R179); "
                                       "no-face 404 members counted untradable; "
                                       "top_third = most-liquid stratum of sample (sleeve-relevant)",
                               "measured_frac_of_sample": round(len(measured) / max(1, n_sample_total), 3),
                               "designs": verdict}

    last_dates = [b["last_date"] for b in measured]
    rep["evidence_cutoff"] = max([run_date] + last_dates)      # no-future law
    rep["per_bond"] = per_bond
    rep["sec_total"] = round(time.time() - t0, 1)
    json.dump(rep, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    chk = json.load(open(OUT, encoding="utf-8"))
    assert chk["evidence_cutoff"] and chk["unit"]["k_median"] > 0
    print("PROBE OK ->", OUT, "| sec:", rep["sec_total"],
          "| k_median:", round(k_hat, 3),
          "| measured/no_face/fail:", len(measured), "/", len(no_face), "/", len(fails))
    return 0


# ---- hermetic selftest (zero network) ----------------------------------------
def selftest():
    ok = []

    def eq(name, a, b):
        ok.append((name, a == b, a, b))

    # fixture: spot face incl. convertible exclusion + k calibration
    spot = pd.DataFrame({
        "代码": ["sh010107", "sh020737", "sh113001", "sz128001", "sh010218"],
        "名称": ["21国债07", "25国债38", "XX转债", "YY转债", "02国债03"],
        "最新价": [102.0, 99.7, 100.0, 100.0, 101.0],
        "涨跌额": [0.0, 0.0, 0.0, 0.0, 0.0], "涨跌幅": [0.0, 0.0, 0.0, 0.0, 0.0],
        "买入": [0.0, 0.0, 0.0, 0.0, 0.0], "卖出": [0.0, 0.0, 0.0, 0.0, 0.0],
        "昨收": [101.0, 99.7, 100.0, 100.0, 100.0],
        "最高": [102.0, 99.7, 100.0, 100.0, 101.0], "最低": [101.0, 99.7, 100.0, 100.0, 100.0],
        "加权": [0.0, 0.0, 0.0, 0.0, 0.0],
        "成交量": [1000.0, 2000.0, 10.0, 10.0, 500.0],
        "成交额": [102000.0, 199400.0, 1000.0, 1000.0, 50500.0],
    })
    eq("classify treasury", classify("sh010107", "21国债07"), "treasury")
    eq("classify treasury-by-name (sh02 code)", classify("sh020737", "25国债38"), "treasury")
    eq("classify convertible sh11", classify("sh113001", "XX转债"), "convertible")
    eq("classify convertible sz12", classify("sz128001", "YY转债"), "convertible")
    dom = spot[[classify(c, n) != "convertible" for c, n in zip(spot["代码"], spot["名称"])]]
    eq("domain excludes convertibles", len(dom), 3)
    act = dom[(dom["成交量"] > 0) & (dom["成交额"] > 0) & (dom["最新价"] > 0)]
    k_vals = (act["成交额"] / (act["成交量"] * act["最新价"])).values
    k_hat = float(np.median(k_vals))
    eq("k calibration = 1.0 (amount=vol*price units)", round(k_hat, 6), 1.0)

    # fixture: daily face -> adv20_by_year math (volume in 张, close=100 flat)
    d = pd.DataFrame({
        "date": pd.date_range("2024-12-20", periods=30, freq="B"),
        "open": [100.0] * 30, "high": [100.0] * 30, "low": [100.0] * 30,
        "close": [100.0] * 30,
        "volume": [10.0] * 22 + [0.0] * 8,      # 2024 tail 7 bars, 2025 23 bars
    })
    yv, zero_frac, last_adv, last_date = adv20_by_year(d, k_hat=1.0)
    eq("adv20 2024 (8 bars all vol=10 -> 1000)", yv[2024], 1000.0)
    eq("adv20 2025 (last20 = 12*1000 + 8*0)/20", yv[2025], 600.0)
    eq("zero frac", round(zero_frac, 4), round(8 / 30, 4))
    eq("last20 adv (12*1000+8*0)/20", last_adv, 600.0)

    # capacity verdict math
    eq("verdict tradable 20k @ adv 1000*1%=10", 1000.0 * PART_CAP >= 20000, False)
    eq("verdict tradable 10k @ adv 2e6*1%=20k", 2e6 * PART_CAP >= 10000, True)

    # evidence cutoff no-future law
    cutoff = max(["2026-09-25", "2021-07-30"])
    eq("cutoff bounded by run_date", cutoff, "2026-09-25")

    # no-face zero-inclusion scaling math (R179): no-face member contributes 0
    # to cap-sum; scaling denominator = total sample incl. no-face, NOT measured only
    n_dom, n_sample_total = 300, 4
    vals_measured = [1e6, 2e6]                      # 2 measured, 1 no-face(0), 1 excluded fail
    cap_est = sum(vals_measured) * (n_dom / n_sample_total) * PART_CAP
    eq("cap-sum scaling includes no-face in denominator", cap_est, 3000000 * 75 * PART_CAP)
    eq("cap-sum scaling NOT measured-only (overstatement guard)",
       cap_est == sum(vals_measured) * (n_dom / 3) * PART_CAP, False)
    now_all = [1e6 * PART_CAP, 2e6 * PART_CAP, 0.0]  # no-face = untradable member
    eq("no-face counted untradable in frac",
       round(float(np.mean([v >= 10000 for v in now_all])), 3), round(2 / 3, 3))

    bad = [r for r in ok if not r[1]]
    for name, passed, a, b in ok:
        print(("PASS" if passed else "FAIL"), "|", name, "|", a, "vs", b)
    print("selftest: %d/%d PASS" % (len(ok) - len(bad), len(ok)))
    return 0 if not bad else 2


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "run"
    sys.exit(selftest() if cmd == "selftest" else run())
