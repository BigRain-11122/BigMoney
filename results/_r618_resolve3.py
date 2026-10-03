"""r618 bm-b resolver leg 3: pull --no-rebase merge conflicts vs origin
(bm-c r625 close). Stage2=ours(local bm-b), stage3=theirs(origin).
Recipes per SKILL.md: jsonl union (marker-filtered); rolling-ledger union +
take-new state; snapshots take-new by ts (tie->ours r140); md twins mirror
json side. Parse-verify before write (r185)."""
import json
import subprocess
import sys

LEDGER = ["results/compute_audit.json", "results/regime_state.json"]
JSONL = ["results/x2_watch_log.jsonl"]
MD_TWINS = {
    "docs/daily_report/REPORT-2026-10-03.md": "docs/daily_report/REPORT-2026-10-03.json",
    "docs/live_usage/LIVE-2026-10-03.md": "docs/live_usage/LIVE-2026-10-03.json",
    "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
}
TS_KEYS = ["updated", "now", "generated", "generated_at", "written_at",
           "ts", "asof", "updated_at"]


def stage(n, p):
    r = subprocess.run(["git", "show", ":%s:%s" % (n, p)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def unmerged():
    r = subprocess.run(["git", "diff", "--name-only", "--diff-filter=U"],
                      capture_output=True, text=True)
    return [l for l in r.stdout.splitlines() if l.strip()]


def find_ts(b):
    try:
        d = json.loads(b)
    except Exception:
        return None
    for k in TS_KEYS:
        v = d.get(k)
        if isinstance(v, str) and len(v) >= 8:
            return v
    return None


def take_new(p):
    o, t = stage(2, p), stage(3, p)
    to, tt = find_ts(o), find_ts(t)
    if tt is not None and (to is None or tt > to):
        b, side = t, "theirs"
    else:
        b, side = o, "ours"
    json.loads(b)
    open(p, "wb").write(b)
    return {"recipe": "snapshot take-new", "side": side,
            "ours_ts": to, "theirs_ts": tt}


def union_jsonl(p):
    seen, out = set(), []
    for n in (2, 3):
        b = stage(n, p)
        if not b:
            continue
        for raw in b.splitlines():
            ln = raw.rstrip(b"\r\n")
            if ln.startswith((b"<<<<<<<", b"=======", b">>>>>>>")):
                continue
            if ln and ln not in seen:
                seen.add(ln)
                out.append(ln)
    b = b"\n".join(out) + b"\n"
    open(p, "wb").write(b)
    return {"recipe": "append-log line-union", "lines": len(out)}


def ledger(p):
    o, t = json.loads(stage(2, p)), json.loads(stage(3, p))
    merged = dict(o)
    for key, idk in (("history", "ts"), ("launches", "ts"),
                     ("transitions", "asof")):
        if key in o or key in t:
            by = {}
            for e in (o.get(key) or []) + (t.get(key) or []):
                k = e.get(idk)
                if k not in by:
                    by[k] = e
            merged[key] = [by[k] for k in sorted(by)]
    to, tt = find_ts_bytes = (find_ts(stage(2, p)), find_ts(stage(3, p)))
    if tt and (to is None or tt > to):
        for k, v in t.items():
            if k not in ("history", "launches", "transitions"):
                merged[k] = v
    h = merged.get("history")
    if h:
        merged["latest"] = max(h, key=lambda e: e.get("ts", ""))
    b = json.dumps(merged, ensure_ascii=False, indent=1).encode("utf-8") + b"\n"
    json.loads(b)
    open(p, "wb").write(b)
    return {"recipe": "ledger-union n=%d" % len(h or [])}


def main():
    files = unmerged()
    report = {}
    for p in files:
        if p in JSONL:
            report[p] = union_jsonl(p)
        elif p in LEDGER:
            report[p] = ledger(p)
        elif p in MD_TWINS:
            continue  # handled after json twins
        else:
            report[p] = take_new(p)
    for p, twin in MD_TWINS.items():
        if p in files:
            side = report[twin]["side"]
            n = 3 if side == "theirs" else 2
            b = stage(n, p)
            if b"<<<<<<<" in b or b">>>>>>>" in b:
                raise RuntimeError("marker in md %s" % p)
            open(p, "wb").write(b)
            report[p] = {"recipe": "md twin mirror", "side": side}
    with open("results/_r618_resolve_report.json", "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=1)
    print("resolved %d" % len(report))
    for k in sorted(report):
        print(" ", k, report[k].get("side", report[k]["recipe"]))


if __name__ == "__main__":
    sys.exit(main())
