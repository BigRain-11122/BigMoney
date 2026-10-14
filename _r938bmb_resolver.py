"""r938 S0 rebase resolver -- fleet/machine-health.json row-level union heal.

Conflict: replay pick 05f1a00e9 (r937 pre-round, tail ts 15:11) vs origin base
77132634b (bm-a r998 estate absorb, dual-tail 14:11+14:36 union heal already landed).
Both sides appended oversight rows to the same hourly ledger since merge base.
Law: r996 c85e806c9 / r998 77132634b dual-tail union precedent (not r911
whole-file newer-wins -- would drop the origin-only 14:36 row).

Resolution: recursive walk both stage blobs, collect every dict carrying a "ts"
key (PS ConvertTo-Json nests entries in value/Count envelopes), row-level union
dedup by canonical content, sort by ts, keep last 168 (C-20261011-02 rolling
ledger spec), write flat JSON array. PS ConvertFrom-Json consumer handles flat
list fine; next oversight append re-serializes with its own envelope.
"""
import json
import subprocess

PATH = "fleet/machine-health.json"
KEEP = 168


def show(stage):
    return subprocess.check_output(["git", "show", stage + PATH]).decode("utf-8")


def collect(node, out):
    """Recursively collect dicts that carry a ts key (ledger rows)."""
    if isinstance(node, dict):
        if "ts" in node:
            out.append(node)
            return
        for v in node.values():
            collect(v, out)
    elif isinstance(node, list):
        for v in node:
            collect(v, out)


def main():
    rows = []
    for stage, label in ((":2:", "HEAD(origin-r998)"), (":3:", "ours(05f1a00e9)")):
        side = []
        collect(json.loads(show(stage)), side)
        rows.extend(side)
        print("%s side rows=%d max_ts=%s" % (label, len(side), max((r.get("ts", "") for r in side), default="")))

    union = {}
    for r in rows:
        union[json.dumps(r, ensure_ascii=False, sort_keys=True)] = r
    merged = sorted(union.values(), key=lambda r: r.get("ts", ""))[-KEEP:]
    with open(PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(merged, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(
        "union rows_in=%d distinct=%d kept=%d tail_ts=%s"
        % (len(rows), len(union), len(merged), merged[-1].get("ts", "") if merged else "")
    )
    ts_list = [r.get("ts", "") for r in merged]
    assert "2026-10-14 14:36" in ts_list and "2026-10-14 15:11" in ts_list, "dual-tail assertion failed"
    print("dual-tail assertion PASS (14:36 + 15:11 both present)")


if __name__ == "__main__":
    main()
