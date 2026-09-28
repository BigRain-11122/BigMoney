# -*- coding: utf-8 -*-
"""r412 bm-b rebase-conflict resolver batch 2 (skill: bigmoney-conflict-resolve).

Face: my harvest commit (dead-session 06:0x S6 outputs) replaying on top of
origin fb0ce7fec (bm-c r201, whose S6 chain did lawful stale-takeovers of
bm-a-guarded faces per O-2100 s2.4 at 06:12-06:14 -- newer than dead
session's 06:02-06:06). 16 UU, all known classes:

  - 12 snapshots + LIVE/REPORT md twins  -> take s2 (bm-c, newer) blob
    verbatim (probe: s2 06:12-06:14 > s3 06:02-06:06 all twelve)
  - results/dashboard_status.js          -> js-wrapper: take-side whole
    bytes (twinned with dashboard_status.json = s2)
  - results/regime_state.json            -> rolling-ledger: union history/
    transitions (both sides 2 rows) + state fields take-new (s2 06:12:24)
  - results/compute_audit.json          -> rolling-ledger: union history
    (s2=179, s3=180, dedup ts+machine+flags) + latest take-new (s2 06:03:19)

Rebase stage semantics: stage2 = upstream base (origin/bm-c side),
stage3 = my replayed harvest. All take-side decisions ts-probed, not blind.
"""
import json
import subprocess
import sys

ROOT = r"E:\Fluxgroup\FluxGroup\quant\bigmoney"


def blob(stage, path):
    out = subprocess.run(["git", "show", f":{stage}:{path}"], cwd=ROOT,
                         capture_output=True)
    if out.returncode != 0:
        raise RuntimeError(f"git show :{stage}:{path} rc={out.returncode}")
    return out.stdout.decode("utf-8-sig")


def write(path, text):
    with open(path.replace("/", "\\"), "w", encoding="utf-8",
              newline="\n") as fh:
        fh.write(text)


SNAPSHOTS = [
    "docs/daily_report/REPORT-2026-09-29.json",
    "docs/daily_report/REPORT-2026-09-29.md",
    "docs/live_usage/LIVE-2026-09-29.json",
    "docs/live_usage/LIVE-2026-09-29.md",
    "docs/live_usage/LIVE-latest.json",
    "docs/live_usage/LIVE-latest.md",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/fundamental_b_layer_filter.json",
    "results/futures_update_status.json",
    "results/lhb_update_status.json",
    "results/prospect_promotion/_summary.json",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/token_usage.json",
    "results/update_status.json",
]


def resolve_snapshots():
    took = []
    for p in SNAPSHOTS:
        write(p, blob(2, p))
        took.append({"path": p, "took": "s2"})
    return took


def resolve_audit():
    s2, s3 = json.loads(blob(2, "results/compute_audit.json")), \
        json.loads(blob(3, "results/compute_audit.json"))
    h2 = s2.get("history") or []
    h3 = s3.get("history") or []

    def ident(row):
        return (str(row.get("ts")), str(row.get("machine")),
                json.dumps(row.get("flags"), sort_keys=True))

    seen = {}
    for row in h2 + h3:
        seen.setdefault(ident(row), row)
    merged = sorted(seen.values(), key=lambda r: str(r.get("ts")))
    assert len(merged) >= max(len(h2), len(h3)), "union zero-loss violated"
    base = s2 if str(s2.get("latest", {}).get("ts", "")) >= \
        str(s3.get("latest", {}).get("ts", "")) else s3
    out = dict(base)
    out["history"] = merged
    write("results/compute_audit.json",
          json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    return {"history_s2": len(h2), "history_s3": len(h3),
            "history_merged": len(merged),
            "latest_from": "s2" if base is s2 else "s3"}


def resolve_regime():
    s2, s3 = json.loads(blob(2, "results/regime_state.json")), \
        json.loads(blob(3, "results/regime_state.json"))

    def row_ident(e):
        return (str(e.get("asof")), str(e.get("raw")), str(e.get("state")),
                str(e.get("green_streak")), str(e.get("days_in_state")))

    seen = {}
    for e in (s2.get("history") or []) + (s3.get("history") or []):
        seen.setdefault(row_ident(e), e)
    merged = sorted(seen.values(), key=lambda r: str(r.get("asof")))
    base = s2 if str(s2.get("updated", "")) >= str(s3.get("updated", "")) \
        else s3
    tseen = {}
    for t in (s2.get("transitions") or []) + (s3.get("transitions") or []):
        tseen.setdefault(json.dumps(t, sort_keys=True), t)
    out = dict(base)
    out["history"] = merged
    out["transitions"] = list(tseen.values())
    if base is s2 and out == s2:
        write("results/regime_state.json", blob(2, "results/regime_state.json"))
        verbatim = True
    else:
        write("results/regime_state.json",
              json.dumps(out, ensure_ascii=False, indent=1) + "\n")
        verbatim = False
    return {"history_merged": len(merged),
            "base": "s2" if base is s2 else "s3", "verbatim": verbatim}


def main():
    snaps = resolve_snapshots()
    audit = resolve_audit()
    regime = resolve_regime()
    for p in SNAPSHOTS + ["results/compute_audit.json",
                          "results/regime_state.json"]:
        if p.endswith(".js") or p.endswith(".md"):
            continue
        with open(p.replace("/", "\\"), encoding="utf-8") as fh:
            json.load(fh)
    print(json.dumps({"snapshots": len(snaps), "took": "s2 all (probed)",
                      "audit": audit, "regime": regime},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
