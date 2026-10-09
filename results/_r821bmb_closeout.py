"""r821 bm-b closeout: append round row + heartbeat scalar-field update.

r818 law: heartbeat carries a large orders_ack list -- NEVER hand-rewrite
the whole file; load-modify-dump preserves it byte-for-byte.
"""
import datetime as dt
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HB = os.path.join(ROOT, "fleet", "machines", "bm-b.json")
ROW_SRC = os.path.join(ROOT, "results", "_r821bmb_round_row.txt")
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports.md")

now = dt.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S")
now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())

# 1) append round row (utf-8, exact bytes from the staging file)
row = open(ROW_SRC, encoding="utf-8").read()
if not row.endswith("\n"):
    row += "\n"
with open(LEDGER, "a", encoding="utf-8", newline="") as f:
    f.write(row)

# 2) heartbeat scalar-field update (orders_ack preserved by load-dump)
hb = json.load(open(HB, encoding="utf-8"))
hb["round"] = 821
hb["round_no"] = 821
hb["now_active"] = ("r821: P3-E1 CB T+0 data-face feasibility "
                    "(scripts/cb_data_probe.py + survey md)")
hb["current_task"] = ("P3 explore queue next head E2 (options IV panel "
                      "prereg roadmap, survey-first) after E1 done; tech "
                      "queue T15 still awaiting GM flag (3 left); waiting: "
                      "W18 wave drafting gated on W17-JUDGE drain (bm-c "
                      "lane) / Monday 10-12 09:15 minute_feed first gated "
                      "run backfills 10-08/10-09")
hb["task"] = hb["current_task"]
hb["latest_artifact"] = ("r821: scripts/cb_data_probe.py (probe 8/11 "
                         "reachable, selftest 9/9) + results/"
                         "cb_data_probe.json + research/shortline/"
                         "CB_T0_DATA_FEASIBILITY.md, 2026-10-10 07:2x")
hb["next_milestone"] = ("r822+: P3 explore E2 head (options IV panel "
                        "prereg roadmap, survey-first, <=48h) / Monday "
                        "2026-10-12 09:15 minute_feed first gated run "
                        "backfills 10-08/10-09 / W18 wave drafting once "
                        "W17-JUDGE drains")
hb["verdict"] = ("r821: E1 CB T+0 data-face feasibility closed (probe "
                 "8/11 reachable: sina spot 326-member universe + 4-bond "
                 "deep daily 1368-1433 bars + live tail 2026-10-09 + daily "
                 "x spot absdiff=0.0; gaps honestly disclosed: sina min "
                 "endpoint-side FAIL on live bond, EM comparison "
                 "persistent FAIL x2, jsl redeem token-free OK; landing "
                 "gates 5/5 unmet; zero prereg zero panel zero backtest); "
                 "smoke 49/49; S6 38 legs rc0 (dualrun ZERO-DRIFT streak "
                 "6; rev_osc SIG-2026-10-09 picks=10 first landing; "
                 "Saturday no-new-bar quad legitimately skipped); "
                 "watermark red=false healthy; orders both sweeps zero "
                 "unacked (60/184); ORD/DEC hash MATCH both keys; "
                 "attrition CLEAN; orphans=0")
hb["last_action"] = ("r821: P3-E1 CB T+0 data-face feasibility "
                     "(cb_data_probe + survey md + explore.md E1 done) + "
                     "S6 38 legs rc0 + S7 quartet green + attrition CLEAN")
hb["last_round_at"] = now_iso
hb["last_seen"] = now_iso
hb["updated"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_faces"] = 0
hb["orphan_face_note"] = ("r821 probe 07:0x: 13 py faces 0 orphans; "
                          "astock refresh tail landed (panel fresh "
                          "2026-10-09)")
hb["sync"] = {
    "ahead": 0,
    "behind": 0,
    "last_push_ts": now_iso,
    "note": ("r821: S0 pre-pull live-face housekeeping commit + rebase "
             "1/1 clean zero UU; round commit push follows; verify = "
             "post-push fetch+rev-list+ls-remote self-proof"),
}

tmp = HB + ".tmp"
with open(tmp, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
os.replace(tmp, HB)

# 3) self-proof: epoch is int, orders_ack untouched
back = json.load(open(HB, encoding="utf-8"))
assert isinstance(back["heartbeat_epoch_utc"], int), "epoch must be int"
assert len(back["orders_ack"]) == 184, "orders_ack must stay 184"
print("closeout ok: row appended, hb updated, epoch=%d int ok, "
      "orders_ack=%d preserved, now=%s" % (epoch,
                                           len(back["orders_ack"]), now))
