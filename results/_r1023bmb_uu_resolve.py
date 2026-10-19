"""r1023 bm-b stash-pop UU resolver (S0 absorb face).

Laws applied (r1008/r1015/r1020/r1022 lineages + D-20261019-02):
- fleet/machine-health.json      : per-machine union, newer-wins per machine face
- results/token_usage.json       : per-machine UNION (bm-b=ours, others=theirs; no ts field)
- results/d19_watermark.json     : whole-file newer-wins by ts
- results/{futures,lhb}_update_status.json : whole-file newer-wins by ts
- results/scorecard_v1.json      : whole-file newer-wins by ts
- results/watermark_red.json     : DU -> git rm --cached (machine-local takeover, D-20261019-02)
- Tools/register_loop_task.ps1   : handled outside (checkout --theirs + ASCII fix)
Exit 0 = all resolved; prints per-face verdict lines.
"""
import json
import subprocess
import sys

TS_KEYS = ("ts", "updated_at", "updated", "last_seen", "last_run",
           "generated", "asof", "heartbeat_epoch_utc", "clock_read")


def blob(stage, path):
    r = subprocess.run(["git", "show", ":%s:%s" % (stage, path)],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return json.loads(r.stdout.decode("utf-8", "replace"))


def best_ts(obj):
    if isinstance(obj, dict):
        for k in TS_KEYS:
            v = obj.get(k)
            if isinstance(v, str) and len(v) >= 10:
                return v
        for v in obj.values():
            t = best_ts(v)
            if t:
                return t
    return None


def resolve_newer_wins(path):
    ours, theirs = blob(2, path), blob(3, path)
    if ours is None or theirs is None:
        subprocess.run(["git", "checkout", "--theirs", "--", path])
        return "theirs (fallback: one side unparsable)"
    to, tt = best_ts(ours), best_ts(theirs)
    if to and tt:
        win = "ours" if to >= tt else "theirs"
    elif to:
        win = "ours"
    elif tt:
        win = "theirs"
    else:
        win = "theirs"
    if win == "ours":
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(ours, f, ensure_ascii=False, indent=1)
    else:
        subprocess.run(["git", "checkout", "--theirs", "--", path])
    return "%s (ours_ts=%s theirs_ts=%s)" % (win, to, tt)


def resolve_machine_union(path, mine_id):
    ours, theirs = blob(2, path), blob(3, path)
    if ours is None or theirs is None:
        subprocess.run(["git", "checkout", "--theirs", "--", path])
        return "theirs (fallback)"
    out = dict(theirs)
    for k, v in ours.items():
        if k not in theirs:
            out[k] = v
            continue
        tv = theirs[k]
        if isinstance(v, dict) and isinstance(tv, dict):
            to, tt = best_ts(v), best_ts(tv)
            if k == mine_id or (to and (not tt or to >= tt)):
                out[k] = v
        elif k == mine_id:
            out[k] = v
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    keys = sorted(set(list(ours) + list(theirs)))
    return "union keys=%s (bm-b face: ours)" % ",".join(keys)


def resolve_token_usage(path, mine_id):
    ours, theirs = blob(2, path), blob(3, path)
    if ours is None or theirs is None:
        subprocess.run(["git", "checkout", "--theirs", "--", path])
        return "theirs (fallback)"
    out = dict(theirs)
    mach_t = out.get("machines", {})
    mach_o = ours.get("machines", {})
    if isinstance(mach_t, dict) and isinstance(mach_o, dict):
        for k, v in mach_o.items():
            mach_t[k] = v if k == mine_id else mach_t.get(k, v)
        out["machines"] = mach_t
    for k, v in ours.items():
        if k != "machines" and k not in out:
            out[k] = v
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    return "union machines=%s (bm-b face: ours)" % ",".join(
        sorted(set(list(mach_t) + list(mach_o))))


def main():
    mine = "bm-b"
    for p in ("results/d19_watermark.json",
              "results/futures_update_status.json",
              "results/lhb_update_status.json",
              "results/scorecard_v1.json"):
        print("%s :: %s" % (p, resolve_newer_wins(p)))
    print("fleet/machine-health.json :: %s" %
          resolve_machine_union("fleet/machine-health.json", mine))
    print("results/token_usage.json :: %s" %
          resolve_token_usage("results/token_usage.json", mine))
    r = subprocess.run(["git", "rm", "--cached", "--", "results/watermark_red.json"],
                        capture_output=True)
    ok = r.returncode == 0
    ig = subprocess.run(["git", "check-ignore", "-q", "results/watermark_red.json"])
    print("results/watermark_red.json :: rm --cached rc=%d ignore=%d (disk face kept, D-20261019-02)"
          % (r.returncode, ig.returncode))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
