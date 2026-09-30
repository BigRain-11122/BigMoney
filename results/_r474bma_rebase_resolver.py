"""r474 bm-a rebase UU resolver (canon: r461/r462 recipes).

Direction is NEVER assumed from rebase semantics -- per-file staged-blob ts
probe decides (r461 pitlaw). File classes:
  - marks-*.jsonl                -> row-level union (exact-line dedup)
  - snapshot/status .json/.md    -> take the side with the LATER internal
                                    timestamp (generated/ts/clock field or
                                    per-trader tick ts); tie -> stage-2.
Asserts zero-loss for union and prints per-file verdicts.
"""
import json
import re
import subprocess
import sys

FILES = [
    "docs/daily_report/REPORT-2026-09-30.json",
    "docs/daily_report/REPORT-2026-09-30.md",
    "docs/live_usage/LIVE-2026-09-30.json",
    "docs/live_usage/LIVE-2026-09-30.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/compute_audit.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/paper/marks/marks-20260930.jsonl",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]

TS_KEYS = ("ts", "generated", "generated_utc", "generated_at", "updated",
           "updated_at", "last_run", "clock_read", "date")


def blob(stage, path):
    r = subprocess.run(["git", "show", f":{stage}:{path}"], capture_output=True)
    return r.stdout.decode("utf-8", errors="replace")


def ts_of(text):
    """Best-effort latest internal timestamp in a blob (ISO-ish)."""
    stamps = re.findall(
        r"20\d{2}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2})?", text)
    return max(stamps) if stamps else ""


def side_ts(stage, path):
    return ts_of(blob(stage, path))


def main():
    verdicts = []
    for path in FILES:
        if path.endswith(".jsonl"):
            a = blob(2, path).splitlines()
            b = blob(3, path).splitlines()
            seen, out = set(), []
            for l in a + b:
                if l.strip() and l not in seen:
                    seen.add(l)
                    out.append(l)
            assert len(out) >= max(len(a), len(b)), f"union loss {path}"
            with open(path, "w", encoding="utf-8", newline="\n") as fh:
                fh.write("\n".join(out) + ("\n" if out else ""))
            verdicts.append((path, f"union {len(a)}+{len(b)}->{len(out)}"))
        else:
            t2, t3 = side_ts(2, path), side_ts(3, path)
            take = 2 if t2 >= t3 else 3
            data = blob(take, path)
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(data)
            verdicts.append((path, f"take stage{take} (ts2={t2!r} ts3={t3!r})"))
    for path, v in verdicts:
        print(f"{v:60s} <- {path}")
    # marks union parse check
    ok = 0
    for line in open("results/paper/marks/marks-20260930.jsonl", encoding="utf-8"):
        if line.strip():
            json.loads(line)
            ok += 1
    print(f"marks union parse check: {ok} rows OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
