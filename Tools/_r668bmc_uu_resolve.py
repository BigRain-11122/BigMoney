# -*- coding: utf-8 -*-
"""r668 bm-c rebase resolver: 17 ts-newer faces -> MINE whole-file;
compute_audit.json -> latest ts-newer + history/samples row-union (r667/r528
two-rule precedent). Writes resolved files in place, prints per-file receipt."""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
R = "K:/Fluxgroup/FluxGroup/quant/bigmoney/"
PAT = re.compile(r"<<<<<<< HEAD\r?\n(.*?)\|\|\|\|\|\|\|.*?\r?\n(.*?)=======\r?\n(.*?)>>>>>>> [^\r\n]*\r?\n", re.S)

TS_FILES = [
    "docs/daily_report/REPORT-2026-10-07.json",
    "docs/daily_report/REPORT-2026-10-07.md",
    "docs/live_usage/LIVE-2026-10-07.json",
    "docs/live_usage/LIVE-2026-10-07.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/_attrition_guard_scan.json",
    "results/dashboard_status.js",
    "results/dashboard_status.json",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/regime_state.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]
CA = "results/compute_audit.json"


def resolve_sides(raw, side_idx):
    """Rebuild full file with every hunk resolved to the chosen side (2=mine, 0=head)."""
    out = []
    pos = 0
    for m in PAT.finditer(raw):
        out.append(raw[pos:m.start()])
        out.append(m.group(side_idx))
        pos = m.end()
    out.append(raw[pos:])
    return "".join(out)


fails = []
for f in TS_FILES:
    path = R + f
    raw = open(path, "rb").read().decode("utf-8")
    hunks = PAT.findall(raw)
    if not hunks:
        fails.append((f, "no hunks parsed"))
        continue
    # integrity: no markers left after resolution
    resolved = resolve_sides(raw, 2)
    if "<<<<<<<" in resolved or ">>>>>>>" in resolved or "=======" in resolved:
        fails.append((f, "marker residue"))
        continue
    # strict reparse for .json faces (js/md skipped: prose faces)
    if f.endswith(".json"):
        try:
            json.loads(resolved)
        except Exception as e:
            fails.append((f, "reparse " + str(e)[:60]))
            continue
    with open(path, "wb") as fh:
        fh.write(resolved.encode("utf-8"))
    print("RESOLVED ts-newer MINE:", f, "(hunks=%d)" % len(hunks))

# ---- compute_audit.json two-rule ----
raw = open(R + CA, "rb").read().decode("utf-8")
head_full = resolve_sides(raw, 0)
mine_full = resolve_sides(raw, 2)
assert "<<<<<<<" not in head_full and "<<<<<<<" not in mine_full, "marker residue CA"
head_j = json.loads(head_full)
mine_j = json.loads(mine_full)


def union_rows(a, b):
    seen = set()
    out = []
    for row in list(a) + list(b):
        key = json.dumps(row, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out


merged = dict(mine_j)  # ts-newer side as base (latest face)
union_summary = {}
for key in ("history", "samples", "runs", "rows"):
    ha, mb = head_j.get(key), mine_j.get(key)
    if isinstance(ha, list) or isinstance(mb, list):
        ha = ha or []
        mb = mb or []
        u = union_rows(ha, mb)
        merged[key] = u
        union_summary[key] = (len(ha), len(mb), len(u))
    elif key in head_j and key not in mine_j:
        merged[key] = head_j[key]
for key in head_j:
    if key not in merged:
        merged[key] = head_j[key]
# 'latest' + scalars: ts-newer side (mine) already the base; nothing to do
json.dump({"head_latest_ts": head_j.get("latest", {}).get("ts"),
           "mine_latest_ts": mine_j.get("latest", {}).get("ts"),
           "union": union_summary},
          open(R + "results/_r668bmc_ca_union_receipt.json", "w", encoding="utf-8", newline="\n"),
          ensure_ascii=False, indent=1)
with open(R + CA, "wb") as fh:
    fh.write(json.dumps(merged, ensure_ascii=False, indent=2).encode("utf-8"))
print("RESOLVED compute_audit row-union:", union_summary,
      "latest head=%s mine=%s -> mine(ts-newer)" % (head_j.get("latest", {}).get("ts"), mine_j.get("latest", {}).get("ts")))

if fails:
    print("FAILS:", fails)
    sys.exit(1)
print("ALL RESOLVED")
