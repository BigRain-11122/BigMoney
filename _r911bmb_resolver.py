"""r911 S0 rebase 6-face resolver (r782/r747 family regen-face recipe).

Conflict set (commit 38fb32c9b vs origin bm-c r950):
  - fleet/machine-health.json        -> newer max(entry ts) wins (PS-written fleet face)
  - results/_attrition_guard_scan.json -> ts newer-wins (S7 scan re-derives anyway)
  - results/compute_audit.json       -> latest newer-wins; history union-by-ts keep 65 newest
  - results/regime_state.json        -> 'updated' newer-wins (S6 re-derives)
  - results/token_usage.json         -> 'generated' newer-wins (same machine keys both sides)
  - results/update_status.json       -> 'updated' newer-wins (S6 re-derives)
All six faces are deterministic re-derive faces of the S6/S7 chain; merge keeps
both machines' latest state without losing the incoming machine's rows.
"""
import json
import subprocess

TS_KEYS = {
    "results/_attrition_guard_scan.json": ["ts"],
    "results/regime_state.json": ["updated"],
    "results/token_usage.json": ["generated"],
    "results/update_status.json": ["updated"],
}
HIST_KEEP = 65


def show(stage, path):
    return subprocess.check_output(["git", "show", stage + path])


def ts_of(obj, keys):
    for k in keys:
        v = obj.get(k) if isinstance(obj, dict) else None
        if v:
            return v
    return ""


def write(path, obj):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
        f.write("\n")


def main():
    verdicts = []
    # scalar newer-wins faces
    for path, keys in TS_KEYS.items():
        ours = json.loads(show(":2:", path))
        theirs = json.loads(show(":3:", path))
        pick, side = (ours, "OURS") if ts_of(ours, keys) >= ts_of(theirs, keys) else (theirs, "THEIRS")
        write(path, pick)
        verdicts.append("%s -> %s (%s)" % (path, side, ts_of(pick, keys)))

    # machine-health: list face, newer max ts wins
    path = "fleet/machine-health.json"
    ours = json.loads(show(":2:", path))
    theirs = json.loads(show(":3:", path))
    o_ts = max(ts_of(e, ["ts"]) for e in ours)
    t_ts = max(ts_of(e, ["ts"]) for e in theirs)
    pick, side = (ours, "OURS") if o_ts >= t_ts else (theirs, "THEIRS")
    write(path, pick)
    verdicts.append("%s -> %s (ours_max=%s theirs_max=%s)" % (path, side, o_ts, t_ts))

    # compute_audit: latest newer-wins + history union by ts
    path = "results/compute_audit.json"
    ours = json.loads(show(":2:", path))
    theirs = json.loads(show(":3:", path))
    union = {}
    for e in theirs["history"]:
        union[e["ts"]] = e
    for e in ours["history"]:
        union[e["ts"]] = e
    merged = sorted(union.values(), key=lambda e: e["ts"])[-HIST_KEEP:]
    latest, side = (
        (ours["latest"], "OURS")
        if ours["latest"]["ts"] >= theirs["latest"]["ts"]
        else (theirs["latest"], "THEIRS")
    )
    write(path, {"latest": latest, "history": merged})
    verdicts.append(
        "%s -> latest %s (%s) history union=%d keep=%d" % (path, side, latest["ts"], len(union), len(merged))
    )

    print("\n".join(verdicts))


if __name__ == "__main__":
    main()
