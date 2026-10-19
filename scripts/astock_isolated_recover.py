"""Astocks daily panel -- isolated-symbol recovery leg (bm-b lane).

Why: update_astock_daily.py isolates a symbol after QUARANTINE_AT consecutive
fetch failures (attempts counter in data/astock_daily/_progress.json). A chunk
of those isolation events is transient (source hiccup, decoder glitch); the
panel then stays "incomplete" forever because a quarantined symbol is excluded
from todo and can never clear its own counter.

This leg re-probes every isolated symbol ONCE per run through the same
fetch/validate/merge primitives imported from update_astock_daily (zero
re-implementation -- single source of truth):
  - fetch success -> write/append the per-symbol csv, pop the attempts entry
  - fetch failure -> keep the counter, record the honest error string

It never writes the gate-owned status face: the next gate cycle re-derives
completeness from disk bytes. Zero network when nothing is isolated.

Usage:
    python scripts/astock_isolated_recover.py            # run
    python scripts/astock_isolated_recover.py selftest   # offline guards

Exit codes: 0 = nothing isolated / all recovered, 1 = partial (some still
fail -- honest, nothing rewritten for those), 2 = mechanism error.
"""
from __future__ import annotations

import datetime as dt
import importlib.util
import io
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHARED = os.path.join(ROOT, "scripts", "update_astock_daily.py")
RECEIPT = os.path.join(ROOT, "results", "_r1044bmb_astock_recover.json")
SLEEP_S = 2.5


def _load_shared():
    spec = importlib.util.spec_from_file_location("update_astock_daily", SHARED)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def isolated_codes(prog, quarantine_at):
    out = []
    for code, n in sorted((prog.get("attempts") or {}).items()):
        try:
            if int(n) >= int(quarantine_at):
                out.append((code, int(n)))
        except Exception:
            continue
    return out


def recover(mod, prog, picks):
    """Probe each isolated symbol once. Returns (recovered, failed) lists."""
    recovered, failed = [], []
    for code, attempts in picks:
        try:
            rows = mod.fetch_one(code, mod.market_of(code))
            rows, _dropped = mod.completeness_filter(rows)
            err = mod.validate_rows(rows)
            if err:
                raise RuntimeError("validation_fail:%s" % err)
            path = os.path.join(mod.PER_DIR, code + ".csv")
            local = mod.read_local_csv(path)
            res = mod.merge_incremental(local, rows)
            if not res["merged"]:
                # qfq corporate-action rewrite: full re-pull + atomic replace
                full = mod.fetch_one(code, mod.market_of(code))
                full, _ = mod.completeness_filter(full)
                err2 = mod.validate_rows(full)
                if err2:
                    raise RuntimeError("readjust_validation_fail:%s" % err2)
                mod.atomic_write(path, mod.rows_to_csv_text(full))
                last = str(full[-1][mod.DATE_KEY]) if full else None
                readjusted = True
            else:
                mod.atomic_write(path, mod.rows_to_csv_text(res["merged_rows"]))
                last = (str(res["merged_rows"][-1][mod.DATE_KEY])
                        if res["merged_rows"] else None)
                readjusted = False
            prog["attempts"].pop(code, None)
            recovered.append({"code": code, "attempts_before": attempts,
                              "rows": len(res.get("merged_rows") or rows),
                              "tail": last, "readjusted": readjusted})
        except Exception as e:
            failed.append({"code": code, "attempts_before": attempts,
                           "error": "%s: %s" % (type(e).__name__, str(e)[:140])})
        time.sleep(SLEEP_S)
    return recovered, failed


def run():
    mod = _load_shared()
    if not os.path.isdir(mod.PER_DIR):
        print("panel dir missing: %s (honest exit 2)" % mod.PER_DIR)
        return 2
    prog = mod.load_progress()
    picks = isolated_codes(prog, mod.QUARANTINE_AT)
    if not picks:
        print("no isolated symbols -> zero network no-op")
        return 0
    print("isolated=%d -> probing once each" % len(picks))
    recovered, failed = recover(mod, prog, picks)
    mod.save_progress(prog)
    per_files = len([p for p in os.listdir(mod.PER_DIR) if p.endswith(".csv")])
    receipt = {
        "probe": "astock_daily isolated-symbol recovery",
        "ts": dt.datetime.now().isoformat(timespec="seconds"),
        "machine": "bm-b",
        "lane": "T-2026-09-26-87-bm-b-astock-daily-collector",
        "isolated_n": len(picks),
        "recovered_n": len(recovered),
        "failed_n": len(failed),
        "recovered": recovered,
        "failed": failed,
        "per_files_after": per_files,
    }
    os.makedirs(os.path.dirname(RECEIPT), exist_ok=True)
    with io.open(RECEIPT, "w", encoding="utf-8") as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2)
    print("recovered=%d failed=%d per_files=%d receipt=%s"
          % (len(recovered), len(failed), per_files,
             os.path.relpath(RECEIPT, ROOT)))
    for r in failed:
        print("  still-isolated %s %s" % (r["code"], r["error"]))
    return 0 if not failed else 1


def selftest():
    checks = []

    prog = {"attempts": {"000001": 3, "600000": 1, "688089": 5}}
    got = isolated_codes(prog, 3)
    checks.append(("isolated picks counter>=3", got == [("000001", 3), ("688089", 5)]))

    checks.append(("no isolated -> empty picks", isolated_codes({"attempts": {}}, 3) == []))
    checks.append(("missing attempts key tolerated",
                   isolated_codes({}, 3) == []))

    prog2 = {"attempts": {"000001": 3}}
    mod = type("M", (), {})()
    # failure path must KEEP the counter (honest isolation stays isolated)
    def boom(*a, **k):
        raise RuntimeError("network_down")
    mod.fetch_one = boom
    mod.market_of = lambda c: "sz"
    mod.PER_DIR = os.path.join(ROOT, "results", "_selftest_tmp_per")
    os.makedirs(mod.PER_DIR, exist_ok=True)
    mod.QUARANTINE_AT = 3
    rec, fail = recover(mod, prog2, isolated_codes(prog2, 3))
    checks.append(("failure keeps attempts", prog2["attempts"].get("000001") == 3))
    checks.append(("failure recorded", len(fail) == 1 and not rec))
    try:
        os.rmdir(mod.PER_DIR)
    except OSError:
        pass

    ok = True
    for name, passed in checks:
        print("  [%s] %s" % ("PASS" if passed else "FAIL", name))
        ok = ok and passed
    print("selftest: %d/%d %s" % (sum(1 for _, p in checks if p), len(checks),
                                  "PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv):
    cmd = argv[1] if len(argv) > 1 else "run"
    if cmd == "selftest":
        return selftest()
    if cmd in ("run", "recover"):
        return run()
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))