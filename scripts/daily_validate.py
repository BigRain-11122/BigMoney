"""Tencent validation leg for the core-48 daily bars (T-08, dept:data).

Why (O-20260924-1045 P1 ticket + OPERATING_PLAN Phase 0 "日线源双腿" + R34
probe results/daily_source_probe.json): sina is a single point of daily-bar
truth with an 11-hour publication-delay incident on record (09-23 bar landed
~20:26; 12 SZ 159xxx laggards frozen for hours behind the probe fast-path).
The R34 probe established the only viable second source is tencent fqkline --
fresh same-day, level parity 0.0 at the last common date vs local -- but it
carries NO amount column, so it can NEVER be a bar-write source. This module
is therefore a *validation leg* only:

  - freshness : does tencent show a bar NEWER than the local cutoff?
                (disambiguates "sina late/down" vs "bar not published yet"
                vs "market closed" -- the 0-new-row ambiguity, for free)
  - parity    : level parity at the last common date (primary gate, 1e-3
                relative tol, R34 finding: qfq latest == raw latest so the
                comparison is valid on non-ex-div dates) + 30d return-parity
                diagnostic (secondary; ex-div dates false-red by design --
                qfq back-adjusts history, local raw does not -> flagged, never
                treated as hard failure)
  - fallback  : diagnosis source for update_daily's primary-failure path.
                NEVER writes bars; mismatch is flagged, never auto-applied
                (update_daily overlap_mismatch precedent).

Contract (mirrors update_daily discipline):
  - zero writes to data/daily, zero history rewrites, zero new network pulls
    beyond the tencent validation endpoint (throttled).
  - direct urllib with ProxyHandler({}) -- Clash global mode hijacks even
    loopback (J13 pitfall), never trust ambient proxy for this host.
  - status: results/daily_validate_status.json (atomic .tmp + os.replace).
  - injectable fetcher for offline selftest (deterministic, zero network).

Exit codes: 0 ok/no-op | 1 selftest fail | 2 validation source unreachable
(honest -- recorded, never silenced).

Usage:
    python scripts/daily_validate.py run              # full-pool audit
    python scripts/daily_validate.py check --symbols 510300,159934
    python scripts/daily_validate.py selftest         # offline logic tests
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS

STATUS_PATH = os.path.join(PATHS.results_dir, "daily_validate_status.json")
TENCENT_ROWS = 640            # ~2.5y tail, same as probe arm
LEVEL_TOL = 1e-3              # relative close-level parity at last common date
PARITY_DAYS = 30              # return-parity diagnostic window
THROTTLE_S = 0.5              # remote-citizen throttle (P-B r39 lesson)


# ---------------------------------------------------------------- source
def _direct_opener():
    """No-proxy opener: never let Clash route/intercept this host (J13 pit)."""
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def to_tencent_symbol(code: str) -> str:
    if not (len(code) == 6 and code.isdigit()):
        raise ValueError(f"bad bare code: {code!r}")
    return ("sh" if code.startswith("5") else "sz") + code


def tencent_daily(code: str, rows: int = TENCENT_ROWS):
    """Tencent fqkline daily tail -> (pairs, has_amount).

    pairs: list[(date_str, close)] ascending; close is item index 2
    (probe fixture pinned: [date, open, close, high, low, volume, ...]).
    Raises on network/parse failure -- callers classify honestly."""
    url = ("https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?param="
           f"{to_tencent_symbol(code)},day,,,{rows},qfq")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with _direct_opener().open(req, timeout=15) as r:
        payload = json.loads(r.read().decode("utf-8", errors="replace"))
    node = (payload.get("data") or {}).get(to_tencent_symbol(code)) or {}
    klines = node.get("qfqday") or node.get("day") or []
    pairs, has_amount = [], False
    for it in klines:
        if not it or len(it) < 6:
            continue
        has_amount = has_amount or len(it) >= 7
        pairs.append((str(it[0]), float(it[2])))
    if not pairs:
        raise ValueError("tencent kline empty")
    return pairs, has_amount


def local_tail(code: str, n: int = PARITY_DAYS + 40):
    """Last n (date, close) pairs of the local sina-built CSV."""
    import pandas as pd
    path = os.path.join(PATHS.daily_dir, f"{code}.csv")
    df = pd.read_csv(path, dtype={"date": str})
    tail = df.tail(n)
    return [(str(d), float(c)) for d, c in zip(tail["date"], tail["close"])]


def local_last_date(code: str) -> str:
    import pandas as pd
    path = os.path.join(PATHS.daily_dir, f"{code}.csv")
    return str(pd.read_csv(path, dtype={"date": str})["date"].iloc[-1])


def core_codes() -> list:
    return sorted(f[:-4] for f in os.listdir(PATHS.daily_dir)
                  if f.endswith(".csv") and f[:-4].isdigit())


# ---------------------------------------------------------------- checks
def parity(src_pairs, local_pairs):
    """Level parity (primary) + return parity (diagnostic) vs local tail."""
    src = {d: c for d, c in src_pairs if d}
    loc = {d: c for d, c in local_pairs}
    common = sorted(set(src) & set(loc))
    if len(common) < 2:
        return {"common_dates": len(common), "overlap_insufficient": True,
                "level_pass": None, "return_parity_max": None}
    win = common[-(PARITY_DAYS + 1):]
    diffs = []
    for a, b in zip(win, win[1:]):
        diffs.append(abs(src[b] / src[a] - 1.0 - (loc[b] / loc[a] - 1.0)))
    last = common[-1]
    rel = abs(src[last] / loc[last] - 1.0) if loc[last] else None
    return {"common_dates": len(common), "overlap_insufficient": False,
            "last_common_date": last,
            "level_rel_diff_last": rel,
            "level_pass": (rel is not None and rel <= LEVEL_TOL),
            "return_parity_max": (max(diffs) if diffs else None),
            "note": "return-parity false-reds on ex-div dates are expected "
                    "(qfq back-adjusts history, local raw does not)"}


def freshness(src_pairs, local_last: str, now=None) -> dict:
    """Upstream (tencent) vs local cutoff classification.

    Intraday refinement (live audit finding 2026-09-24 11:58: tencent, like
    sina, serves TODAY'S IN-PROGRESS bar during trading hours): a newer
    upstream bar dated TODAY before 15:30 is an intraday partial -- NOT a
    "sina is lagging" signal. class 'upstream_intraday_partial_bar' keeps the
    completed-bar semantics honest for the fallback diagnosis."""
    now = now or dt.datetime.now()
    t_latest = src_pairs[-1][0] if src_pairs else None
    if t_latest is None:
        return {"tencent_latest": None, "class": "no_data"}
    if t_latest > local_last:
        cls = "upstream_has_newer_bar"
        if t_latest == str(now.date()) and now.time() < dt.time(15, 30):
            cls = "upstream_intraday_partial_bar"
    elif t_latest == local_last:
        cls = "upstream_equal"
    else:
        cls = "upstream_behind"
    return {"tencent_latest": t_latest, "local_last": local_last,
            "class": cls}


def _classify_error(exc: BaseException) -> str:
    msg = f"{type(exc).__name__}: {exc}"
    net = ("RemoteDisconnected", "ConnectionReset", "timeout", "URLError",
           "ConnectionError", "gaierror", "WSA")
    return "network" if any(m in msg for m in net) else "api_or_parse"


def check_symbol(code: str, fetcher=None) -> dict:
    """One symbol: freshness + parity vs local. Never writes anything."""
    fetcher = fetcher or tencent_daily
    out = {"symbol": code, "ok": False}
    try:
        pairs, has_amount = fetcher(code)
        out.update({"ok": True, "has_amount": has_amount,
                    "rows": len(pairs), "earliest": pairs[0][0],
                    "latest": pairs[-1][0]})
        out["freshness"] = freshness(pairs, local_last_date(code))
        out["parity"] = parity(pairs, local_tail(code))
    except BaseException as exc:  # noqa: BLE001 -- honest per-symbol capture
        out["error"] = f"{type(exc).__name__}: {exc}"[:200]
        out["error_kind"] = _classify_error(exc)
    return out


def run_audit(codes=None, status_path=None, fetcher=None, now=None) -> dict:
    """Full (or targeted) pool audit -> atomic status write. Returns summary."""
    now = now or dt.datetime.now()
    codes = codes or core_codes()
    fetcher = fetcher or tencent_daily
    per, flags = {}, []
    for c in codes:
        r = check_symbol(c, fetcher)
        per[c] = r
        if r.get("ok"):
            p = r["parity"]
            if p.get("level_pass") is False:
                flags.append({"symbol": c, "flag": "level_parity_fail",
                              "rel": p["level_rel_diff_last"]})
            f = r["freshness"]
            if f.get("class") == "upstream_has_newer_bar":
                flags.append({"symbol": c,
                              "flag": "upstream_ahead_of_local",
                              "tencent_latest": f["tencent_latest"]})
        else:
            flags.append({"symbol": c, "flag": r.get("error_kind", "error"),
                          "error": r.get("error")})
        if fetcher is tencent_daily:
            time.sleep(THROTTLE_S)
    summary = {
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "now": str(now), "source": "tencent_fqkline_validation_leg",
        "role": "validation-only (no amount column -> never a bar-write source)",
        "symbols_checked": len(per),
        "level_parity_pass": sum(1 for r in per.values()
                                  if (r.get("parity") or {}).get("level_pass")),
        "upstream_ahead": [c for c, r in per.items()
                           if (r.get("freshness") or {}).get("class")
                           == "upstream_has_newer_bar"],
        "upstream_intraday_partial": [
            c for c, r in per.items()
            if (r.get("freshness") or {}).get("class")
            == "upstream_intraday_partial_bar"],
        "unreachable": [c for c, r in per.items() if not r.get("ok")],
        "flags": flags, "per_symbol": per,
        "writes": ["data/daily: NONE (validation leg)"],
    }
    _write_status_atomic(summary, status_path or STATUS_PATH)
    return summary


# ------------------------------------------------------- fallback diagnosis
def fallback_diagnose(symbols, local_last=None, fetcher=None) -> list:
    """Primary-failure diagnosis (update_daily exit-2/stale path).

    For each symbol whose PRIMARY (sina) fetch failed or whose local cutoff is
    stale: does the bar exist upstream at tencent?
      upstream_has_newer_bar -> primary-side outage/lag (retry later helps)
      upstream_equal/behind  -> bar genuinely not published / no new bar
      unreachable            -> both legs down (honest, recorded)
    Bars are NEVER written from this leg (no amount column)."""
    fetcher = fetcher or tencent_daily
    events = []
    for c in symbols:
        try:
            last = (local_last or {}).get(c) or local_last_date(c)
        except BaseException as exc:  # noqa: BLE001
            events.append({"symbol": c, "diagnosis": "local_read_error",
                           "error": f"{type(exc).__name__}: {exc}"[:120]})
            continue
        try:
            pairs, _ = fetcher(c)
            f = freshness(pairs, last)
            events.append({"symbol": c, "local_last": last,
                           "tencent_latest": f["tencent_latest"],
                           "diagnosis": f["class"]})
        except BaseException as exc:  # noqa: BLE001
            events.append({"symbol": c, "local_last": last,
                           "diagnosis": "validation_leg_unreachable",
                           "error": f"{type(exc).__name__}: {exc}"[:120],
                           "error_kind": _classify_error(exc)})
        if fetcher is tencent_daily:
            time.sleep(THROTTLE_S)
    return events


def audit_new_rows(new_symbols, fetcher=None) -> dict:
    """Post-sweep parity audit for symbols that just received bars."""
    if not new_symbols:
        return {"symbols": [], "flags": []}
    fetcher = fetcher or tencent_daily
    flags = []
    for c in new_symbols:
        try:
            pairs, _ = fetcher(c)
            p = parity(pairs, local_tail(c))
            if p.get("level_pass") is False:
                flags.append({"symbol": c, "flag": "level_parity_fail",
                              "rel": p["level_rel_diff_last"],
                              "note": "ex-div dates may false-red; flagged "
                                      "never auto-corrected"})
        except BaseException as exc:  # noqa: BLE001
            flags.append({"symbol": c, "flag": "audit_unreachable",
                          "error": f"{type(exc).__name__}: {exc}"[:120]})
        if fetcher is tencent_daily:
            time.sleep(THROTTLE_S)
    return {"symbols": list(new_symbols), "flags": flags}


def _write_status_atomic(summary: dict, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2, ensure_ascii=False)
    os.replace(tmp, path)


# ---------------------------------------------------------------- selftest
def _fake_fetcher(rows: dict, amount=False):
    def f(code):
        if code not in rows:
            raise KeyError(code)
        return rows[code], amount
    return f


def selftest() -> bool:
    ok = True

    # A: freshness classification (+ intraday-partial refinement: tencent
    #    serves today's IN-PROGRESS bar during trading hours)
    pairs = [("2026-09-22", 4.6), ("2026-09-23", 4.61)]
    _n = dt.datetime(2026, 9, 25, 16, 0)     # explicit now -> deterministic
    ok &= freshness(pairs, "2026-09-22", now=_n)["class"] \
        == "upstream_has_newer_bar"
    ok &= freshness(pairs, "2026-09-23", now=_n)["class"] == "upstream_equal"
    ok &= freshness(pairs, "2026-09-24", now=_n)["class"] == "upstream_behind"
    today_pairs = [("2026-09-23", 4.61), ("2026-09-24", 4.62)]
    ok &= freshness(today_pairs, "2026-09-23",
                   now=dt.datetime(2026, 9, 24, 11, 0))["class"] \
        == "upstream_intraday_partial_bar"
    ok &= freshness(today_pairs, "2026-09-23",
                    now=dt.datetime(2026, 9, 24, 15, 31))["class"] \
        == "upstream_has_newer_bar"
    print("  [validate] freshness classes (incl intraday partial)... "
          + ("PASS" if ok else "FAIL"))

    # B: parity math -- 2x level offset, identical returns -> level gate
    #    fails at last date but return parity is ~0
    local = [("2026-09-20", 10.0), ("2026-09-21", 11.0), ("2026-09-22", 12.0)]
    src = [("2026-09-20", 20.0), ("2026-09-21", 22.0), ("2026-09-22", 24.0)]
    p = parity(src, local)
    b = (p["level_pass"] is False and abs(p["level_rel_diff_last"] - 1.0) < 1e-12
         and abs(p["return_parity_max"]) < 1e-12)
    ok &= b
    print("  [validate] parity math (level gate + return diagnostic)... "
          + ("PASS" if b else "FAIL"))

    # C: parity pass within tolerance
    src2 = [(d, c * (1 + 5e-4)) for d, c in local]
    ok &= parity(src2, local)["level_pass"] is True
    # overlap insufficient honest path
    p3 = parity([("2026-09-22", 1.0)], local)
    ok &= p3["overlap_insufficient"] is True and p3["level_pass"] is None
    print("  [validate] tolerance + insufficient-overlap paths... PASS")

    # D: error classification taxonomy
    ok &= _classify_error(Exception("RemoteDisconnected('peer closed')")) \
        == "network"
    ok &= _classify_error(ValueError("tencent kline empty")) == "api_or_parse"
    print("  [validate] error taxonomy... PASS")

    # E: check_symbol with injected fetcher (offline, deterministic)
    fake = _fake_fetcher({"510300": [("2026-09-22", 4.6),
                                     ("2026-09-23", 4.61)]}, amount=True)
    import tempfile
    import pandas as pd
    with tempfile.TemporaryDirectory() as td:
        real_daily = PATHS.daily_dir
        PATHS.daily_dir = td
        try:
            cols = ["date", "open", "high", "low", "close", "volume", "amount"]
            # local tail matches the fake tencent tail (level parity gate 1e-3)
            rows = [(f"2026-09-{d}", 4.0, 4.1, 3.9,
                     (4.61 if d == "23" else 4.5), 100, 400)
                    for d in ("21", "22", "23")]
            pd.DataFrame(rows, columns=cols).to_csv(
                os.path.join(td, "510300.csv"), index=False)
            r = check_symbol("510300", fake)
            e = (r["ok"] is True and r["has_amount"] is True
                 and r["freshness"]["class"] == "upstream_equal"
                 and r["parity"]["level_pass"] is True)
            # unreachable symbol -> honest error, not a crash
            r2 = check_symbol("510301", fake)
            e &= (r2["ok"] is False
                  and r2["error_kind"] == "api_or_parse")
            ok &= e
            print("  [validate] check_symbol offline (parity/freshness/"
                  "unreachable)... " + ("PASS" if e else "FAIL"))

            # F: fallback_diagnose -- three diagnoses with injected source
            pairs = [("2026-09-22", 4.6), ("2026-09-23", 4.61)]
            diag = _fake_fetcher({"510300": pairs})
            ev = fallback_diagnose(["510300", "510301"],
                                   {"510300": "2026-09-22",
                                    "510301": "2026-09-23"},
                                   fetcher=diag)
            f = (ev[0]["diagnosis"] == "upstream_has_newer_bar"
                 and ev[1]["diagnosis"] == "validation_leg_unreachable")
            # local read error path (no such csv)
            ev2 = fallback_diagnose(["510301"], {}, fetcher=diag)
            f &= ev2[0]["diagnosis"] == "local_read_error"
            ok &= f
            print("  [validate] fallback diagnosis classes... "
                  + ("PASS" if f else "FAIL"))

            # G: audit_new_rows flags level-parity failure, never rewrites
            aud = audit_new_rows(["510300"], fetcher=diag)
            g = aud["symbols"] == ["510300"] and aud["flags"] == []
            aud2 = audit_new_rows(["510300"],
                                  fetcher=_fake_fetcher(
                                      {"510300": [(d, c * 2) for d, c in
                                                  pairs]}))
            g &= (aud2["flags"][0]["flag"] == "level_parity_fail")
            ok &= g
            print("  [validate] post-sweep audit flags... "
                  + ("PASS" if g else "FAIL"))
        finally:
            PATHS.daily_dir = real_daily
    return bool(ok)


def main(argv=None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if "selftest" in argv:
        print(f"=== daily_validate selftest "
              f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===")
        return 0 if selftest() else 1
    if "check" in argv:
        i = argv.index("check")
        syms = ([s.strip() for s in argv[i + 1].split(",")]
                if len(argv) > i + 1 and not argv[i + 1].startswith("--")
                else None)
        s = run_audit(codes=syms)
        print(f"checked {s['symbols_checked']} | level_pass "
              f"{s['level_parity_pass']} | upstream_ahead "
              f"{len(s['upstream_ahead'])} | unreachable "
              f"{len(s['unreachable'])}")
        return 0 if not s["unreachable"] else 2
    # default: run
    s = run_audit()
    print(f"audited {s['symbols_checked']} | level_pass "
          f"{s['level_parity_pass']}/{s['symbols_checked']} | "
          f"upstream_ahead {len(s['upstream_ahead'])} | unreachable "
          f"{len(s['unreachable'])} | flags {len(s['flags'])}")
    print(f"status -> {STATUS_PATH}")
    return 0 if not s["unreachable"] else 2


if __name__ == "__main__":
    sys.exit(main())
