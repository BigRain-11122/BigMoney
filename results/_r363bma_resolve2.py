# -*- coding: utf-8 -*-
"""r363 bm-a wave-2 rebase-storm resolver (second pull --rebase, final pick ade08dbb
onto d62f7d43, base 5c8e4542). New origin side (bm-b r347 S6 + bm-c r114/115 S6)
ran FRESHER (23:19-23:20) than my r362 faces (23:05-23:07) -> mirror of wave-1:
all snapshots/twins take-OURS; compute_audit = history ts-key union no-cap
(201+202 -> 204 expected) + state face take-OURS; autofill_state already
auto-merged correct (launches 47, last_tick ours 23:20:02) = not touched here.
CODELY.md + archive 202609.md NOT here (hand phase 2).
Sourcing = COMMIT BLOBS (tick-immune): ours=d62f7d43, mine=ade08dbb.
"""
import io
import json
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
OURS, MINE = "d62f7d43", "ade08dbb"


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300]}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def blob(rev, path):
    return git("show", f"{rev}:{path}", binary=True)


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
    io.open(path, "wb").write(data)


def take(rev, path, log, why):
    io.open(path, "wb").write(blob(rev, path))
    log.append(f"  {path}: take-{'OURS' if rev == OURS else 'MINE'} ({why})")


def main():
    log = []
    take(OURS, "docs/daily_report/REPORT-2026-09-27.json", log, "twin json probe ours 23:20:33 > mine 23:06:57")
    take(OURS, "docs/daily_report/REPORT-2026-09-27.md", log, "twin-coupled same-side OURS (r329)")
    take(OURS, "results/dashboard_status.json", log, "dash json probe ours 23:20:35 > mine 23:06:58")
    take(OURS, "results/dashboard_status.js", log, "dash pair same-side OURS whole-bytes wrapper (R209)")
    # regime_state: assert history/transitions identical then take fresher OURS whole
    ra = json.loads(blob(OURS, "results/regime_state.json").decode("utf-8"))
    rb = json.loads(blob(MINE, "results/regime_state.json").decode("utf-8"))
    assert ra.get("history") == rb.get("history"), "regime history diverged"
    assert ra.get("transitions") == rb.get("transitions"), "regime transitions diverged"
    take(OURS, "results/regime_state.json", log, "history/transitions identical, updated ours 23:19:33 > mine 23:05:55")
    # compute_audit: rolling union no-cap + state face OURS
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
        if t in merged and merged[t] != r:
            sa, sb = set(merged[t]), set(r)
            if sb >= sa:
                merged[t] = r
            elif not (sa >= sb):
                div.append(t)
        else:
            merged[t] = r
    assert not div, f"compute_audit same-ts true divergence: {div}"
    assert set(merged.keys()) == (ka | kb), "union key loss"
    rows = sorted(merged.values(), key=lambda r: r.get("ts", ""))
    out = dict(a)
    out["history"] = rows
    write_mirror("results/compute_audit.json", out, blob(OURS, "results/compute_audit.json"))
    log.append(f"  results/compute_audit.json: history union {len(ha)}+{len(hb)} -> {len(rows)} (distinct {len(ka | kb)}, no-cap zero-loss), state face OURS (23:19:18 > 23:05:35)")
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
        take(OURS, p, log, "snapshot deep-probe OURS fresher (23:19-20 vs 23:05-07)")
    verify = [
        "docs/daily_report/REPORT-2026-09-27.json",
        "docs/daily_report/REPORT-2026-09-27.md",
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
    print("PARSE-VERIFY 14/14 OK (marker-clean + json-valid + js-wrapper)")
    for l in log:
        print(l)
    git("add", "--", *verify)
    rem = [p for p in git("diff", "--name-only", "--diff-filter=U").strip().splitlines() if p]
    assert rem == ["CODELY.md", "research/memory-archive/202609.md"], f"unexpected UU set: {rem}"
    print("remaining UU (hand phase 2):", rem)
    return 0


if __name__ == "__main__":
    sys.exit(main())
