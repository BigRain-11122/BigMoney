# -*- coding: utf-8 -*-
# r845 bm-b rebase resolver: 18 UU shared S6 regen faces (bm-a r963 vs bm-b r845)
# Rules: runnable_pool.json -> theirs (origin live claim, my settle was stale-base);
# token_usage.json -> per-key max-union (append-ish ledger, r678 law);
# other .json -> ts-newer-wins (S6 deterministic regen faces, next round re-derives);
# .md/.js twins -> follow their .json sibling decision.
import json
import subprocess
import sys

CONFLICTS = [
    "docs/daily_report/REPORT-2026-10-10.json",
    "docs/daily_report/REPORT-2026-10-10.md",
    "docs/live_usage/LIVE-2026-10-10.json",
    "docs/live_usage/LIVE-2026-10-10.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/regime_state.json",
    "results/runnable_pool.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def side(path, n):
    r = subprocess.run(["git", "show", ":%d:%s" % (n, path)], capture_output=True)
    return r.stdout


def parse(b):
    try:
        return json.loads(b.decode("utf-8")), True
    except Exception:
        return None, False


def get_ts(obj):
    if not isinstance(obj, dict):
        return None
    for k in ("ts", "updated_at", "updated", "generated_at", "generated", "written_at"):
        v = obj.get(k)
        if isinstance(v, str) and len(v) >= 10:
            return v
    return None


def maxunion(a, b):
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            out[k] = maxunion(out[k], v) if k in out else v
        return out
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) and not isinstance(b, bool):
        return max(a, b)
    if isinstance(a, list) and isinstance(b, list):
        return a if len(a) >= len(b) else b
    return a


def main():
    decisions = {}
    # pass 1: json files
    for p in CONFLICTS:
        if not p.endswith(".json"):
            continue
        ours, theirs = side(p, 2), side(p, 3)
        if p == "results/runnable_pool.json":
            decisions[p] = ("theirs", "pool live claim authority (my settle stale-base)")
            continue
        o, ok1 = parse(ours)
        t, ok2 = parse(theirs)
        if ok1 and ok2:
            if p == "results/token_usage.json":
                merged = maxunion(o, t)
                with open(p, "wb") as f:
                    f.write((json.dumps(merged, ensure_ascii=False, indent=1) + "\n").encode("utf-8"))
                decisions[p] = ("union", "per-key max-union (r678 law)")
                continue
            to, tt = get_ts(o), get_ts(t)
            if to and tt:
                if to >= tt:
                    decisions[p] = ("ours", "ts %s >= %s" % (to, tt))
                    with open(p, "wb") as f:
                        f.write(ours)
                else:
                    decisions[p] = ("theirs", "ts %s > %s" % (tt, to))
                    with open(p, "wb") as f:
                        f.write(theirs)
            else:
                decisions[p] = ("ours", "no ts pair, regen face ours-keep")
                with open(p, "wb") as f:
                    f.write(ours)
        else:
            # unparseable json (maybe CRLF/mixed): keep ours
            decisions[p] = ("ours", "parse fail keep-ours")
            with open(p, "wb") as f:
                f.write(ours)
    # pass 2: md/js twins follow sibling json
    twin = {
        "docs/daily_report/REPORT-2026-10-10.md": "docs/daily_report/REPORT-2026-10-10.json",
        "docs/live_usage/LIVE-2026-10-10.md": "docs/live_usage/LIVE-2026-10-10.json",
        "docs/live_usage/LIVE-latest.md": "docs/live_usage/LIVE-latest.json",
        "results/dashboard_status.js": "results/dashboard_status.json",
    }
    for p, sib in twin.items():
        mode = decisions.get(sib, ("ours", "?"))[0]
        if mode == "theirs":
            with open(p, "wb") as f:
                f.write(side(p, 3))
        else:
            with open(p, "wb") as f:
                f.write(side(p, 2))
        decisions[p] = (mode, "twin follows " + sib)
    for p in sorted(decisions):
        print("%s -> %s (%s)" % (p, decisions[p][0], decisions[p][1]))
    # stage resolved
    for p in decisions:
        subprocess.run(["git", "add", p])
    print("staged %d resolved files" % len(decisions))


if __name__ == "__main__":
    main()
