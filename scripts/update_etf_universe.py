"""Whole-universe ETF daily panel refresh leg (E29, bm-b lane).

Why this exists (r1106 measurement, digest
research/digests/DIGEST-20261021-e35-broad-book-screens.md):
the E24-E27 broad ETF line reads 1,231 eligible equity ETFs off
data/daily, but only the five pinned ladder members (update_etf_daily.py)
plus ~48 core codes are ever refreshed. 1,671 of 1,725 panel files stop on
exactly 2026-09-22 (a one-off 2026-10-17 bulk import). Every trailing
liquidity / turnover screen therefore loses coverage as the calendar
advances, and "strategy decay" and "data decay" become indistinguishable in
the readout. This leg is the missing refresh for the other 1,276 codes.

Design (deliberately reuses update_etf_daily.py, no re-implementation):
  * Universe = the ETF csv population actually on disk (same prefix rule as
    scripts/e27_universe_expansion.py: 15x SZ + 51x/52x/53x/55x/56x/58x SH),
    de-duplicated to the exchange-prefixed canonical name. Listing
    survivorship of that population is inherited and disclosed, not hidden.
  * Per-code full-history pull from the sina klc_kl.js endpoint (as-traded
    basis, same recipe/evidence as update_etf_daily.py r398 probe) and an
    append-only, overlap-verified merge (prices tol 1e-6, volume/amount
    int-round +-1) BEFORE any write. Mismatch -> that code's file is left
    untouched and counted, never silently re-anchored.
  * Resumable pass: a pass is a bounded slice of the pending work list
    (--max-seconds / --limit), and the done set is checkpointed in the
    status face, so a killed session loses at most the in-flight code.
  * Pacing 2.5s, conn-fuse 3 consecutive connection failures -> stop the
    pass (exit 2), 30-min spawn throttle for the detached full pass.
  * Lane guard: bm-b only (R31 lineage with update_astock_daily /
    update_etf_daily); other machines print an honest no-op.

Exit contract: 0 ok/no-op/pass-complete | 2 mechanism/source failure |
3 overlap mismatch (>=1 code left untouched).

Subcommands: selftest | status | run [--limit N] [--max-seconds S] |
             refresh (spawn detached pass)
"""

import datetime as dt
import glob
import io
import json
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import update_etf_daily as base  # noqa: E402  (reuse, do not re-implement)

DATA_DIR = os.path.join(ROOT, "data", "daily")
STATUS = os.path.join(ROOT, "results", "etf_universe_pull_status.json")
LANE_OWNER = "bm-b"                 # R31 lane law (broad ETF panel = bm-b)
ETF_PREFIXES = ("15", "51", "52", "53", "55", "56", "58")
SLEEP_S = 2.5
CONN_STOP = 3
SPAWN_THROTTLE_S = 1800
NAME_RE = re.compile(r"^(sh|sz)?((?:15|51|52|53|55|56|58)\d{4})(_[A-Za-z0-9]+)?\.csv$")


# ------------------------------------------------------------------ universe


def discover_universe(data_dir=None):
    """Canonical ETF symbols on disk. Prefixed copy wins over a bare copy;
    `_suffix` specialist copies (e.g. 510880_t73.csv) are skipped."""
    data_dir = data_dir or DATA_DIR
    picked = {}
    for path in sorted(glob.glob(os.path.join(data_dir, "*.csv"))):
        m = NAME_RE.match(os.path.basename(path))
        if not m:
            continue
        exch, code, suffix = m.group(1), m.group(2), m.group(3)
        if suffix:
            continue
        sym = (exch or ("sz" if code.startswith("15") else "sh")) + code
        prev = picked.get(sym)
        if prev is None or (exch and not prev[0]) or \
                (bool(exch) == bool(prev[0]) and
                 os.path.getsize(path) > os.path.getsize(prev[1])):
            picked[sym] = (exch, path)
    return [{"symbol": s, "path": p, "prefixed": bool(x)}
            for s, (x, p) in sorted(picked.items())]


def fetch_symbol(sym):
    """Full-history pull for a canonical symbol (sh510300 / sz159915).
    Same endpoint + JS decoder + normalize as the five-member leg, but the
    exchange prefix is carried by the symbol here (that leg assumes sh)."""
    import requests
    hist_url, js_decode, MiniRacer = base._endpoints()
    r = requests.get(hist_url.format(sym), timeout=15)
    r.raise_for_status()
    if "=" not in r.text or ";" not in r.text:
        raise ValueError(f"payload_face_drift:len={len(r.text)}")
    js = MiniRacer()
    js.eval(js_decode)
    dl = js.call("d", r.text.split("=")[1].split(";")[0].replace('"', ""))
    return base.normalize_decoded(dl)


def last_bar_date(path):
    """Cheap tail read: last data row's date (str) or None."""
    try:
        with io.open(path, "rb") as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(max(0, size - 512))
            tail = f.read().decode("utf-8", "replace")
        for line in reversed(tail.splitlines()):
            d = line.split(",")[0].strip()
            if re.match(r"^\d{4}-\d{2}-\d{2}$", d):
                return d
    except Exception:
        return None
    return None


def pending_work(universe, expected, done=None):
    """Codes whose panel does not yet reach the expected complete bar."""
    done = done or set()
    out = []
    for u in universe:
        if u["symbol"] in done:
            continue
        last = last_bar_date(u["path"])
        if last is None or str(last) < expected:
            u = dict(u)
            u["last"] = last
            out.append(u)
    return out


# -------------------------------------------------------------------- status


def load_status():
    try:
        with io.open(STATUS, encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return {}


def write_status(payload):
    tmp = STATUS + ".tmp"
    with io.open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)


def lane_owner_id():
    try:
        with io.open(os.path.join(ROOT, "fleet", "machine.json"),
                     encoding="utf-8-sig") as f:
            return json.load(f).get("machine_id")
    except Exception:
        return None


# ----------------------------------------------------------------------- run


def run_pass(limit=None, max_seconds=None, expected=None):
    owner = lane_owner_id()
    if owner != LANE_OWNER:
        print(f"no-op: broad ETF universe lane owned by {LANE_OWNER}, "
              f"not this machine ({owner or '?'})")
        return 0
    base._clear_proxy_env()
    now = dt.datetime.now()
    expected = expected or base.expected_latest_bar_date(now)
    universe = discover_universe()
    st = load_status()
    done = set(st.get("done", []))
    work = pending_work(universe, expected, done)
    if limit:
        work = work[:int(limit)]
    print(f"universe={len(universe)} expected={expected} "
          f"pending={len(work)} (done checkpoint={len(done)})")
    if not work:
        st.update({"ts": now.isoformat(timespec="seconds"),
                   "mode": "no-op: panel covered",
                   "expected_cutoff": expected,
                   "universe": len(universe)})
        write_status(st)
        return 0

    st.setdefault("pass", {})
    st["last_attempt"] = now.isoformat(timespec="seconds")
    started = time.time()
    appended_total, mismatch, fails, ok = 0, [], 0, 0
    conn_fails = 0
    for i, u in enumerate(work):
        if max_seconds and (time.time() - started) > float(max_seconds):
            print(f"slice stop: {i}/{len(work)} (max-seconds reached)")
            break
        sym, path = u["symbol"], u["path"]
        if conn_fails >= CONN_STOP:
            fails += 1
            st.setdefault("errors", []).append(
                f"{sym}: conn-fuse ({conn_fails} consecutive)")
            break
        try:
            try:
                rows = fetch_symbol(sym)
            except Exception as e:
                if type(e).__name__ in ("ConnectionError", "ConnectTimeout",
                                        "ReadTimeout", "Timeout", "URLError",
                                        "ChunkedEncodingError", "SSLError"):
                    conn_fails += 1
                    raise RuntimeError(f"conn_fail:{type(e).__name__} "
                                       f"({conn_fails}/{CONN_STOP})")
                conn_fails = 0
                raise
            conn_fails = 0
            rows, _dropped = base.completeness_filter(rows, now=now)
            err = base.validate_rows(rows)
            if err:
                raise RuntimeError(f"validation_fail: {err}")
            local = base.read_local_csv(path)
            res = base.merge_incremental(local, rows)
            if not res["merged"]:
                mismatch.append(f"{sym}@{res['mismatch']}")
                continue
            if res["appended"]:
                base.atomic_write(path, base.rows_to_csv_text(res["merged_rows"]))
                appended_total += res["appended"]
            done.add(sym)
            ok += 1
        except Exception as e:
            fails += 1
            st.setdefault("errors", []).append(f"{sym}: {type(e).__name__}: "
                                               f"{str(e)[:140]}")
        if i < len(work) - 1:
            time.sleep(SLEEP_S)

    st.update({
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "mode": "per-code full-history pull, append-only, overlap-verified",
        "expected_cutoff": expected,
        "universe": len(universe),
        "done": sorted(done),
        "pass": {"attempted": len(work), "ok": ok, "appended_rows": appended_total,
                 "mismatches": mismatch[-20:], "failures": fails,
                 "errors_tail": st.get("errors", [])[-20:]},
    })
    write_status(st)
    print(f"pass: ok={ok} appended={appended_total} mismatch={len(mismatch)} "
          f"fail={fails} checkpoint_done={len(done)}/{len(universe)}")
    if fails:
        return 2
    if mismatch:
        return 3
    return 0


def spawn_detached(limit=None):
    """Detached full pass (long job: survives the session tree kill)."""
    st = load_status()
    last = st.get("last_spawn")
    now = dt.datetime.now()
    if last:
        try:
            age = (now - dt.datetime.fromisoformat(last)).total_seconds()
            if age < SPAWN_THROTTLE_S:
                print(f"throttle: last spawn {last} ({age/60:.1f}min) <30min")
                return 0
        except Exception:
            pass
    logp = os.path.join(ROOT, "results", "logs", "etf_universe_pass.log")
    os.makedirs(os.path.dirname(logp), exist_ok=True)
    cmd = [sys.executable, os.path.abspath(__file__), "run"]
    if limit:
        cmd += ["--limit", str(limit)]
    creation = 0x08000000 | 0x00000008  # CREATE_NO_WINDOW | DETACHED
    with io.open(logp, "ab") as logf:
        p = subprocess.Popen(cmd, cwd=ROOT, stdout=logf, stderr=logf,
                             creationflags=creation, close_fds=True)
    st["last_spawn"] = now.isoformat(timespec="seconds")
    st["spawn_pid"] = p.pid
    st["spawn_log"] = logp
    write_status(st)
    print(f"spawned detached pass pid={p.pid} log={logp}")
    return 0


def status_print():
    st = load_status()
    universe = discover_universe()
    expected = base.expected_latest_bar_date(dt.datetime.now())
    work = pending_work(universe, expected, set(st.get("done", [])))
    out = {"universe": len(universe), "expected_cutoff": expected,
           "pending": len(work), "done_checkpoint": len(st.get("done", [])),
           "last_attempt": st.get("last_attempt"),
           "last_spawn": st.get("last_spawn"),
           "pass": st.get("pass")}
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


# ------------------------------------------------------------------- selftest


def _selftest():
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # U1 discovery: prefixes only, bare-vs-prefixed dedupe, suffix skip
        names = ["sh510300.csv", "510300.csv", "sz159915.csv", "sh588000.csv",
                 "sh600000.csv", "sz000001.csv", "sh510880_t73.csv",
                 "sh512880.csv", "sh511010.csv"]
        for n in names:
            base.atomic_write(os.path.join(td, n), ",".join(base.COLS) + "\n")
        uni = discover_universe(td)
        syms = [u["symbol"] for u in uni]
        assert syms == ["sh510300", "sh511010", "sh512880", "sh588000",
                        "sz159915"], syms
        assert "sh510880_t73" not in syms            # suffix specialist copy
        assert "sh600000" not in syms and "sz000001" not in syms  # stocks

        # U2 last_bar_date tail read + pending selection
        rows = [{"date": "2026-09-22", "open": 1.0, "high": 1.0, "low": 1.0,
                 "close": 1.0, "volume": 1.0, "amount": 1.0},
                {"date": "2026-10-20", "open": 1.0, "high": 1.0, "low": 1.0,
                 "close": 1.0, "volume": 1.0, "amount": 1.0}]
        p = os.path.join(td, "sh510300.csv")
        base.atomic_write(p, base.rows_to_csv_text(rows))
        assert last_bar_date(p) == "2026-10-20"
        assert last_bar_date(os.path.join(td, "sz159915.csv")) is None
        work = pending_work(uni, "2026-10-20")
        assert [w["symbol"] for w in work] == ["sh511010", "sh512880",
                                               "sh588000", "sz159915"]
        assert pending_work(uni, "2026-10-20",
                            done={"sh511010", "sh512880", "sh588000",
                                  "sz159915"}) == []

        # U3 merge honesty is inherited from the five-member leg (one assert
        # pins that this leg really calls it, not a copy)
        local = [{"date": "2026-09-22", "open": 1.0, "high": 1.0, "low": 1.0,
                  "close": 1.0, "volume": 10.0, "amount": 10.0}]
        bad = [dict(local[0], close=2.0)]
        assert base.merge_incremental(local, bad)["merged"] is False
        assert base.merge_incremental(local, local)["appended"] == 0

    # U4 lane guard + status native types
    assert LANE_OWNER == "bm-b"
    assert json.loads(json.dumps({"pid": int(3)}))["pid"] == 3
    print("selftest: 4/4 PASS")
    return 0


def main(argv):
    a = argv[1:]
    if not a:
        return run_pass()
    cmd = a[0]
    if cmd == "selftest":
        return _selftest()
    if cmd == "status":
        return status_print()
    if cmd == "refresh":
        limit = a[a.index("--limit") + 1] if "--limit" in a else None
        return spawn_detached(limit)
    if cmd == "run":
        limit = a[a.index("--limit") + 1] if "--limit" in a else None
        maxs = a[a.index("--max-seconds") + 1] if "--max-seconds" in a else None
        return run_pass(limit=limit, max_seconds=maxs)
    print(f"unknown subcommand: {cmd}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))