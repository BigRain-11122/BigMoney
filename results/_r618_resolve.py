"""r618 bm-b rebase conflict resolver (skill bigmoney-conflict-resolve).

Rebase state: daemon pre-push pull --rebase replayed my commits onto
origin tip 4515c4e31 (bm-a r625 estate). Pick #1 (ed01917d2, dead r618
S6 outputs) conflicted on 31 shared derive faces; a prior add -A blunder
collapsed the UU stages with marker content. Both sides recoverable from
refs:
  ours   (HEAD/onto) = 4515c4e31   (bm-a r625 derives)
  theirs (pick)      = ed01917d2   (bm-b dead-session S6 derives)
Recipes per SKILL.md: jsonl=line-union; rolling-ledger faces=union
history + take-new state; snapshots=take-new whole side by embedded ts;
js-wrapper=take-side whole bytes (mirror json twin side); md twins mirror
their json twin. Parse-verify before add (r185). Tie/missing ts -> ours
(r140). All decisions logged to results/_r618_resolve_report.json.
"""
import json
import subprocess
import sys

OURS = "4515c4e31"
THEIRS = "ed01917d2"

JSONL_UNION = [
    "results/x2_watch_log.jsonl",
]
LEDGER_FACES = [  # union history/transitions + take-new state fields
    "results/compute_audit.json",
    "results/regime_state.json",
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
    "docs/daily_report/REPORT-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-latest.json",
]
JS_WRAPPER = ["results/dashboard_status.js"]
MD_TWINS = {
    "docs/daily_report/REPORT-2026-10-03.md": "docs/daily_report/REPORT-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md": "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}

TS_KEYS = ["updated", "now", "generated", "generated_at", "written_at",
           "ts", "asof", "updated_at"]


def show_bytes(ref, path):
    r = subprocess.run(["git", "show", "%s:%s" % (ref, path)],
                       capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git show %s:%s rc=%d %s" % (
            ref, path, r.returncode, r.stderr[:200]))
    return r.stdout


def find_ts(d):
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return v
    return None


def pick_side(ours_b, theirs_b, path):
    ours = json.loads(ours_b)
    theirs = json.loads(theirs_b)
    to, tt = find_ts(ours), find_ts(theirs)
    if to is None and tt is None:
        return ours_b, "ours(fallback no-ts r140)", to, tt
    if tt is None or (to is not None and to >= tt):
        return ours_b, "ours", to, tt
    return theirs_b, "theirs", to, tt


def union_lines(ours_b, theirs_b):
    out, seen = [], set()
    for raw in ours_b.splitlines(keepends=True) + theirs_b.splitlines(keepends=True):
        line = raw.rstrip(b"\r\n")
        if line in seen:
            continue
        seen.add(line)
        out.append(raw)
    return b"".join(out)


def resolve_ledger(path, ours_b, theirs_b):
    ours, theirs = json.loads(ours_b), json.loads(theirs_b)
    merged = dict(ours)  # start from ours (HEAD tie law)
    for key in ("history", "launches", "transitions"):
        if key in ours or key in theirs:
            a = ours.get(key) or []
            b = theirs.get(key) or []
            idk = "ts" if key != "transitions" else "asof"
            by = {}
            for e in a + b:
                k = e.get(idk)
                if k not in by:
                    by[k] = e
            merged[key] = [by[k] for k in sorted(by)]
    to, tt = find_ts(ours), find_ts(theirs)
    if tt and (to is None or tt > to):
        for k, v in theirs.items():
            if k not in ("history", "launches", "transitions"):
                merged[k] = v
    # latest pointer: newest history entry wins
    h = merged.get("history")
    if h:
        merged["latest"] = max(h, key=lambda e: e.get("ts", ""))
    return json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8") + b"\n", \
        "ledger-union n=%d" % len(h or [])


def main():
    report = {}
    for p in JSONL_UNION:
        o, t = show_bytes(OURS, p), show_bytes(THEIRS, p)
        u = union_lines(o, t)
        open(p, "wb").write(u)
        report[p] = {"recipe": "append-log line-union",
                     "lines": len(u.splitlines()),
                     "ours_lines": len(o.splitlines()),
                     "theirs_lines": len(t.splitlines())}
    for p in LEDGER_FACES:
        o, t = show_bytes(OURS, p), show_bytes(THEIRS, p)
        b, note = resolve_ledger(p, o, t)
        json.loads(b)  # parse-verify before write (r185)
        open(p, "wb").write(b)
        report[p] = {"recipe": note}
    for p in SNAPSHOTS:
        o, t = show_bytes(OURS, p), show_bytes(THEIRS, p)
        b, side, to, tt = pick_side(o, t, p)
        json.loads(b)  # parse-verify (r185)
        open(p, "wb").write(b)
        report[p] = {"recipe": "snapshot take-new", "side": side,
                     "ours_ts": to, "theirs_ts": tt}
    json_side = {}
    for p in SNAPSHOTS:
        if p.startswith("docs/"):
            b, side, to, tt = None, None, None, None
            rep = report[p]
            json_side[p] = rep["side"]
    for p in JS_WRAPPER:
        # mirror the dashboard_status.json twin side, whole bytes (R209)
        twin = report["results/dashboard_status.json"]["side"]
        src = OURS if twin.startswith("ours") else THEIRS
        b = show_bytes(src, p)
        if b"window.DASH_DATA" not in b:
            raise RuntimeError("js wrapper lost DASH_DATA: %s" % p)
        open(p, "wb").write(b)
        report[p] = {"recipe": "js-wrapper take-side bytes", "side": twin}
    for p, twin in MD_TWINS.items():
        side = json_side.get(twin) or report.get(twin, {}).get("side", "ours")
        src = OURS if side.startswith("ours") else THEIRS
        b = show_bytes(src, p)
        if b"<<<<<<<" in b or b">>>>>>>" in b:
            raise RuntimeError("marker leaked into resolved md: %s" % p)
        open(p, "wb").write(b)
        report[p] = {"recipe": "md twin mirror-json-side", "side": side}
    with open("results/_r618_resolve_report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("resolved %d faces" % (len(report)))
    for k in sorted(report):
        print(" ", k, "->", report[k].get("side", report[k]["recipe"]))


if __name__ == "__main__":
    sys.exit(main())
