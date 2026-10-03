# -*- coding: utf-8 -*-
"""r412 bm-c heartbeat-only leg (bookkeeping assert tail-window too small; round
report append verified separately via PS read-back). Heartbeat epoch = int."""
import json, time, datetime

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
now_iso = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
now_epoch = int(time.time())

# round-report read-back verify (wide window, errors-tolerant per r607 family)
rp = ROOT + r"\round_reports-bm-c.md"
with open(rp, encoding="utf-8", errors="replace") as fh:
    tail = fh.read()[-2000:]
assert "r412" in tail and "\u7b49\u5f85\u6001\u503c\u5b88\u8f6e" in tail, "r412 line missing"
print("round-report readback ok (r412 line present)")

hp = ROOT + r"\fleet\machines\bm-c.json"
with open(hp, encoding="utf-8") as fh:
    hb = json.load(fh)
hb["activity_now"] = ("r412 waiting-state duty: S6 33/33 rc0 (dualrun streak 8) + waiting-object triage "
                      "(T-156 code-expired hold / moneyflow source-blocked / 688 lane-owned zero-touch)")
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = now_epoch
hb["current_task"] = ("r412 duty round complete; next: T-156 fresh-code window watch + moneyflow IC panel window + "
                      "D-06 reconciliation 10-07 + T-143 assembly 10-29")
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["latest_artifact"] = ("S6 regenerated faces @ 11:21-11:24 (REPORT-2026-10-03 / LIVE-2026-10-03 / scorecard per "
                         "lane_io origin-fresh guard) + results/_r412bmc_s6_chain.ps1 + _r412bmc_s6_runner.log")
hb["next_milestone"] = ("T-156 fresh-code window (bm-b sender leg re-issue, <=48h) + moneyflow IC batch on panel "
                       "completion + D-06 reconciliation 10-07 + T-143 assembly 10-29")
hb["prod_lanes"] = ("r412 waiting-state duty: S6 33/33 rc0 (dualrun streak 8, audit supply_gap structural "
                    "observation) + waiting-object triage per product law #2")
hb["round_no"] = 412
hb["updated_at"] = now_iso
hb["verdict"] = ("green (red=false; py_low_with_work_cands legal-idle per O-2115 sec.2: pool 7 ready all bm-a/bm-b "
                 "lane-owned or T-156 fuse-locked, board 0 open, bandit 0, sat-engine alive queue 0)")
with open(hp, "w", encoding="utf-8", newline="\n") as fh:
    json.dump(hb, fh, indent=1, ensure_ascii=False)
with open(hp, encoding="utf-8") as fh:
    chk = json.load(fh)
assert isinstance(chk["heartbeat_epoch_utc"], int) and chk["round_no"] == 412
assert "T" in chk["clock_read"] and "+" in chk["clock_read"]
print("heartbeat ok round_no=412 epoch=%d clock_read=%s" % (chk["heartbeat_epoch_utc"], chk["clock_read"]))
print("HEARTBEAT LEG OK")
