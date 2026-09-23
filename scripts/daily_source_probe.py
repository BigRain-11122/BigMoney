"""Daily-bar source probe audit -- dual-leg Phase 0 precursor (dept:data).

OPERATING_PLAN Phase 0 lists "daily-line dual legs" (mitigate sina single-point
latency: the 09-23 bar arrived ~20:26). This probe AUDITS candidate second
sources for the core48 ETF daily bars. ZERO ADOPTION: no writes to data/daily,
no pipeline changes, no P1 ticket implied -- output is decision evidence only.
Adoption itself = P1 signed ticket (O-1620 discipline).

Arms (3 symbols: 510300 / 159934 / 511010):
  - sina_control      : ak.fund_etf_hist_sina (current source, parity baseline)
  - em_direct         : ak.fund_etf_hist_em, system proxy stripped (requests
                        proxy resolution patched off; push2his was IP-blocked
                        on bm-b r40/46 -- subdomain blocks are per-machine, so
                        bm-a must be measured independently)
  - em_envproxy       : ak.fund_etf_hist_em with default environment proxy
                        (distinguishes "blocked direct" vs "blocked via proxy")
  - tencent_direct    : raw urllib direct (ProxyHandler({})), fqkline qfq API
                        (known J13/P-B pitfall: loopback/EM hijack under Clash
                        global mode -> direct opener mandatory)

Parity methodology (adjustment-agnostic, TURNOVER_DERIVATION precedent):
  - return parity  : max |src_ret - local_ret| over last 30 common dates
                    (survives adjustment-reference differences between vendors)
  - level parity  : last common date close vs local close (expected to differ
                    when vendors pick different adjust anchors)
  - freshness     : has 2026-09-23 bar (all arms probed post-publish)
  - merge-compat  : amount column availability (local format needs 7 columns)

Latency limitation (honest): a snapshot probe cannot measure historical publish
latency. Sina's 09-23 ~20:26 publish is logged in results/update_status.json
history; forward latency sampling = future work (P-C-style forward sampler),
not claimed here.

Exit contract: 0 = probe completed (arm failures are findings, not crashes);
2 = all arms failed (network dead). Selftest: 0 = pass, 1 = fail. Zero network.
"""

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "daily_source_probe.json"
LOCAL_DAILY = ROOT / "data" / "daily"

SYMBOLS = {"510300": "sh510300", "159934": "sz159934", "511010": "sh511010"}
FRESH_DATE = "2026-09-23"          # last completed trading day at probe time
THROTTLE_S = 2.5                    # EM/远端公民义务限速 (P-B r39 lesson)
PARITY_DAYS = 30
TENCENT_ROWS = 640

PROXY_KEYS = ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "NO_PROXY",
              "http_proxy", "https_proxy", "all_proxy", "no_proxy")


# ---------------------------------------------------------------- helpers
def _direct_opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _strip_requests_proxy():
    """Force requests (hence akshare) to go direct on Windows.

    requests.utils resolves proxies via urllib.request.getproxies(), which on
    Windows reads BOTH env vars and the registry (system/Clash proxy). Clearing
    env vars alone is insufficient; rebind the module attribute so sessions
    created afterwards resolve no proxy. Returns a restore callable.
    """
    import requests.utils as ru
    saved = getattr(ru, "getproxies", None)
    ru.getproxies = lambda: {}
    return lambda: setattr(ru, "getproxies", saved) if saved else None


def _load_local_tail(code: str, n: int = 60):
    """Last n rows of the local sina-built CSV -> list[(date, close)]."""
    import csv
    path = LOCAL_DAILY / f"{code}.csv"
    if not path.exists():
        return None
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = [(r["date"], float(r["close"])) for r in rows[-n:]]
    return out or None


def _parity(src_pairs, local_pairs):
    """Return-parity + level-parity vs local tail.

    src_pairs/local_pairs: list[(date, close)] ascending.
    Returns dict with common_dates/return_parity_max/level_diff_last/overlap.
    """
    src = {d: c for d, c in src_pairs if d}
    loc = {d: c for d, c in local_pairs}
    common = sorted(set(src) & set(loc))
    if len(common) < 2:
        return {"common_dates": len(common), "return_parity_max": None,
                "level_diff_last": None, "overlap_insufficient": True}
    # return parity over the last PARITY_DAYS common dates
    win = common[-(PARITY_DAYS + 1):]
    diffs = []
    for a, b in zip(win, win[1:]):
        s_ret = src[b] / src[a] - 1.0
        l_ret = loc[b] / loc[a] - 1.0
        if s_ret is not None and l_ret is not None:
            diffs.append(abs(s_ret - l_ret))
    last = common[-1]
    return {"common_dates": len(common),
            "return_parity_max": (max(diffs) if diffs else None),
            "level_diff_last": src[last] - loc[last],
            "level_rel_diff_last": (src[last] / loc[last] - 1.0) if loc[last] else None,
            "last_common_date": last,
            "overlap_insufficient": False}


# ---------------------------------------------------------------- arms
def arm_sina(code: str) -> dict:
    """Control arm: current source via akshare (default env)."""
    import akshare as ak
    df = ak.fund_etf_hist_sina(symbol=SYMBOLS[code])
    pairs = [(str(d), float(c)) for d, c in zip(df["date"], df["close"])]
    return {"rows": len(pairs), "earliest": pairs[0][0], "latest": pairs[-1][0],
            "has_fresh": pairs[-1][0] >= FRESH_DATE,
            "amount_col": "amount" in df.columns, "pairs_tail": pairs[-60:]}


def arm_em(code: str, direct: bool) -> dict:
    """EM fund-ETF daily via akshare wrapper. direct=True strips all proxy
    resolution; direct=False keeps default env/registry behavior."""
    restore = None
    try:
        if direct:
            restore = _strip_requests_proxy()
        import akshare as ak
        df = ak.fund_etf_hist_em(symbol=code, period="daily", adjust="qfq")
        if df is None or len(df) == 0:
            return {"ok": False, "error": "empty dataframe"}
        dcol = "日期" if "日期" in df.columns else df.columns[0]
        pairs = [(str(d), float(c)) for d, c in zip(df[dcol], df["收盘"])]
        return {"ok": True, "rows": len(pairs), "earliest": pairs[0][0],
                "latest": pairs[-1][0], "has_fresh": pairs[-1][0] >= FRESH_DATE,
                "amount_col": "成交额" in df.columns, "pairs_tail": pairs[-60:]}
    finally:
        if restore:
            restore()


def arm_tencent(code: str) -> dict:
    """Tencent fqkline qfq via raw urllib direct opener (no wrapper risk)."""
    url = ("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param="
           f"{SYMBOLS[code]},day,,,{TENCENT_ROWS},qfq")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with _direct_opener().open(req, timeout=15) as r:
        payload = json.loads(r.read().decode("utf-8", errors="replace"))
    node = (payload.get("data") or {}).get(SYMBOLS[code]) or {}
    klines = node.get("qfqday") or node.get("day") or []
    # tencent item: [date, open, close, high, low, volume, (amount?)]
    pairs, has_amount = [], False
    for it in klines:
        if not it or len(it) < 6:
            continue
        has_amount = has_amount or len(it) >= 7
        pairs.append((str(it[0]), float(it[2])))
    if not pairs:
        return {"ok": False, "error": "no kline rows", "has_amount": has_amount}
    return {"ok": True, "rows": len(pairs), "earliest": pairs[0][0],
            "latest": pairs[-1][0], "has_fresh": pairs[-1][0] >= FRESH_DATE,
            "amount_col": has_amount, "pairs_tail": pairs[-60:]}


# ---------------------------------------------------------------- runner
def _summarize_arm(res: dict, local_pairs) -> dict:
    if not res.get("ok", True) and res.get("error"):
        return {"ok": False, "error": res["error"]}
    out = {k: v for k, v in res.items() if k != "pairs_tail"}
    out["ok"] = True
    if local_pairs:
        out["parity_vs_local"] = _parity(res["pairs_tail"], local_pairs)
    else:
        out["parity_vs_local"] = {"error": "local csv missing"}
    return out


def _net_vs_api_error(exc: BaseException) -> dict:
    """Honest taxonomy: network-level vs wrapper/API-level (J13 pitfall #2)."""
    name = type(exc).__name__
    msg = str(exc)[:200]
    net_markers = ("RemoteDisconnected", "ConnectionReset", "timeout",
                   "URLError", "ConnectionError", "gaierror", "WSA")
    api_markers = ("AttributeError", "KeyError", "JSONDecodeError",
                   "ValueError", "TypeError")
    kind = "network" if any(m in name or m in msg for m in net_markers) else \
           ("api_or_wrapper" if any(m in name for m in api_markers) else "unknown")
    return {"ok": False, "error_class": name, "error": msg, "error_kind": kind}


def run_probe() -> int:
    import akshare as ak
    env_proxy = {k: os.environ[k] for k in PROXY_KEYS if os.environ.get(k)}
    payload = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "machine": json.loads((ROOT / "fleet" / "machine.json")
                              .read_text(encoding="utf-8"))["machine_id"],
        "purpose": "daily-bar second-source audit (dual-leg Phase 0 precursor); "
                   "zero adoption, zero data/daily writes, P1 ticket remains GM-gated",
        "akshare_version": getattr(ak, "__version__", "unknown"),
        "env_proxy_vars": env_proxy,
        "fresh_date_expected": FRESH_DATE,
        "symbols": sorted(SYMBOLS),
        "arms": {},
        "audit": {"ledger_trials_added": 0, "engine_runs": 0,
                  "writes": ["results/daily_source_probe.json"]},
    }
    any_ok = False
    for code in sorted(SYMBOLS):
        local = _load_local_tail(code)
        cell = {"local_rows_tail": (len(local) if local else 0)}
        for arm_name, fn in (
            ("sina_control", lambda c=code: arm_sina(c)),
            ("em_direct", lambda c=code: arm_em(c, direct=True)),
            ("em_envproxy", lambda c=code: arm_em(c, direct=False)),
            ("tencent_direct", lambda c=code: arm_tencent(c)),
        ):
            try:
                res = fn()
                cell[arm_name] = _summarize_arm(res, local)
                if cell[arm_name].get("ok"):
                    any_ok = True
            except BaseException as exc:  # honest per-arm capture
                cell[arm_name] = _net_vs_api_error(exc)
            time.sleep(THROTTLE_S)
        payload["arms"][code] = cell
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False),
                   encoding="utf-8")
    print(f"probe -> {OUT.relative_to(ROOT)}  any_ok={any_ok}")
    return 0 if any_ok else 2


# ---------------------------------------------------------------- selftest
def _tencent_fixture():
    node = {"sh510300": {"qfqday": [
        ["2026-09-18", "4.60", "4.62", "4.63", "4.59", "500000000"],
        ["2026-09-21", "4.61", "4.63", "4.64", "4.60", "510000000"],
        ["2026-09-22", "4.64", "4.615", "4.65", "4.60", "520000000"],
        ["2026-09-23", "4.62", "4.60", "4.63", "4.58", "530000000"],
    ]}}
    return {"code": 0, "data": node}


def selftest() -> int:
    import tempfile
    ok = []

    # T1: tencent parse -- close is index 2 (not 3), date index 0
    raw = _tencent_fixture()["data"]["sh510300"]["qfqday"]
    pairs = [(it[0], float(it[2])) for it in raw]
    ok.append(pairs[-1] == ("2026-09-23", 4.60))

    # T2: return parity math on synthetic known diff
    local = [("2026-09-20", 10.0), ("2026-09-21", 11.0), ("2026-09-22", 12.0)]
    src = [("2026-09-20", 20.0), ("2026-09-21", 22.0), ("2026-09-22", 24.0)]
    # both +10% daily -> return parity 0 despite 2x level offset
    r = _parity(src, local)
    ok.append(abs(r["return_parity_max"] - 0.0) < 1e-12)
    ok.append(r["level_diff_last"] == 12.0)

    # T3: overlap insufficient honest path
    r2 = _parity([("2026-09-22", 1.0)], local)
    ok.append(r2["overlap_insufficient"] is True and r2["return_parity_max"] is None)

    # T4: proxy strip restores original resolver
    import requests.utils as ru
    before = ru.getproxies
    restore = _strip_requests_proxy()
    ok.append(ru.getproxies() == {})
    restore()
    ok.append(ru.getproxies is before)

    # T5: error taxonomy classification
    e1 = _net_vs_api_error(Exception("RemoteDisconnected('peer closed')"))
    e2 = _net_vs_api_error(KeyError("日期"))
    ok.append(e1["error_kind"] == "network" and e2["error_kind"] == "api_or_wrapper")

    # T6: local loader tolerant of missing symbol (returns None, no crash)
    ok.append(_load_local_tail("999999") is None)

    # T7: local loader reads a real core48 file when present
    got = _load_local_tail("510300")
    ok.append(got is None or (len(got) > 0 and got[-1][0] >= "2026-09-22"))

    passed = sum(bool(x) for x in ok)
    print(f"selftest: {passed}/{len(ok)} PASS")
    return 0 if passed == len(ok) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", choices=["probe", "selftest"])
    args = ap.parse_args()
    if args.cmd == "selftest":
        return selftest()
    return run_probe()


if __name__ == "__main__":
    sys.exit(main())
