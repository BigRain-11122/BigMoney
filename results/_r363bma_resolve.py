# -*- coding: utf-8 -*-
"""r363 bm-a rebase-storm resolver (final pick 9ddf5883 onto 5c8e4542, base 28d9249f):
17 UU vs origin f92993e5-chain (bm-b r347 + bm-c r113 same-window).
Sourcing = COMMIT BLOBS (tick-immune, r359 law): ours=5c8e4542, mine=9ddf5883.
Adjudication pre-read by results/_r363bma_probe.py:
  - 12 faces take-MINE (my S6 chain 23:05-23:07 fresher than origin 22:56-22:57)
  - REPORT twins + dashboard pair: same-side coupling -> MINE
  - autofill_state: launches 47=47 full-identical + last_tick tie 23:00:01 -> take OURS whole (r140 tie->HEAD)
  - compute_audit: history ts-key union 201+201->202 no-cap zero-loss, state face take-MINE (23:05:35>22:55:30)
  - regime_state: history/transitions both-sides identical -> take MINE whole (fresher updated 23:05:55)
CODELY.md + research/memory-archive/202609.md NOT here (hand resolution, memory-union + batch renumber).
NO auto-push: caller continues rebase after zero-UU confirmation.
"""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OURS, MINE = "5c8e4542", "9ddf5883"


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300]}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def blob(rev, path):
    return git("show", f"{rev}:{path}", binary=True)


def write_bytes(path, data):
    io.open(path, "wb").write(data)


def take(rev, path, log, why):
    write_bytes(path, blob(rev, path))
    log.append(f"  {path}: take-{'OURS' if rev == OURS else 'MINE'} ({why})")


def fmt_detect(b):
    crlf = b"\r\n" in b
    txt = b.decode("utf-8")
    indent = 1
    for line in txt.splitlines():
        if line.startswith('  "') or line.startswith("  {") or line.startswith("  ["):
            indent = 2
            break
        if line.startswith('   "'):
            indent = 3
            break
    non_ascii = any(ord(c) > 127 for c in txt)
    return crlf, indent, not non_ascii


def write_mirror(path, obj, mirror_bytes):
    crlf, indent, asc = fmt_detect(mirror_bytes)
    txt = json.dumps(obj, ensure_ascii=asc, indent=indent) + "\n"
    data = txt.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    write_bytes(path, data)


def main():
    log = []
    # 1) report twins same-side (json probe decided MINE 23:06:57 > 22:57:34)
    take(MINE, "docs/daily_report/REPORT-2026-09-27.json", log, "twin json probe 23:06:57>22:57:34")
    take(MINE, "docs/daily_report/REPORT-2026-09-27.md", log, "twin-coupled same-side MINE (r329)")
    # 2) dashboard pair same-side (json probe decided MINE 23:06:58 > 22:57:35)
    take(MINE, "results/dashboard_status.json", log, "dash json probe 23:06:58>22:57:35")
    take(MINE, "results/dashboard_status.js", log, "dash pair same-side MINE whole-bytes wrapper (R209)")
    # 3) autofill_state: identical overlap, tie->HEAD (r140)
    take(OURS, "results/autofill_state.json", log, "launches 47=47 identical + last_tick tie 23:00:01 -> HEAD/ours (r140)")
    # 4) regime_state: history/transitions identical both sides -> take MINE fresher updated
    take(MINE, "results/regime_state.json", log, "history 2+2 & transitions 0+0 identical, updated 23:05:55>22:56:02")
    # 5) compute_audit: rolling-ledger union no-cap + state take-MINE
    a = json.loads(blob(OURS, "results/compute_audit.json").decode("utf-8"))
    b = json.loads(blob(MINE, "results/compute_audit.json").decode("utf-8"))
    ha, hb = a.get("history", []), b.get("history", [])
    ka = {r.get("ts") for r in ha}
    kb = {r.get("ts") for r in hb}
    merged = {}
    div = []
    for r in ha:
        merged[r.get("ts")] = r
    for r in hb:
        t = r.get("ts")
        if t in merged:
            sa, sb = set(merged[t]), set(r)
            if merged[t] != r:
                if sb >= sa:
                    merged[t] = r  # mine field-superset of ours (r322)
                elif sa >= sb:
                    pass  # ours superset, keep ours
                else:
                    div.append(t)  # true divergence -> fail-closed
        else:
            merged[t] = r
    assert not div, f"compute_audit same-ts true-divergence rows, manual: {div}"
    assert set(merged.keys()) == (ka | kb), "union key loss"
    rows = sorted(merged.values(), key=lambda r: r.get("ts", ""))
    out = dict(b)  # state face take-MINE (23:05:35 fresher)
    out["history"] = rows
    write_mirror("results/compute_audit.json", out, blob(OURS, "results/compute_audit.json"))
    log.append(f"  results/compute_audit.json: history union {len(ha)}+{len(hb)} -> {len(rows)} (distinct {len(ka | kb)}, no-cap zero-loss r360-law), state face MINE (latest 23:05:35>22:55:30)")
    # 6) 8 snapshots take-MINE (probe: all 23:0x > 22:5x)
    for p in [
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/heat_update_status.json",
        "results/lhb_update_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]:
        take(MINE, p, log, "snapshot deep-probe MINE fresher")
    # parse-verify every resolved face (r185 law)
    verify = [
        "docs/daily_report/REPORT-2026-09-27.json",
        "docs/daily_report/REPORT-2026-09-27.md",
        "results/autofill_state.json",
        "results/compute_audit.json",
        "results/regime_state.json",
        "results/dashboard_status.json",
        "results/dashboard_status.js",
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/heat_update_status.json",
        "results/lhb_update_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in verify:
        raw = io.open(p, "rb").read()
        assert b"<<<<<<<" not in raw and b">>>>>>>" not in raw, f"markers left: {p}"
        if p.endswith(".js"):
            assert b"window.DASH_DATA" in raw and raw.rstrip().endswith(b"};"), f"js wrapper broken: {p}"
        elif p.endswith(".json"):
            json.loads(raw.decode("utf-8"))
    print("PARSE-VERIFY 15/15 OK (marker-clean + json-valid + js-wrapper)")
    for l in log:
        print(l)
    git("add", "--", *verify)
    rem = [p for p in git("diff", "--name-only", "--diff-filter=U").strip().splitlines() if p]
    assert rem == ["CODELY.md", "research/memory-archive/202609.md"], f"unexpected UU set: {rem}"
    print("remaining UU (hand phase):", rem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
