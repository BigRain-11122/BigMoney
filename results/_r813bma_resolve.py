# -*- coding: utf-8 -*-
"""r813 bm-a takeover rebase-conflict resolver (29 UU, skill recipes).

bigmoney-conflict-resolve skill canon, stage orientation r351:
  :2: = origin/base side (bm-c r663 08:07), :3: = local/replay side
  (churn-absorb-3: dead-r813 S6 02-03 + r813-takeover scan 08:1x).
  same-second tie -> :2: origin (r140).

Faces resolved here (23): snapshot deep-ts take-new (r98/r99/r100/R350),
twin-regen-md same-side byte-copy (r327/r329), js-wrapper-snapshot
take-side whole bytes (R209), append-log line union (r188/r217).
ALL_FACES members (6) are NOT touched here -- they go through
  python scripts\\merge_lane_views.py resolve <path>  (r377/r376 canon).

Zero-loss assertions before write; parse-verify after write; fail-closed
rc2 on any face that cannot be adjudicated (no blind take-new).
"""
import json
import re
import subprocess
import sys

TS_RE = re.compile(r"^20\d{2}-\d{2}-\d{2}")
TOD_RE = re.compile(r"[T ]\d{2}:\d{2}")


def stage_bytes(stage, rel):
    """stage = '2'|'3' (bare digit; f-string adds the colons)."""
    r = subprocess.run(["git", "show", f":{stage}:{rel}"],
                       capture_output=True)
    return r.stdout if r.returncode == 0 else None


def deep_ts(blob):
    """R350 value-shape adjudication (no key lists): deep-collect every
    ts-shaped string that carries time-of-day, return the per-side max.
    Deterministic content (future dates, cutoffs) appears on BOTH sides
    so a shared max ties; only the generation-ts differs."""
    best = [None]

    def walk(o):
        if isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str) and TS_RE.match(o) and TOD_RE.search(o):
            if best[0] is None or o > best[0]:
                best[0] = o
    walk(json.loads(blob.decode("utf-8")))
    return best[0]


def take_new(rel):
    """snapshot recipe: whole-side byte-copy of the deep-ts winner."""
    o, l = stage_bytes("2", rel), stage_bytes("3", rel)
    if o is None or l is None:
        return ("FAIL", "stage read fail")
    try:
        ts_o, ts_l = deep_ts(o), deep_ts(l)
    except Exception as e:
        return ("FAIL", f"probe parse fail: {e}")
    if ts_o is None and ts_l is None:
        return ("FAIL", "no ts-shaped value with time-of-day on either side")
    if ts_l is not None and (ts_o is None or ts_l > ts_o):
        side, ts, tag = l, ts_l, ":3: local"
    elif ts_o is not None and (ts_l is None or ts_o > ts_l):
        side, ts, tag = o, ts_o, ":2: origin"
    else:
        side, ts, tag = o, ts_o, ":2: origin (tie r140)"
    with open(rel, "wb") as f:
        f.write(side)
    json.loads(open(rel, "rb").read().decode("utf-8"))  # parse-verify
    return ("OK", f"{tag} ts={ts}")


def twin(json_rel, md_rel):
    """twin-regen-md: probe the json side, byte-copy BOTH from same side."""
    o, l = stage_bytes("2", json_rel), stage_bytes("3", json_rel)
    if o is None or l is None:
        return ("FAIL", "json stage read fail")
    try:
        ts_o, ts_l = deep_ts(o), deep_ts(l)
    except Exception as e:
        return ("FAIL", f"probe parse fail: {e}")
    if ts_l is not None and (ts_o is None or ts_l > ts_o):
        stage, ts, tag = ":3:", ts_l, ":3: local"
    elif ts_o is not None and (ts_l is None or ts_o > ts_l):
        stage, ts, tag = ":2:", ts_o, ":2: origin"
    else:
        stage, ts, tag = ":2:", ts_o, ":2: origin (tie r140)"
    for rel in (json_rel, md_rel):
        side = stage_bytes(stage.strip(":"), rel)
        if side is None:
            return ("FAIL", f"twin stage read fail {rel}")
        with open(rel, "wb") as f:
            f.write(side)
    json.loads(open(json_rel, "rb").read().decode("utf-8"))
    return ("OK", f"both twins from {tag} ts={ts}")


def line_union(rel):
    """append-log recipe: line-level union, origin order first, zero loss."""
    o, l = stage_bytes("2", rel), stage_bytes("3", rel)
    if o is None or l is None:
        return ("FAIL", "stage read fail")
    o_lines = o.decode("utf-8").splitlines()
    seen = set(o_lines)
    l_lines = l.decode("utf-8").splitlines()
    out_lines = list(o_lines) + [x for x in l_lines if x not in seen]
    blob = ("\n".join(out_lines) + "\n").encode("utf-8")
    back = blob.decode("utf-8").splitlines()
    assert all(x in back for x in o_lines), "origin line lost"
    assert all(x in back for x in l_lines), "local line lost"
    with open(rel, "wb") as f:
        f.write(blob)
    return ("OK", f"union |O|={len(o_lines)} |L|={len(l.splitlines())} "
            f"-> |merged|={len(back)}")


def main():
    verdicts = []
    snapshots = [
        "results/daily_scorecard.json",
        "results/fundamental_b_layer_filter.json",
        "results/paper/COMPOSITE-CE-01_paper.json",
        "results/paper/COMPOSITE-CE-02_paper.json",
        "results/paper/DROUGHT-CE-01_paper.json",
        "results/paper/ENGULF-CE-01_paper.json",
        "results/paper/NEEDLE-DE-01_paper.json",
        "results/paper/VOLATILITY-CE-01_paper.json",
        "results/prospect_paper/_summary.json",
        "results/prospect_promotion/_summary.json",
        "results/scorecard_v1.json",
        "results/strategy_scorecard.json",
        "results/t35_open_fill_verify.json",
        "results/_attrition_guard_scan.json",
    ]
    for rel in snapshots:
        st, msg = take_new(rel)
        verdicts.append((rel, st, msg))
    for j, m in [
        ("docs/daily_report/REPORT-2026-10-07.json",
         "docs/daily_report/REPORT-2026-10-07.md"),
        ("docs/live_usage/LIVE-2026-10-07.json",
         "docs/live_usage/LIVE-2026-10-07.md"),
        ("docs/live_usage/LIVE-latest.json",
         "docs/live_usage/LIVE-latest.md"),
        # producer twins: dashboard json + js wrapper, same side both (R209)
        ("results/dashboard_status.json", "results/dashboard_status.js"),
    ]:
        st, msg = twin(j, m)
        verdicts.append((j + " + " + m, st, msg))
    st, msg = line_union("results/x2_watch_log.jsonl")
    verdicts.append(("results/x2_watch_log.jsonl", st, msg))

    fails = [v for v in verdicts if v[1] != "OK"]
    for rel, st, msg in verdicts:
        print(f"[{st}] {rel} :: {msg}")
    print(f"resolver: {len(verdicts) - len(fails)}/{len(verdicts)} OK, "
          f"{len(fails)} FAIL")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
