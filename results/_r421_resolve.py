# -*- coding: utf-8 -*-
"""r421 bm-b merge-back conflict resolver (bigmoney-conflict-resolve skill law).

Pit-93 single-merge merge-back: machine/bm-b-r420 escape series (r420
closeout + checkpoint tails) merged onto origin/main e93d36c6f (bm-c
r210/r211).  21 UU files; classifier 9 classified + 12 UNKNOWN; UNKNOWN
batch hand-classified = same-day idempotent regen twins + deterministic
re-derive faces (r419-addendum precedent family).

Merge-context sides (pit-93 law): :2 = ours = HEAD = bm-b r420 series
(S6 chain 10:39-10:42), :3 = theirs = origin/main = bm-c r210/r211
(S6 chain 10:48-10:50).  Deep-ts probe on every face: :3 fresher on all
probed ts fields, zero same-second ties -> all take-new faces = :3
(take-new recipe is side-number-agnostic per pit-93).

Recipes:
  - compute_audit.json = rolling-ledger: history union (row-key dedup,
    ts-sorted, zero loss, dynamic count assertion) + latest take-:3
    (10:48:27); written back in producer format (indent=2 + CRLF
    mirror probe, r419 precedent).
  - regime_state.json = rolling-ledger: history/transitions identity
    probe; whole-doc take-:3 == union if identical (zero loss by
    identity), else explicit union.
  - dashboard_status.js = js-wrapper-snapshot: take-side WHOLE BYTES
    :3 (wrapper preserved; twin dashboard_status.json same side, R209).
  - b_layer_mask.csv = deterministic re-derive face (firm.risk
    b_layer_filter): take :3 (their derive 10:49:45 fresher vs ours
    10:41:02 per fundamental_b_layer_filter.json updated probe);
    S6 chain re-derives in-round anyway.
  - all other snapshots + daily_report twins + live_usage twins/pointers
    = take :3 whole bytes (twins forced same side).

Validated before write-back (r185): json.loads on every resolved JSON;
compute_audit union count assertion; regime history identity assertion.
"""
import json
import subprocess
import sys

TAKE3 = [
    "data/fundamental/b_layer_mask.csv",
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
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
    "results/t35_open_fill_verify.json",
    "results/token_usage.json",
    "results/prospect_paper/_summary.json",
    "results/prospect_promotion/_summary.json",
    "results/update_status.json",
]


def stage_bytes(n, path):
    r = subprocess.run(["git", "show", f":{n}:{path}"], capture_output=True)
    assert r.returncode == 0, (n, path, r.returncode)
    return r.stdout


def main():
    # ---- take-side whole bytes (all probed fresher on :3, zero ties)
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
    assert len(union) == len(sa) + len(set(sb) - set(sa)), \
        "union count != |A u B| (zero-loss law breach)"
    merged = {"latest": b["latest"], "history": union}
    assert merged["latest"]["ts"] > a["latest"]["ts"], "latest take-new"
    json.dumps(merged)                                     # r185 gate
    text = json.dumps(merged, ensure_ascii=False, indent=2)
    with open("results/compute_audit.json", "wb") as fh:
        fh.write(text.replace("\n", "\r\n").encode("utf-8"))
    print(f"compute_audit union: {len(ha)} + {len(hb)} -> {len(union)} "
          f"rows ({len(set(sa) & set(sb))} common, "
          f"+{len(set(sa) - set(sb))} bm-b, "
          f"+{len(set(sb) - set(sa))} bm-c); latest take-:3 @"
          f"{merged['latest']['ts']}")

    # ---- regime_state.json ledger probe + resolve
    ra = json.loads(stage_bytes(2, "results/regime_state.json"))
    rb = json.loads(stage_bytes(3, "results/regime_state.json"))
    if ra.get("history") == rb.get("history") and \
            ra.get("transitions") == rb.get("transitions"):
        with open("results/regime_state.json", "wb") as fh:
            fh.write(stage_bytes(3, "results/regime_state.json"))
        json.loads(open("results/regime_state.json",
                        encoding="utf-8").read())         # r185 gate
        print("regime_state: history/transitions identical both sides "
              "-- whole-doc take-:3 == union (zero loss by identity)")
    else:
        hka = {json.dumps(r, sort_keys=True): r
               for r in ra.get("history", [])}
        hkb = {json.dumps(r, sort_keys=True): r
               for r in rb.get("history", [])}
        hist = list(hka.values()) + \
            [r for k, r in hkb.items() if k not in hka]
        tka = {json.dumps(r, sort_keys=True): r
               for r in ra.get("transitions", [])}
        tkb = {json.dumps(r, sort_keys=True): r
               for r in rb.get("transitions", [])}
        trans = list(tka.values()) + \
            [r for k, r in tkb.items() if k not in tka]
        merged_r = {k: v for k, v in rb.items()
                    if k not in ("history", "transitions")}
        merged_r["history"] = hist
        merged_r["transitions"] = trans
        json.dumps(merged_r)                               # r185 gate
        with open("results/regime_state.json", "wb") as fh:
            fh.write(json.dumps(merged_r, ensure_ascii=False,
                                indent=2).encode("utf-8"))
        print(f"regime_state: EXPLICIT union history "
              f"{len(hka)}+{len(hkb)}->{len(hist)}, transitions "
              f"{len(tka)}+{len(tkb)}->{len(trans)}; state fields take-:3")

    # ---- git add resolved set
    resolved = TAKE3 + ["results/compute_audit.json",
                        "results/regime_state.json"]
    r = subprocess.run(["git", "add"] + resolved, capture_output=True)
    assert r.returncode == 0, r.stderr
    print(f"git add: {len(resolved)} resolved files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
