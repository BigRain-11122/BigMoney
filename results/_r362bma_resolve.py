# -*- coding: utf-8 -*-
"""r362 bm-a push-storm resolver (r360 pattern, adapted file set):
rebase stop 3 UU x17 vs origin f92993e5 (bm-b r347 + bm-c r113 window).
Side-assert r351: :2:=origin, :3:=mine. Handles the 15 S6-family files per
classifier recipes (r360 verbatim machinery); CODELY.md + archive 202609.md
resolved separately by hand (memory-union + batch-renumber), NOT here.
NO auto-push: continues rebase only after caller confirms no UU remains.
"""
import io
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TS_RE = re.compile(r"^20\d{2}-")
TOD_RE = re.compile(r"[T ]\d{2}:\d{2}")


def git(*args, binary=False):
    p = subprocess.run(["git"] + list(args), capture_output=True)
    if p.returncode != 0:
        raise RuntimeError(f"git {args[:3]} rc={p.returncode}: {p.stderr[:300]}")
    return p.stdout if binary else p.stdout.decode("utf-8", errors="replace")


def blob(rev, path):
    return git("show", f"{rev.rstrip(':')}:{path}", binary=True)


def wallocks(obj):
    out = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        elif isinstance(x, str) and TS_RE.match(x) and TOD_RE.search(x):
            out.append(x)
    walk(obj)
    return out


def load(b):
    return json.loads(b.decode("utf-8"))


def fmt_detect(b):
    crlf = b"\r\n" in b
    try:
        txt = b.decode("utf-8")
    except UnicodeDecodeError:
        return (crlf, 1, False)
    indent = 1
    for line in txt.splitlines():
        if line.startswith("  \"") or line.startswith("  {") or line.startswith("  ["):
            indent = 2
            break
        if line.startswith("   \""):
            indent = 3
            break
    non_ascii = any(ord(c) > 127 for c in txt)
    return (crlf, indent, not non_ascii)


def write_mirror(path, obj, origin_bytes):
    crlf, indent, asc = fmt_detect(origin_bytes)
    txt = json.dumps(obj, ensure_ascii=asc, indent=indent) + "\n"
    data = txt.encode("utf-8")
    if crlf:
        data = data.replace(b"\n", b"\r\n")
    io.open(path, "wb").write(data)


def take_side(path, rev):
    b = blob(rev, path)
    io.open(path, "wb").write(b)
    return rev


def probe_sides(path):
    a = load(blob(":2:", path))
    b = load(blob(":3:", path))
    wa, wb_ = max(wallocks(a)) if wallocks(a) else None, max(wallocks(b)) if wallocks(b) else None
    return a, b, wa, wb_


def resolve_snapshot(path, log):
    a, b_, wa, wb_ = probe_sides(path)
    if wa is None and wb_ is None:
        side, why = ":2:", "no-wallclock->HEAD"
    elif wb_ is None:
        side, why = ":2:", f"origin-only-wallclock({wa})"
    elif wa is None:
        side, why = ":3:", f"mine-only-wallclock({wb_})"
    elif wa > wb_:
        side, why = ":2:", f"origin={wa} > mine={wb_}"
    elif wb_ > wa:
        side, why = ":3:", f"mine={wb_} > origin={wa}"
    else:
        side, why = ":2:", f"tie({wa})->HEAD"
    take_side(path, side)
    log.append(f"  {path}: snapshot take-{'origin' if side==':2:' else 'MINE'} ({why})")


def resolve_compute_audit(path, log):
    a = load(blob(":2:", path))
    b_ = load(blob(":3:", path))
    ha, hb = a.get("history", []), b_.get("history", [])
    ka = {r.get("ts") for r in ha}
    kb = {r.get("ts") for r in hb}
    kall = ka | kb
    merged = {}
    for r in ha:
        merged[r.get("ts")] = r
    for r in hb:
        merged[r.get("ts")] = r
    assert set(merged.keys()) == kall, f"union lost keys: {kall - set(merged.keys())}"
    rows = sorted(merged.values(), key=lambda r: r.get("ts", ""))
    wa = max(wallocks(a)) if wallocks(a) else None
    wb_ = max(wallocks(b_)) if wallocks(b_) else None
    if wa is not None and (wb_ is None or wa >= wb_):
        out, took = dict(a), "origin"
    else:
        out, took = dict(b_), "mine"
    out["history"] = rows
    write_mirror(path, out, blob(":2:", path))
    log.append(f"  {path}: rolling union {len(ha)}+{len(hb)} -> {len(rows)} (distinct {len(kall)}, no-cap zero-loss), take-{took} (origin={wa} mine={wb_})")


def resolve_regime_state(path, log):
    a = load(blob(":2:", path))
    b_ = load(blob(":3:", path))
    ta, tb = a.get("transitions", []), b_.get("transitions", [])
    ka = {r.get("ts") for r in ta}
    kb = {r.get("ts") for r in tb}
    merged = {}
    for r in ta + tb:
        merged[r.get("ts")] = r
    assert set(merged.keys()) == (ka | kb), "regime union lost keys"
    rows = sorted(merged.values(), key=lambda r: r.get("ts", ""))
    wa = max(wallocks(a)) if wallocks(a) else None
    wb_ = max(wallocks(b_)) if wallocks(b_) else None
    if wa is not None and (wb_ is None or wa > wb_):
        base, why = a, f"origin={wa} newer"
    elif wb_ is not None and (wa is None or wb_ > wa):
        base, why = b_, f"mine={wb_} newer"
    else:
        base, why = a, f"tie/no-wallclock({wa},{wb_})->HEAD"
    out = dict(base)
    out["transitions"] = rows
    write_mirror(path, out, blob(":2:", path))
    log.append(f"  {path}: transitions union {len(ta)}+{len(tb)} -> {len(rows)} zero-loss, state {why}")


def resolve_autofill(path, log):
    a = load(blob(":2:", path))
    b_ = load(blob(":3:", path))
    la, lb = a.get("launches", []), b_.get("launches", [])
    comp = ("ts", "machine", "pid", "runner_sha256", "entry", "shard")
    seen = {}
    collisions = 0
    for r in la + lb:
        k = tuple(r.get(c) for c in comp)
        if k in seen:
            collisions += 1
            s, o = r, seen[k]
            if json.dumps(s, sort_keys=True) != json.dumps(o, sort_keys=True):
                merged = dict(o)
                merged.update({kk: vv for kk, vv in s.items()})
                seen[k] = merged
        else:
            seen[k] = r
    rows = sorted(seen.values(), key=lambda r: r.get("ts", ""), reverse=True)[:50]
    rows.sort(key=lambda r: r.get("ts", ""))  # asc write-back (r245)
    ta = a.get("last_tick", {})
    tb = b_.get("last_tick", {})
    tsa = ta.get("ts") if isinstance(ta, dict) else None
    tsb = tb.get("ts") if isinstance(tb, dict) else None
    if isinstance(tsa, str) and TS_RE.match(tsa) and isinstance(tsb, str) and TS_RE.match(tsb):
        last = ta if tsa >= tsb else tb
        why = f"origin={tsa} mine={tsb} -> {'origin' if last is ta else 'mine'}"
    else:
        last = ta
        why = "probe-miss->HEAD"
    out = dict(a)
    out.update({k: v for k, v in b_.items() if k not in ("launches", "last_tick")})
    out["launches"] = rows
    out["last_tick"] = last
    assert isinstance(out["last_tick"], dict), "last_tick not dict (r203 law)"
    write_mirror(path, out, blob(":2:", path))
    log.append(f"  {path}: launches union {len(la)}+{len(lb)} -> {len(rows)} (collisions {collisions}, cap50 asc), last_tick {why}")


def resolve_report_twins(log):
    jp, mp = "docs/daily_report/REPORT-202609-27.json", "docs/daily_report/REPORT-202609-27.md"
    a, b_, wa, wb_ = probe_sides(jp)
    if wa is not None and (wb_ is None or wa > wb_):
        side = ":2:"
    elif wb_ is not None and (wa is None or wb_ > wa):
        side = ":3:"
    else:
        side = ":2:"
    take_side(jp, side)
    take_side(mp, side)
    log.append(f"  {jp} + .md: twin take-{'origin' if side==':2:' else 'MINE'} SAME-SIDE (origin={wa} mine={wb_})")


def resolve_dash_pair(log):
    jp, js = "results/dashboard_status.json", "results/dashboard_status.js"
    a, b_, wa, wb_ = probe_sides(jp)
    if wa is not None and (wb_ is None or wa > wb_):
        side = ":2:"
    elif wb_ is not None and (wa is None or wb_ > wa):
        side = ":3:"
    else:
        side = ":2:"
    take_side(jp, side)
    take_side(js, side)
    log.append(f"  {jp} + .js: dash pair take-{'origin' if side==':2:' else 'MINE'} SAME-SIDE (origin={wa} mine={wb_})")


def main():
    log = []
    resolve_report_twins(log)
    resolve_dash_pair(log)
    resolve_autofill("results/autofill_state.json", log)
    resolve_compute_audit("results/compute_audit.json", log)
    resolve_regime_state("results/regime_state.json", log)
    snapshots = [
        "results/fundamental_b_layer_filter.json",
        "results/futures_update_status.json",
        "results/heat_update_status.json",
        "results/lhb_update_status.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/token_usage.json",
        "results/update_status.json",
    ]
    for p in snapshots:
        resolve_snapshot(p, log)
    verify = ["docs/daily_report/REPORT-202609-27.json",
              "results/autofill_state.json",
              "results/compute_audit.json",
              "results/regime_state.json",
              "results/dashboard_status.json",
              "results/dashboard_status.js"] + snapshots
    for p in verify:
        raw = io.open(p, "rb").read()
        if p.endswith(".js"):
            assert b"window.DASH_DATA" in raw and raw.rstrip().endswith(b"};"), f"js wrapper broken: {p}"
        else:
            json.loads(raw.decode("utf-8"))
    print("PARSE-VERIFY 15/15 OK")
    for l in log:
        print(l)
    add_files = verify + ["docs/daily_report/REPORT-202609-27.md"]
    git("add", "--", *add_files)
    rem = [p for p in git("diff", "--name-only", "--diff-filter=U").strip().splitlines() if p]
    print("remaining UU (expected CODELY+archive only):", rem)
    assert rem == ["CODELY.md", "research/memory-archive/202609.md"], f"unexpected UU set: {rem}"
    return 0


if __name__ == "__main__":
    sys.exit(main())
