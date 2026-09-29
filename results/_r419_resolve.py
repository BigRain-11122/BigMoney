# -*- coding: utf-8 -*-
"""r419 bm-b rebase-conflict resolver (bigmoney-conflict-resolve skill law).

Rebase replay of round-419 closeout commit onto origin/main cbacb61c7
(bm-a same-window S6 chain).  Classifier: 13 classified + 4 UNKNOWN
(live_usage family = manual same-day idempotent regen twin face ->
snapshot take-new by generated ts, twins same side).

Sides probed by explicit stage number (r402 side-assumption ban):
  :2 = HEAD (origin/main = bm-a side, S6 chain ~10:18-10:19)
  :3 = replayed commit (bm-b side, S6 chain ~10:20-10:22, fresher on
       every snapshot face)

Recipes:
  - compute_audit.json = rolling-ledger: history union (identical-row
    dedup, ts-sorted, zero loss: 200 common + 1 + 1 = 202) + latest
    take-new (:3, 10:20:27); written back in producer format
    (indent=2 + CRLF mirror probe).
  - regime_state.json = rolling-ledger whose history/transitions rows
    are byte-identical on both sides -> whole-doc take :3 IS the union
    (zero loss by identity).
  - dashboard_status.js = js-wrapper-snapshot: take-side WHOLE BYTES
    (:3, fresher; wrapper preserved byte-for-byte; twin
    dashboard_status.json also :3).
  - all other snapshots + daily_report twins + live_usage twins/pointers
    = take :3 (deep-ts probe: bm-b side fresher on every face; twins
    forced same side).

Validated before write-back (r185): json.loads on every resolved JSON;
union count assertion (== 202); regime history identity assertion.
"""
import json
import subprocess
import sys

TAKE3 = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
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


def stage_bytes(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    assert r.returncode == 0, (n, path, r.returncode)
    return r.stdout


def main():
    # ---- take-side whole bytes (twins/pointers/js all :3)
    for p in TAKE3:
        with open(p, "wb") as fh:
            fh.write(stage_bytes(3, p))
        if p.endswith(".json"):
            json.loads(open(p, encoding="utf-8").read())   # r185 gate
    print(f"take-:3 whole bytes: {len(TAKE3)} files")

    # ---- compute_audit.json rolling-ledger union
    a = json.loads(stage_bytes(2, "results/compute_audit.json"))
    b = json.loads(stage_bytes(3, "results/compute_audit.json"))
    ha, hb = a["history"], b["history"]
    sa = {json.dumps(r, sort_keys=True): r for r in ha}
    sb = {json.dumps(r, sort_keys=True): r for r in hb}
    union = list(sa.values()) + [r for k, r in sb.items() if k not in sa]
    union.sort(key=lambda r: r.get("ts", ""))
    assert len(union) == len(sa) + len(set(sb) - set(sa)) == 202, \
        f"union count {len(union)} != 202 (zero-loss law breach)"
    merged = {"latest": b["latest"], "history": union}
    assert merged["latest"]["ts"] > a["latest"]["ts"], "latest take-new"
    json.dumps(merged)                                     # r185 gate
    text = json.dumps(merged, ensure_ascii=False, indent=2)
    with open("results/compute_audit.json", "wb") as fh:
        fh.write(text.replace("\n", "\r\n").encode("utf-8"))
    print(f"compute_audit union: {len(ha)} + {len(hb)} -> "
          f"{len(union)} rows (200 common, +1 bm-a @10:18:05, "
          f"+1 bm-b @10:20:27); latest take-:3 @"
          f"{merged['latest']['ts']}")

    # ---- regime_state identity assertion (whole-doc take-:3 already
    # written above; verify its history == both sides' identical rows)
    ra = json.loads(stage_bytes(2, "results/regime_state.json"))
    rb = json.loads(open("results/regime_state.json", encoding="utf-8")
                    .read())
    assert ra["history"] == rb["history"] and ra["transitions"] == \
        rb["transitions"] == [], "regime ledger identity breach"
    print("regime_state: history/transitions identical both sides -- "
          "whole-doc take-:3 == union (zero loss by identity)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
