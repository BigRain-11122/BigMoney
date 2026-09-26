"""r298 bm-b rebase batch resolver #4: the 10 hand-qualified MANUAL-STOP files.
Per-file qualification (fail-closed, no blind take):

  Pure runtime-metadata drift (whitelist key-name gaps, semantics identical):
  - token_usage.json        (R216 snapshot; delta_vs_prev baselines differ per
                             machine's own prev face; meter re-derives whole
                             doc from files each round -> newest wins)
  - paper_export/latest.json + export-2026-09-24.json  (only state_updated /
                             generated_from_state_updated differ; trading
                             content byte-identical)
  - lhb_update_status.json / futures_update_status.json (only last_attempt)

  Legitimately newer machine-state snapshots (upstream r294 ran 05:0x with
  post-integration faces):
  - daily_scorecard.json    (post_review_latest row = bm-a r294 T-87-CN-KLINE
                             registration, 42 vs 41 fields)
  - dashboard_status.json   (autofill face reflects pool done-flip: ready 0,
                             last_tick 05:00:01)
  - dashboard_status.js     (same data, wrapper face, take same side)

  Semantically complete faces (stage3 derived from pre-c986f8c5 tree lacking
  CN-KLINE judged products -> ledger totals/skill_line/landing_hooks short):
  - scorecard_v1.json       (ledger_head 200396 vs 198389 = +2007 CN-KLINE rows)
  - strategy_scorecard.json (landing_hooks CN-KLINE-PATTERN entry present)

Resolution: take stage2 (upstream bm-a r294) whole bytes verbatim; parse-verify
after write; marker sweep. Next round's S6 re-derives from the union tree.
"""
import io
import json
import subprocess

FILES = [
    "results/token_usage.json",
    "results/paper_export/latest.json",
    "results/paper_export/export-2026-09-24.json",
    "results/lhb_update_status.json",
    "results/futures_update_status.json",
    "results/daily_scorecard.json",
    "results/dashboard_status.json",
    "results/dashboard_status.js",
    "results/scorecard_v1.json",
    "results/strategy_scorecard.json",
]


def blob(stage, path):
    return subprocess.run(["git", "show", f":{stage}:{path}"],
                           capture_output=True, check=True).stdout


for p in FILES:
    data = blob(2, p)                     # stage2 = upstream bm-a r294 face
    with io.open(p, "wb") as f:
        f.write(data)
    if p.endswith(".json"):
        json.load(io.open(p, encoding="utf-8-sig"))
    body = data.decode("utf-8", errors="replace")
    bad = [l for l in body.splitlines()
           if l.startswith(("<<<<<<<", "=======", ">>>>>>>"))]
    assert not bad, (p, bad[:2])
    print("take-stage2 OK:", p, len(data), "bytes")

print("10/10 hand-qualified files resolved to upstream r294 face")
