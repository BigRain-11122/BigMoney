"""T-69 wave-2b: OPTIONS forward daily collector (O-20260925-1158 continuation).

Purpose: sina retention window keeps only recent expiry months (R190
retention_boundary), so the wave-2 backfill pilot measured a thin 160-day
window (T-67 s2: 0/18 honest fail). This lane accumulates FORWARD history:
each pass enumerates the currently listed months (codes face) and pulls every
listed contract's full available daily history, appending rows the local
panel lacks. Near-month standard-roll contracts accumulate month by month.
DEFINITIVE BATCH LAW (T-67 prereg §2 frozen): new prereg only after >=12
months forward history; this lane is data collection only -- zero backtest
claims, zero engine changes, registry face data/options/contracts.json stays
the s0/runner anchor (never rewritten here).

Faces (sina same-source as s0 census, akshare):
  list   ak.option_sse_list_sina(display, exchange="null")     -> listed months
  codes  ak.option_sse_codes_sina(看涨/看跌, month, underlying) -> contract codes
  expire ak.option_sse_expire_day_sina(month, display)          -> expiry items
  daily  ak.option_sse_daily_sina(code) -> [日期,开盘,最高,最低,收盘,成交量]

Guards (update_futures / update_moneyflow family precedents):
- lane ownership (R31): auto-gate acts only on LANE_OWNER (bm-a, T-67 chain
  owner); other machines stdout-only no-op, zero shared-state writes.
- daily-cutoff no-op: pass-complete mirror panel.last_pass_date vs
  expected_latest_bar_date (15:30 convention, local ETF calendar primary) --
  zero-network no-op when covered (update_futures cutoff_gate).
- completeness filter: today's row kept only >= 15:30; rows dated beyond
  today dropped (future-row guard, R186 observation-date family).
- incremental merge: append-only, row-level overlap verify (price cols,
  tol 1e-6); source-rewrites-history -> mismatch flag, local file NOT
  rewritten, exit 3 (update_futures precedent). Pass with fresh mismatches
  does NOT set last_pass_date (next pass retries); mismatch retry count >= 3
  -> mismatch_stale (excluded from universe, disclosed, bounded loop).
- expired/dead sweep: contracts on disk but absent from the codes face get
  ONE tail pull (month not yet past target); EMPTY result or expiry-month
  already past target -> final mark in data/options/forward_meta.json (never
  re-pulled). Zero-volume gap days are a known source face (R194: contracts
  legitimately lack bar rows) -- collector never fabricates rows.
- checkpoint resume: results/options_update_cells.jsonl scoped by pass target
  date; conn-fuse 3 consecutive contract fails -> honest stop exit 2,
  checkpoint preserved (MF_COLLECTOR / s0 family).
- 30-min spawn throttle (mirror written BEFORE acting, r18 lesson) + pid lock
  (stale lock self-heals); detached silent child, zero popups (R20).

Budget (R192 lesson: census x sustained payload): ~16 codes pulls + ~8
expiry pulls (~2s pace) + ~200 contracts x (payload 0.4-9s + 0.5s pace)
~ 5-8 min/pass, once per trading day post-15:30.

Exit codes (gate):        0 = ok/no-op/spawned/in-progress; 2 = machinery failure
Exit codes (refresh): 0 = pass complete; 2 = incomplete (fuse/machinery);
                       3 = complete but overlap mismatches (local untouched)

Usage: python scripts/update_options.py            # S6 gate step
       python scripts/update_options.py refresh    # detached worker
       python scripts/update_options.py status
       python scripts/update_options.py selftest
"""
from __future__ import annotations

import datetime as dt
import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPT_DIR = os.path.join(ROOT, "data", "options")
PANEL_DIR = os.path.join(OPT_DIR, "daily")
META_JSON = os.path.join(OPT_DIR, "forward_meta.json")
REGISTRY_JSON = os.path.join(OPT_DIR, "contracts.json")
LOCK = os.path.join(OPT_DIR, "_refresh.lock")
STATUS = os.path.join(ROOT, "results", "options_update_status.json")
CELLS_JSONL = os.path.join(ROOT, "results", "options_update_cells.jsonl")
LOG = os.path.join(ROOT, "logs", "options_refresh.log")

LANE_OWNER = "bm-a"       # R31 lane-ownership precedent (T-67/T-69 chain owner)
UNDERLYINGS = {"510050": {"display": "50ETF"}, "510300": {"display": "300ETF"}}
DIRECTIONS = {"call": "看涨期权", "put": "看跌期权"}
OPT_COLS = ["date", "open", "high", "low", "close", "volume"]
SLEEP_CODES = 2.0          # s0 census pace (enumeration face)
SLEEP_CONTRACT = 0.5       # s0 CONTRACT_SLEEP (budget input: ~5min/200)
MIN_SPAWN_S = 30 * 60      # spawn throttle (moneyflow family)
FUSE_N = 3                 # consecutive contract fails -> honest stop

# family precedents, zero reimplementation (anti-dup law)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from options_s0_panel_probe import normalize_daily_df  # noqa: E402
from update_futures import (  # noqa: E402
    atomic_write, completeness_filter, cutoff_gate, expected_latest_bar_date,
    merge_incremental, validate_rows)


# ------------------------------------------------------------- pure helpers

def _clear_proxy_env():
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
              "all_proxy", "ALL_PROXY"):
        os.environ.pop(k, None)


def parse_month(mo):
    """'202610' -> (2026, 10); None on any deviation (honest no-parse)."""
    try:
        s = str(mo)
        if len(s) == 6 and s.isdigit():
            return int(s[:4]), int(s[4:])
    except Exception:
        pass
    return None


def month_covered_target(month, target):
    """True when a contract expiring in `month` cannot have bars on/after
    `target` (contract month strictly earlier than the target's month).
    Same-month contracts stay pull-eligible until the source drops them."""
    pm, pt = parse_month(month), parse_month(target.replace("-", "")[:6])
    if pm is None or pt is None:
        return False
    return pm < pt


def should_pull_extra(code, month, final_mark, target):
    """Dead-sweep admission (pure): enumerated-absent disk contracts."""
    if final_mark:
        return False, f"final:{final_mark}"
    if month_covered_target(month, target):
        return False, "expired_before_target"
    return True, "tail sweep"


def fuse_step(fuse, status_ok):
    return 0 if status_ok else fuse + 1


def mismatch_goes_stale(count):
    return (count or 0) >= 3


def drop_future_rows(rows, now=None):
    now = now or dt.datetime.now()
    today = now.date().isoformat()
    kept = [r for r in rows if str(r["date"]) <= today]
    return kept, len(rows) - len(kept)


# ------------------------------------------------------------ csv helpers

def rows_to_csv_text(rows):
    buf = io.StringIO()
    buf.write(",".join(OPT_COLS) + "\n")
    for r in rows:
        buf.write(f"{r['date']},{r['open']},{r['high']},{r['low']},"
                  f"{r['close']},{r['volume']}\n")
    return buf.getvalue()


def read_local_csv(path):
    import csv as _csv
    if not os.path.exists(path):
        return []
    with io.open(path, "r", encoding="utf-8") as f:
        rd = _csv.DictReader(f)
        rows = []
        for x in rd:
            r = {"date": str(x["date"])}
            for col in OPT_COLS[1:]:
                v = x.get(col, "")
                r[col] = float(v) if v not in ("", None) else None
            rows.append(r)
    return rows


def load_json(path, default):
    if os.path.exists(path):
        try:
            with io.open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def write_status(payload):
    atomic_write(STATUS, json.dumps(payload, ensure_ascii=False, indent=1))


def load_meta():
    m = load_json(META_JSON, {"contracts": {}, "expiry": {}})
    m.setdefault("contracts", {})
    m.setdefault("expiry", {})
    return m


def save_meta(m):
    atomic_write(META_JSON, json.dumps(m, ensure_ascii=False, indent=1))


# ---------------------------------------------------------- checkpoint

def load_cells(pass_target):
    """{code: line} for lines scoped to this pass target; foreign-pass lines
    dropped (new pass = fresh file, s0 CELLS_JSONL resume pattern)."""
    done, foreign, torn = {}, 0, 0
    if os.path.exists(CELLS_JSONL):
        with io.open(CELLS_JSONL, "r", encoding="utf-8") as f:
            lines = [ln for ln in f.read().splitlines() if ln.strip()]
        keep = []
        for ln in lines:
            try:
                o = json.loads(ln)
            except json.JSONDecodeError:
                torn += 1
                continue
            if str(o.get("pass")) == str(pass_target):
                done[str(o.get("code"))] = o
                keep.append(ln)
            else:
                foreign += 1
        if foreign or torn:  # rewrite scoped to current pass
            with io.open(CELLS_JSONL, "w", encoding="utf-8") as f:
                f.write("".join(ln + "\n" for ln in keep))
    return done


# ----------------------------------------------------------------- lock

def _write_lock():
    os.makedirs(OPT_DIR, exist_ok=True)
    atomic_write(LOCK, json.dumps({"pid": os.getpid(),
                                   "ts": dt.datetime.now().isoformat(timespec="seconds")}))


def _clear_lock():
    try:
        os.remove(LOCK)
    except FileNotFoundError:
        pass


def _pid_alive(pid):
    try:
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV"],
                              capture_output=True, timeout=15)
        return f'"{pid}"' in out.stdout.decode("utf-8", errors="replace")
    except Exception:
        return False


def _lock_alive():
    if not os.path.exists(LOCK):
        return False
    try:
        with io.open(LOCK, "r", encoding="utf-8") as f:
            pid = int(json.load(f).get("pid", 0))
        if pid and _pid_alive(pid):
            return True
    except Exception:
        pass
    return False


def _lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     "r", encoding="utf-8-sig") as f:
            return str(json.load(f).get("machine_id", ""))
    except Exception:
        return ""


def spawn_detached(arg):
    os.makedirs(os.path.dirname(LOG), exist_ok=True)
    flags = (subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
             | subprocess.CREATE_NO_WINDOW)
    with io.open(LOG, "a", encoding="utf-8") as lf:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), arg],
                         stdout=lf, stderr=subprocess.STDOUT,
                         stdin=subprocess.DEVNULL, creationflags=flags,
                         close_fds=False)


# ------------------------------------------------------------- fetch faces

def _fetch(fn, **kw):
    """(ok, payload, meta) probe-style wrapper (honest FAIL meta)."""
    t0 = time.time()
    try:
        r = fn(**kw)
    except Exception as e:
        return False, None, {"status": "FAIL",
                            "err": f"{type(e).__name__}: {str(e)[:160]}",
                            "sec": round(time.time() - t0, 1)}
    if r is None or (hasattr(r, "__len__") and len(r) == 0):
        return True, None, {"status": "EMPTY", "sec": round(time.time() - t0, 1)}
    return True, r, {"status": "OK", "rows": int(len(r)),
                     "sec": round(time.time() - t0, 1)}


def enumerate_universe():
    """Months/codes/expiry faces. Returns (code_map, months_face, meta_expiry,
    enum_fails) where code_map: code -> (underlying, month, direction)."""
    import akshare as ak
    code_map, enum_fails = {}, []
    months_face, meta_expiry = {}, {}
    for u, cfg in UNDERLYINGS.items():
        ok, r, meta = _fetch(ak.option_sse_list_sina, symbol=cfg["display"],
                             exchange="null")
        months_face[u] = {"meta": meta,
                          "months": [str(x) for x in r] if r is not None else []}
        if not ok or not months_face[u]["months"]:
            enum_fails.append(f"list:{u}:{meta['status']}")
        time.sleep(SLEEP_CODES)
    for u, face in months_face.items():
        for mo in face["months"]:
            ok, r, meta = _fetch(ak.option_sse_expire_day_sina,
                                 trade_date=mo,
                                 symbol=UNDERLYINGS[u]["display"])
            if ok and r is not None:
                meta_expiry.setdefault(u, {})[mo] = [str(x) for x in r]
            elif not ok:
                enum_fails.append(f"expiry:{u}:{mo}:{meta['status']}")
            time.sleep(SLEEP_CODES)
            for dkey, dsym in DIRECTIONS.items():
                ok, r, meta = _fetch(ak.option_sse_codes_sina, symbol=dsym,
                                      trade_date=mo, underlying=u)
                codes = []
                if ok and r is not None and "期权代码" in r.columns:
                    codes = [str(x) for x in r["期权代码"].astype(str).tolist()]
                elif not ok:
                    enum_fails.append(f"codes:{u}:{mo}:{dkey}:{meta['status']}")
                for c in codes:
                    code_map[c] = (u, mo, dkey)
                time.sleep(SLEEP_CODES)
    return code_map, months_face, meta_expiry, enum_fails


def fetch_contract_daily(code):
    import akshare as ak
    ok, r, meta = _fetch(ak.option_sse_daily_sina, symbol=code)
    if not ok or r is None:
        return None, meta
    rows, nmeta = normalize_daily_df(r)
    if rows is None:
        meta.update(nmeta)
        return None, meta
    meta.update(nmeta)
    return rows, meta


# ----------------------------------------------------------------- refresh

def refresh():
    now = dt.datetime.now()
    target = expected_latest_bar_date(now)
    _write_lock()
    try:
        st = load_json(STATUS, {})
        meta = load_meta()
        registry = load_json(REGISTRY_JSON, {})
        reg_contracts = registry.get("contracts", []) if isinstance(registry, dict) else []
        reg_month = {str(c.get("code")): c.get("month") for c in reg_contracts
                     if isinstance(c, dict) and c.get("code")}

        _clear_proxy_env()
        print(f"[opt-refresh] pass target={target} start {now.isoformat(timespec='seconds')}",
              flush=True)
        code_map, months_face, meta_expiry, enum_fails = enumerate_universe()
        for u, mos in meta_expiry.items():          # expiry face -> meta store
            meta["expiry"].setdefault(u, {}).update(mos)
        save_meta(meta)

        ckpt = load_cells(target)
        disk_codes = sorted(os.path.splitext(f)[0] for f in os.listdir(PANEL_DIR)
                            if f.endswith(".csv")) if os.path.isdir(PANEL_DIR) else []
        extra = [c for c in disk_codes if c not in code_map]
        mismatch_map = dict(st.get("mismatch") or {})

        universe = []   # (code, kind, month)
        for c, (u, mo, dkey) in sorted(code_map.items()):
            if c in mismatch_map and mismatch_goes_stale(mismatch_map[c].get("count")):
                continue
            universe.append((c, "live", mo))
        sweep_skipped, sweep_planned = [], []
        for c in extra:
            mrow = meta["contracts"].get(c) or {}
            month = mrow.get("month") or reg_month.get(c)
            pull, why = should_pull_extra(c, month, mrow.get("final"), target)
            if pull and c in mismatch_map and mismatch_goes_stale(mismatch_map[c].get("count")):
                pull, why = False, "mismatch_stale"
            if pull:
                sweep_planned.append(c)
                universe.append((c, "extra", month))
            else:
                if why == "expired_before_target" and not mrow.get("final"):
                    meta["contracts"][c] = dict(mrow, month=month,
                                                final="expired_before_target",
                                                final_ts=now.isoformat(timespec="seconds"))
                sweep_skipped.append(f"{c}:{why}")
        save_meta(meta)

        pending = [(c, k, m) for c, k, m in universe if c not in ckpt]
        print(f"[opt-refresh] enumerated={len(code_map)} disk={len(disk_codes)} "
              f"extra_sweep={len(sweep_planned)} sweep_skip={len(sweep_skipped)} "
              f"ckpt_done={len(ckpt)} pending={len(pending)} "
              f"months={ {u: f['months'] for u, f in months_face.items()} }", flush=True)

        fuse, fails, mismatches, appended_total, max_collected = 0, [], [], 0, target
        cells_f = io.open(CELLS_JSONL, "a", encoding="utf-8")
        for i, (code, kind, month) in enumerate(pending):
            line = {"pass": target, "code": code, "kind": kind,
                    "month": month, "status": "fail", "appended": 0}
            try:
                rows, fmeta = fetch_contract_daily(code)
                line["daily_meta"] = fmeta
                if rows is None:
                    if kind == "extra":
                        mrow = meta["contracts"].get(code) or {}
                        meta["contracts"][code] = dict(
                            mrow, month=month, final="final_empty",
                            final_ts=now.isoformat(timespec="seconds"))
                        save_meta(meta)
                        line["status"] = "final_empty"
                    else:
                        line["status"] = "fail"
                        line["reason"] = f"daily {fmeta['status']}"
                        fails.append(code)
                else:
                    rows, dropped_today = completeness_filter(rows, now=now)
                    rows, dropped_future = drop_future_rows(rows, now=now)
                    if dropped_today:
                        line["dropped_today_partial"] = dropped_today
                    if dropped_future:
                        line["dropped_future"] = dropped_future
                    err = validate_rows(rows)
                    if err:
                        raise RuntimeError(f"validation_fail: {err}")
                    p = os.path.join(PANEL_DIR, f"{code}.csv")
                    local = read_local_csv(p)
                    res = merge_incremental(local, rows)
                    line["overlap"] = res["overlap"]
                    if not res["merged"]:
                        mismatches.append(code)
                        prev = mismatch_map.get(code) or {"count": 0}
                        mismatch_map[code] = {"count": prev.get("count", 0) + 1,
                                              "date": res["mismatch"],
                                              "ts": now.isoformat(timespec="seconds")}
                        st["mismatch"] = mismatch_map
                        write_status(st)
                        line["status"] = "mismatch"
                        line["mismatch_at"] = res["mismatch"]
                    else:
                        if res["appended"]:
                            atomic_write(p, rows_to_csv_text(res["merged_rows"]))
                        line["status"] = "ok"
                        line["appended"] = res["appended"]
                        line["rows_total"] = len(res["merged_rows"])
                        appended_total += res["appended"]
                        if res["merged_rows"]:
                            max_collected = max(max_collected,
                                                str(res["merged_rows"][-1]["date"]))
                        if code in mismatch_map:     # recovered -> clear retry
                            mismatch_map.pop(code, None)
                            st["mismatch"] = mismatch_map
                            write_status(st)
            except Exception as e:
                line["status"] = "fail"
                line["reason"] = f"{type(e).__name__}: {str(e)[:160]}"
                fails.append(code)
            ok_line = line["status"] in ("ok", "final_empty")
            fuse = fuse_step(fuse, ok_line)
            cells_f.write(json.dumps(line, ensure_ascii=False) + "\n")
            cells_f.flush()
            if (i + 1) % 25 == 0 or i + 1 == len(pending):
                print(f"[opt-refresh] {i+1}/{len(pending)} "
                      f"appended={appended_total} fuse={fuse}", flush=True)
            if fuse >= FUSE_N:
                cells_f.close()
                st.update({"ts": now.isoformat(timespec="seconds"),
                           "mode": "refresh: conn-fuse honest stop",
                           "panel": dict(st.get("panel") or {},
                                         pass_target=target, complete=False,
                                         fails=len(fails))})
                write_status(st)
                print(f"[opt-refresh] conn-fuse: {FUSE_N} consecutive fails, "
                      f"honest stop (checkpoint preserved)", flush=True)
                return 2
            time.sleep(SLEEP_CONTRACT)
        cells_f.close()

        pass_ok = not enum_fails and not fails
        if pass_ok and not mismatches:
            last_pass = max(str(target), str(max_collected))
        else:
            last_pass = (st.get("panel") or {}).get("last_pass_date")
        for c in list(mismatch_map):     # stale escalation -> meta exclusion
            if mismatch_goes_stale(mismatch_map[c].get("count")):
                mrow = meta["contracts"].get(c) or {}
                meta["contracts"][c] = dict(mrow, final="mismatch_stale",
                                            final_ts=now.isoformat(timespec="seconds"))
        save_meta(meta)
        st.update({
            "ts": dt.datetime.now().isoformat(timespec="seconds"),
            "mode": "refresh: forward pass complete" if pass_ok else
                    "refresh: pass with honest failures",
            "months_face": months_face,
            "enum_fails": enum_fails,
            "mismatch": mismatch_map,
            "panel": {
                "last_pass_date": last_pass,
                "pass_target": str(target),
                "complete": bool(pass_ok and not mismatches),
                "universe": len(pending) + len(ckpt),
                "attempted": len(pending),
                "appended": appended_total,
                "max_collected": str(max_collected),
                "fails": sorted(set(fails)),
                "mismatches": sorted(set(mismatches)),
                "final_marks": sum(1 for v in meta["contracts"].values()
                                   if v.get("final")),
            },
            "claim": "T-2026-09-25-69 wave-2b options forward collector (bm-a)",
        })
        write_status(st)
        print(f"[opt-refresh] done pass_ok={pass_ok} appended={appended_total} "
              f"mismatches={sorted(set(mismatches))} fails={sorted(set(fails))} "
              f"last_pass={last_pass}", flush=True)
        if mismatches:
            return 3
        if not pass_ok:
            return 2
        return 0
    finally:
        _clear_lock()


# --------------------------------------------------------------------- gate

def gate():
    st = load_json(STATUS, {})
    now = dt.datetime.now()
    owner = _lane_owner_id()
    if owner != LANE_OWNER:
        # R31 lane guard: non-owner = stdout-only, zero shared-state writes
        print(f"no-op: options lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    panel = st.get("panel") or {}
    needs, expected, reason = cutoff_gate(panel.get("last_pass_date"), now)
    if not needs:
        st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = "no-op: cutoff covered"
        st["no_op_reason"] = reason
        st["expected_cutoff"] = expected
        write_status(st)
        print(f"no-op: {reason} -> zero network")
        return 0
    last = st.get("last_spawn_attempt")
    if last:
        try:
            age = (now - dt.datetime.fromisoformat(last)).total_seconds()
            if age < MIN_SPAWN_S:
                print(f"throttle: last spawn {last} ({age/60:.1f}min ago) "
                      f"< 30min -> no-op")
                return 0
        except Exception:
            pass
    if _lock_alive():
        st["ts"] = now.isoformat(timespec="seconds")
        st["mode"] = "refresh in progress (lock alive)"
        write_status(st)
        print("refresh already in progress (lock alive) -> no-op")
        return 0
    _clear_lock()  # stale lock from a dead run
    st["last_spawn_attempt"] = now.isoformat(timespec="seconds")  # mirror FIRST (r18)
    st["ts"] = now.isoformat(timespec="seconds")
    st["mode"] = "spawn: detached refresh"
    st["spawn_reason"] = reason
    write_status(st)
    spawn_detached("refresh")
    print(f"spawned detached options refresh: {reason}")
    return 0


def status():
    st = load_json(STATUS, {})
    print(json.dumps(st, ensure_ascii=False, indent=1)[:3000])
    return 0


# ----------------------------------------------------------------- selftest

def _selftest():
    import tempfile
    now = dt.datetime(2026, 9, 25, 23, 0)
    target = "2026-09-24"
    fails = 0

    def check(name, cond):
        nonlocal fails
        print(f"[{'PASS' if cond else 'FAIL'}] {name}")
        if not cond:
            fails += 1

    # S1 future-row guard
    rows = [{"date": "2026-09-24", "close": 1.0},
            {"date": "2026-09-26", "close": 2.0}]
    kept, dropped = drop_future_rows(rows, now=now)
    check("S1 future-row drop", len(kept) == 1 and dropped == 1
          and kept[0]["date"] == "2026-09-24")
    # S1b completeness integration (imported family guard)
    rows = [{"date": "2026-09-25", "close": 2.0}]
    kept, dropped = completeness_filter(rows, now=dt.datetime(2026, 9, 25, 10, 0))
    check("S1b pre-15:30 today-row dropped", len(kept) == 0 and dropped == 1)
    kept, _ = completeness_filter(rows, now=dt.datetime(2026, 9, 25, 15, 31))
    check("S1c post-15:30 today-row kept", len(kept) == 1)

    # S2 6-col csv roundtrip (s0 format: raw float f-strings, same header)
    rr = [{"date": "2026-09-24", "open": 0.0578, "high": 0.058,
           "low": 0.0575, "close": 0.0578, "volume": 12345.0}]
    text = rows_to_csv_text(rr)
    check("S2 header exact", text.splitlines()[0] == "date,open,high,low,close,volume")
    check("S2 float format s0-identical", "0.0578" in text and "12345.0" in text)
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "10000001.csv")
        atomic_write(p, text)
        back = read_local_csv(p)
        check("S2 roundtrip", back[0]["close"] == 0.0578
              and back[0]["volume"] == 12345.0)

    # S3 merge via family merge_incremental (price-col overlap, tol 1e-6)
    local = [{"date": "2026-09-23", "open": 0.1, "high": 0.11, "low": 0.09,
              "close": 0.1, "volume": 100.0}]
    src = local + [{"date": "2026-09-24", "open": 0.1, "high": 0.12, "low": 0.1,
                    "close": 0.11, "volume": 200.0}]
    res = merge_incremental(local, src)
    check("S3 clean append", res["merged"] and res["appended"] == 1
          and res["overlap"] == 1)
    # S3b idempotency: same source twice -> zero appended
    res2 = merge_incremental(res["merged_rows"], src)
    check("S3b idempotent re-merge", res2["merged"] and res2["appended"] == 0)
    # S3c mismatch -> local untouched (exit-3 semantics)
    bad = [dict(local[0]), dict(src[1])]
    bad[0]["close"] = 0.0999
    res3 = merge_incremental(local, bad)
    check("S3c mismatch blocks rewrite", not res3["merged"]
          and res3["mismatch"] == "2026-09-23" and res3["merged_rows"] is None)

    # S4 month expiry skip
    check("S4 expired month skip", month_covered_target("202609", "2026-09-24") is False
          and month_covered_target("202609", "2026-10-05") is True
          and month_covered_target("202610", "2026-09-24") is False
          and month_covered_target("202610", "2026-10-05") is False
          and month_covered_target(None, target) is False)

    # S5 dead-sweep admission (pure)
    pull, why = should_pull_extra("10011005", "202610", None, target)
    check("S5 tail sweep admitted", pull and why == "tail sweep")
    pull, why = should_pull_extra("10011005", "202609", None, "2026-10-05")
    check("S5b expired skipped", not pull and why == "expired_before_target")
    pull, why = should_pull_extra("10011005", "202610", "final_empty", target)
    check("S5c final mark skipped", not pull and why.startswith("final:"))

    # S6 fuse
    f = 0
    f = fuse_step(f, False); f = fuse_step(f, False); f = fuse_step(f, False)
    check("S6 fuse trips at 3", f >= FUSE_N)
    check("S6b fuse resets on ok", fuse_step(2, True) == 0)

    # S7 mismatch stale escalation
    check("S7 mismatch stale at 3", mismatch_goes_stale(3)
          and not mismatch_goes_stale(2) and not mismatch_goes_stale(None))

    # S8 cutoff gate integration (imported; constructed calendar)
    cal = ["2026-09-22", "2026-09-23", "2026-09-24"]
    needs, exp, _ = cutoff_gate("2026-09-24",
                                dt.datetime(2026, 9, 25, 23, 0), cal)
    check("S8 covered -> no fetch", not needs and exp == "2026-09-24")
    needs, exp, _ = cutoff_gate("2026-09-23",
                                dt.datetime(2026, 9, 25, 23, 0), cal)
    check("S8b behind -> fetch", needs and exp == "2026-09-24")
    needs, _, _ = cutoff_gate(None, dt.datetime(2026, 9, 25, 23, 0), cal)
    check("S8c first run -> fetch", needs)

    # S9 checkpoint scoping (pass-target keyed resume, foreign pass reset)
    with tempfile.TemporaryDirectory() as td:
        global CELLS_JSONL
        old_cells = CELLS_JSONL
        CELLS_JSONL = os.path.join(td, "cells.jsonl")
        with io.open(CELLS_JSONL, "w", encoding="utf-8") as f:
            f.write(json.dumps({"pass": "2026-09-23", "code": "A", "status": "ok"}) + "\n")
            f.write(json.dumps({"pass": "2026-09-24", "code": "B", "status": "ok"}) + "\n")
        done = load_cells("2026-09-24")
        check("S9 resume scoped to pass", "B" in done and "A" not in done)
        with io.open(CELLS_JSONL, "r", encoding="utf-8") as f:
            check("S9b foreign-pass lines reset", "2026-09-23" not in f.read())
        CELLS_JSONL = old_cells

    # S10 lane guard decision + lock (dead pid stale, moneyflow S10 family)
    check("S10 lane guard mismatch", "bm-c" != LANE_OWNER and "bm-a" == LANE_OWNER)
    with tempfile.TemporaryDirectory() as td:
        global LOCK
        old_lock = LOCK
        LOCK = os.path.join(td, "_refresh.lock")
        check("S10b missing lock -> dead", not _lock_alive())
        atomic_write(LOCK, json.dumps({"pid": 99999999, "ts": "x"}))
        check("S10c stale pid lock -> dead", not _lock_alive())
        LOCK = old_lock

    # S11 validate_rows family gate on option-shaped rows
    ok = validate_rows([{"date": "2026-09-23", "close": 0.0578},
                        {"date": "2026-09-24", "close": 0.0579}])
    check("S11 validation pass", ok is None)
    bad = validate_rows([{"date": "2026-09-24", "close": 0.0578},
                         {"date": "2026-09-23", "close": 0.0579}])
    check("S11b non-monotonic caught", bad is not None)

    # S12 parse_month honest forms
    check("S12 month parse", parse_month("202610") == (2026, 10)
          and parse_month("2026-10") is None and parse_month(None) is None)

    print(f"selftest: {'ALL PASS' if fails == 0 else f'{fails} FAIL'}")
    return 0 if fails == 0 else 1


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "gate"
    if cmd == "selftest":
        return _selftest()
    if cmd == "refresh":
        return refresh()
    if cmd == "status":
        return status()
    if cmd == "gate":
        return gate()
    print(f"unknown subcommand: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
