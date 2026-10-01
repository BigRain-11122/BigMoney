"""r510 bm-b rebase resolver: S6 storm faces, ts-newer-wins + ledger unions.

Replay: eb7faf07a (r509 closeout) onto 2d28710cf (bm-a r522 closeout).
Stage sides: :2: = ours = origin/main (bm-a r522), :3: = theirs = bm-b r509.

Laws: r294 (union domain), r500 (parse bytes never raw-str), r100/R350
(normalized ts-key match, ^20\\d{2}- value gate, wall-clock pool preferred,
no key-exclude lists), R209 (js twin follows json side), r98/r99/r100 (docs
twins same side), r185 (json.loads gate before write), r188/R208 (ledger
union zero loss), R93 (paper_export has no 'generated' -> state_updated).

Usage: python results/_r510bmb_rebase_resolver.py inspect|resolve
"""
import json
import re
import subprocess
import sys

DOCS_REPORT = [
    "docs/daily_report/REPORT-2026-10-01.json",
    "docs/daily_report/REPORT-2026-10-01.md",
]
DOCS_LIVE = [
    "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
]
SNAPSHOTS = [
    "results/_attrition_guard_scan.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/COMPOSITE-CE-01_paper.json",
    "results/paper/COMPOSITE-CE-02_paper.json",
    "results/paper/DROUGHT-CE-01_paper.json",
    "results/paper/ENGULF-CE-01_paper.json",
    "results/paper/NEEDLE-DE-01_paper.json",
    "results/paper/VOLATILITY-CE-01_paper.json",
    "results/paper_export/export-2026-09-30.json",
    "results/paper_export/latest.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/update_status.json",
]
ROLLING = [
    "results/compute_audit.json",
    "results/regime_state.json",
]
APPENDLOG = [
    "results/x2_watch_log.jsonl",
]
TWINS = {  # twin -> primary (twin follows primary side)
    "docs/daily_report/REPORT-2026-10-01.md":
        "docs/daily_report/REPORT-2026-10-01.json",
    "docs/live_usage/LIVE-2026-10-01.md":
        "docs/live_usage/LIVE-2026-10-01.json",
    "docs/live_usage/LIVE-latest.md":
        "docs/live_usage/LIVE-latest.json",
    "results/dashboard_status.js": "results/dashboard_status.json",
}

TS_KEYS = ("ts", "generated", "updated", "asof", "written", "epoch",
           "scanned", "checked", "stateupdated", "time")


def norm(k):
    return str(k).lower().replace("_", "").replace("-", "").replace(" ", "")


def val_ok(s):
    if re.match(r"^20\d{2}-", s):
        return True
    if s.isdigit() and len(s) in (10, 13):
        return True
    return False


def has_tod(s):
    return bool(re.search(r"[T ]\d{2}:\d{2}", s))


def probe(blob):
    """Deep-parse for newest ts-ish scalar. Returns (best_str, pool) or None."""
    cands = []

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                nk = norm(k)
                if any(t in nk for t in TS_KEYS) \
                        and isinstance(v, (str, int, float)):
                    s = str(v)
                    if val_ok(s):
                        cands.append(s)
                elif isinstance(v, (dict, list)):
                    walk(v)
        elif isinstance(o, list):
            for it in o:
                walk(it)

    try:
        walk(json.loads(blob.decode("utf-8", errors="replace")))
    except Exception:
        # non-json fallback: line scan (twins normally follow primary)
        for line in blob.decode("utf-8", errors="replace").splitlines()[:40]:
            for t in TS_KEYS:
                i = norm(line).find(t)
                if i >= 0:
                    seg = line[i:i + 48].strip("\"' ,}")
                    s = seg.split(":", 1)[-1].strip(" \"'}")
                    if val_ok(s) and (len(s) >= 10):
                        cands.append(s)
    if not cands:
        return None
    wall = [c for c in cands if has_tod(c)]
    if wall:
        return max(wall), "wallclock"
    dateonly = [c for c in cands if not c.isdigit()]
    if dateonly:
        return max(dateonly), "dateonly"
    return max(cands, key=lambda x: (len(x), x)), "epoch"


def stage(path, n):
    return subprocess.check_output(["git", "show", f":{n}:{path}"])


def side_pick(path):
    """Return (pick2_bool, why). pick2=True -> origin side."""
    pa, pb = probe(stage(path, 2)), probe(stage(path, 3))
    if pa is None and pb is None:
        return False, "no-ts-both->theirs(r509)"
    if pb is None:
        return True, f"theirs-no-ts origin={pa[0]}"
    if pa is None:
        return False, f"origin-no-ts theirs={pb[0]}"
    a, b = pa[0], pb[0]
    if a.isdigit() and b.isdigit():
        ai, bi = int(a), int(b)
        return (ai >= bi, f"epoch {a} vs {b}")
    if b >= a:
        return False, f"theirs {b} >= origin {a} [{pb[1]}]"
    return True, f"origin {a} > theirs {b} [{pa[1]}]"


def write_bytes(path, blob):
    with open(path, "wb") as fh:
        fh.write(blob)


def ledger_shape(path):
    """Report top-level keys + list-shaped keys with counts, both sides."""
    out = {}
    for n in (2, 3):
        try:
            obj = json.loads(stage(path, n).decode("utf-8"))
        except Exception as e:
            out[n] = f"parse-fail {e}"
            continue
        info = {}
        for k, v in obj.items():
            if isinstance(v, list):
                info[k] = f"list[{len(v)}]" + (
                    f" entrykeys={sorted(v[-1].keys())[:6] if v and isinstance(v[-1], dict) else 'n/a'}")
            elif isinstance(v, dict):
                info[k] = f"dict[{len(v)}]"
            else:
                info[k] = repr(v)[:60]
        out[n] = info
    return out


def union_ledger(path, ledger_keys):
    """Union list entries by canonical form; snapshot fields take-new side."""
    a = json.loads(stage(path, 2).decode("utf-8"))
    b = json.loads(stage(path, 3).decode("utf-8"))
    pick2, why = side_pick(path)
    winner = a if pick2 else b
    out = dict(winner)
    details = {}
    for k in ledger_keys:
        la = a.get(k, [])
        lb = b.get(k, [])
        seen = {}
        for e in la + lb:
            seen[json.dumps(e, sort_keys=True, ensure_ascii=False)] = e
        merged = list(seen.values())
        # chronological re-sort if entries carry a probeable ts
        def ets(e):
            p = probe(json.dumps(e, ensure_ascii=False).encode())
            return p[0] if p else ""
        try:
            merged.sort(key=ets)
        except Exception:
            pass
        out[k] = merged
        details[k] = f"{len(la)}|{len(lb)}->{len(merged)}"
    return out, pick2, why, details


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "inspect"
    report = {}

    if mode == "inspect":
        for f in DOCS_REPORT + DOCS_LIVE + SNAPSHOTS:
            pick2, why = side_pick(f)
            report[f] = ("origin" if pick2 else "theirs") + f" ({why})"
        for f in ROLLING:
            report[f + "#shape2"] = ledger_shape(f)[2]
            report[f + "#shape3"] = ledger_shape(f)[3]
        for f in APPENDLOG:
            a = stage(f, 2).decode("utf-8").splitlines()
            b = stage(f, 3).decode("utf-8").splitlines()
            report[f] = f"origin lines={len(a)} theirs lines={len(b)} " \
                        f"union~{len(set(a) | set(b))}"
        print(json.dumps(report, ensure_ascii=False, indent=1, default=str))
        return 0

    # ---- resolve mode ----
    # docs families: all files in a family take the same side (probe jsons,
    # family winner = newest probe across the family's json probes)
    for fam in (DOCS_REPORT, DOCS_LIVE):
        jsons = [f for f in fam if f.endswith(".json")]
        probes = {}
        for f in jsons:
            p = probe(stage(f, 2)), probe(stage(f, 3))
            probes[f] = p
        # family side: any file where origin newer -> origin; else theirs
        origin_newer = False
        for f, (pa, pb) in probes.items():
            if pb is None or (pa is not None and pb[0] < pa[0]):
                origin_newer = True
        fam_side = 2 if origin_newer else 3
        for f in fam:
            write_bytes(f, stage(f, fam_side))
            report[f] = f"family-take {'origin' if fam_side == 2 else 'theirs'}"

    # snapshots: per-file take-new
    for f in SNAPSHOTS:
        if f in TWINS:
            continue
        pick2, why = side_pick(f)
        write_bytes(f, stage(f, 2 if pick2 else 3))
        report[f] = f"pick {'origin' if pick2 else 'theirs'} ({why})"

    # rolling ledgers: union + take-new state
    # ledger keys resolved after inspect (see shapes): compute_audit=history,
    # regime_state=history/transitions
    for f, keys in (("results/compute_audit.json", ["history"]),
                    ("results/regime_state.json", ["history", "transitions"])):
        merged, pick2, why, det = union_ledger(f, keys)
        base = stage(f, 2 if pick2 else 3)
        # mirror base blob formatting: indent+CRLF probe (r509/r514 laws)
        m = re.search(rb"\n( +)\"", base)
        indent = len(m.group(1)) if m else 2
        crlf = b"\r\n" in base
        txt = json.dumps(merged, ensure_ascii=False, indent=indent,
                         sort_keys=False) + ("\n" if True else "")
        data = txt.replace("\n", "\r\n").encode("utf-8") if crlf \
            else txt.encode("utf-8")
        with open(f, "wb") as fh:
            fh.write(data)
        report[f] = f"union {det} state={'origin' if pick2 else 'theirs'} ({why})"

    # append logs: line-level union zero loss
    for f in APPENDLOG:
        a = {ln for ln in stage(f, 2).decode("utf-8").splitlines() if ln}
        b = {ln for ln in stage(f, 3).decode("utf-8").splitlines() if ln}
        u = sorted(a | b)
        base = stage(f, 2).decode("utf-8", errors="replace")
        nl = "\r\n" if "\r\n" in base else "\n"
        with open(f, "wb") as fh:
            fh.write(nl.join(u).encode("utf-8") + nl.encode())
        report[f] = f"union {len(a)}|{len(b)}->{len(u)}"

    # twins follow primary
    for twin, primary in TWINS.items():
        pick2 = "pick origin" in report.get(primary, "") \
            or "family-take origin" in report.get(primary, "") \
            or "state=origin" in report.get(primary, "")
        write_bytes(twin, stage(twin, 2 if pick2 else 3))
        report[twin] = f"twin-follows-primary ({'origin' if pick2 else 'theirs'})"

    # r185: parse-gate every json written
    bad = []
    for f in DOCS_REPORT + DOCS_LIVE + SNAPSHOTS + ROLLING:
        if not f.endswith(".json"):
            continue
        try:
            json.loads(open(f, "rb").read().decode("utf-8"))
        except Exception as e:
            bad.append(f"{f}: {e}")
    if bad:
        print(json.dumps({"PARSE-GATE-FAIL": bad}, ensure_ascii=False, indent=1))
        return 1
    for f in APPENDLOG:
        for ln in open(f, "rb").read().decode("utf-8").splitlines():
            if ln:
                json.loads(ln)  # raises on bad line
    print(json.dumps(report, ensure_ascii=False, indent=1))
    subprocess.check_call(["git", "add"] + DOCS_REPORT + DOCS_LIVE +
                          SNAPSHOTS + ROLLING + APPENDLOG +
                          list(TWINS.keys()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
