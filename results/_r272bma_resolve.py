# -*- coding: utf-8 -*-
"""R272 bm-a rebase conflict resolver (bm-b r275 same-window S6 re-derive collision).

Classes per classify_conflicts.py + manual adjudication of 4 UNKNOWN
(daily_report pair + scorecard pair = deterministic per-round re-derive snapshots,
take-new by embedded generated ts; md/json twin pair taken from SAME side, r265 law).

Rebase orientation: stage2 (ours) = origin/main side (bm-b r275),
stage3 (theirs) = local r272 replay side. Tie -> ours (r140).
Bytes discipline: git show via subprocess capture (no PS redirect, r209 law).
"""
import json
import re
import subprocess
import sys

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"


def stage(path, n):
    r = subprocess.run(["git", "-C", ROOT, "show", ":%d:%s" % (n, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("stage %d missing for %s" % (n, path))
    return r.stdout


def parse(raw):
    return json.loads(raw.decode("utf-8-sig"))


TS_KEYS = ("generated", "ts", "updated_at", "generated_at", "asof", "updated")


def probe_ts(obj, depth=0):
    """Recursively find the newest ISO ts among ts-like keys (two levels, r267 law)."""
    best = ""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, str) and re.match(r"2026-09-\d\d[ T]\d\d:\d\d", v):
                if k in TS_KEYS or depth == 0:
                    best = max(best, v)
            sub = probe_ts(v, depth + 1)
            best = max(best, sub)
    elif isinstance(obj, list):
        for v in obj[:50]:
            best = max(best, probe_ts(v, depth + 1))
    return best


def take_new(path, ours_raw, theirs_raw):
    """Snapshot: parse both, compare embedded ts, take newer (tie -> ours)."""
    o, t = parse(ours_raw), parse(theirs_raw)
    ot, tt = probe_ts(o), probe_ts(t)
    win = "ours" if ot >= tt else "theirs"
    blob = ours_raw if win == "ours" else theirs_raw
    with open(path, "wb") as f:
        f.write(blob)
    print("  [snapshot] %s: ours_ts=%s theirs_ts=%s -> %s" % (path, ot, tt, win))
    return win


def union_rows(a, b):
    """Union list-of-dicts by full-row json identity, order-stable."""
    seen, out = set(), []
    for row in a + b:
        key = json.dumps(row, ensure_ascii=False, sort_keys=True)
        if key not in seen:
            seen.add(key)
            out.append(row)
    return out


def resolve_ledger(path, ours_raw, theirs_raw, ledger_keys, scalar_from):
    """rolling-ledger: union history rows zero-loss; scalar state take-new by ts."""
    o, t = parse(ours_raw), parse(theirs_raw)
    ot, tt = probe_ts(o), probe_ts(t)
    newer, older = (o, t) if ot >= tt else (t, o)
    for k in ledger_keys:
        if k in o or k in t:
            u = union_rows(o.get(k, []), t.get(k, []))
            newer[k] = u
            print("  [ledger] %s.%s: %d|%d -> union %d" %
                  (path, k, len(o.get(k, [])), len(t.get(k, [])), len(u)))
    txt = json.dumps(newer, ensure_ascii=False, indent=1)
    eol = "\r\n" if b"\r\n" in (ours_raw[:2000] or theirs_raw[:2000]) else "\n"
    tail = "\n" if ((ours_raw or theirs_raw).rstrip(b"\r\n") !=
                    (ours_raw or theirs_raw)) else ""
    with open(path, "wb") as f:
        f.write(txt.replace("\n", eol).encode("utf-8") +
                (eol.encode("utf-8") if tail else b""))
    print("  [ledger-state] %s: state from ts=%s side" % (path, max(ot, tt)))


def resolve_autofill(path, ours_raw, theirs_raw):
    o, t = parse(ours_raw), parse(theirs_raw)
    lo, lt = o.get("launches", []), t.get("launches", [])
    uni = union_rows(lo, lt)
    uni.sort(key=lambda r: r.get("ts", ""))          # asc, producer append order
    if len(uni) > 50:                                # rolling cap keeps newest 50
        uni = uni[-50:]
    ot = (o.get("last_tick") or {}).get("ts", "")
    tt = (t.get("last_tick") or {}).get("ts", "")
    last_tick = o.get("last_tick") if ot >= tt else t.get("last_tick")
    assert isinstance(last_tick, dict), "last_tick not dict"
    merged = dict(t)
    merged.update(o)
    merged["launches"] = uni
    merged["last_tick"] = last_tick
    txt = json.dumps(merged, ensure_ascii=False, indent=1)
    eol = "\r\n" if b"\r\n" in ours_raw[:2000] else "\n"
    with open(path, "wb") as f:
        f.write(txt.replace("\n", eol).encode("utf-8"))
    print("  [autofill] launches %d|%d -> union %d (cap50); last_tick ts=%s" %
          (len(lo), len(lt), len(uni), max(ot, tt)))


def resolve_js(path, ours_raw, theirs_raw):
    """js-wrapper-snapshot: take-side WHOLE bytes by embedded ts (R209: no re-emit)."""
    ot = probe_ts(parse(re.sub(rb"^[^{]*", b"", ours_raw, count=1).rstrip(b"; \r\n")))
    tt = probe_ts(parse(re.sub(rb"^[^{]*", b"", theirs_raw, count=1).rstrip(b"; \r\n")))
    win = "ours" if ot >= tt else "theirs"
    blob = ours_raw if win == "ours" else theirs_raw
    with open(path, "wb") as f:
        f.write(blob)
    print("  [js-wrapper] %s: %s vs %s -> %s" % (path, ot, tt, win))


def resolve_report_pair(jpath, mpath, jo, jm, to, tm):
    """daily_report md/json twins: json governs; BOTH files from the SAME side (r265)."""
    jot, jtt = probe_ts(parse(jo)), probe_ts(parse(to))
    win = "ours" if jot >= jtt else "theirs"
    with open(jpath, "wb") as f:
        f.write(jo if win == "ours" else to)
    with open(mpath, "wb") as f:
        f.write(jm if win == "ours" else tm)
    print("  [report-pair] json ts %s vs %s -> %s (md same side)" % (jot, jtt, win))


FILES = {
    "results/autofill_state.json": "autofill",
    "results/compute_audit.json": "ledger",
    "results/regime_state.json": "ledger",
    "results/dashboard_status.js": "js",
    "results/dashboard_status.json": "snap",
    "results/fundamental_b_layer_filter.json": "snap",
    "results/futures_update_status.json": "snap",
    "results/heat_update_status.json": "snap",
    "results/lhb_update_status.json": "snap",
    "results/token_usage.json": "snap",
    "results/update_status.json": "snap",
    "results/scorecard_v1.json": "snap",
    "results/strategy_scorecard.json": "snap",
}


def main():
    ok = True
    for path, cls in sorted(FILES.items()):
        ours_raw, theirs_raw = stage(path, 2), stage(path, 3)
        if cls == "autofill":
            resolve_autofill(path, ours_raw, theirs_raw)
        elif cls == "ledger":
            keys = ["history"] if "compute_audit" in path else ["transitions", "history"]
            resolve_ledger(path, ours_raw, theirs_raw, keys, None)
        elif cls == "js":
            resolve_js(path, ours_raw, theirs_raw)
        else:
            take_new(path, ours_raw, theirs_raw)
        # parse-validate after write-back (r185 law)
        if not path.endswith(".js"):
            try:
                json.load(open(path, encoding="utf-8-sig"))
            except Exception as e:
                ok = False
                print("  PARSE FAIL", path, e)
        else:
            m = re.match(rb"^window\.DASH_DATA = \{.*\};\s*$",
                         open(path, "rb").read().replace(b"\r\n", b"\n"),
                         re.S)
            if not m:
                ok = False
                print("  JS WRAPPER FAIL", path)
    resolve_report_pair("docs/daily_report/REPORT-2026-09-26.json",
                        "docs/daily_report/REPORT-2026-09-26.md",
                        stage("docs/daily_report/REPORT-2026-09-26.json", 2),
                        stage("docs/daily_report/REPORT-2026-09-26.md", 2),
                        stage("docs/daily_report/REPORT-2026-09-26.json", 3),
                        stage("docs/daily_report/REPORT-2026-09-26.md", 3))
    print("ALL RESOLVED" if ok else "FAILURES PRESENT")
    return 0 if ok else 2


if __name__ == "__main__":
    sys.exit(main())
