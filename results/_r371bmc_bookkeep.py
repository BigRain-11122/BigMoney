# -*- coding: utf-8 -*-
"""r371 bm-c bookkeeping: state round increment + heartbeat refresh (R170/R178 int-epoch law)."""
import json
import os
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
now_iso = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
epoch = int(time.time())


def load(path):
    with open(path, "rb") as fh:
        b = fh.read()
    enc = "utf-8-sig" if b[:3] == b"\xef\xbb\xbf" else "utf-8"
    return json.loads(b.decode(enc)), enc


def save(path, obj, enc):
    with open(path, "w", encoding=enc, newline="") as fh:
        json.dump(obj, fh, ensure_ascii=False, indent=1)


sp = os.path.join(ROOT, "state-bm-c.json")
hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
st, enc = load(sp)
hb, enc2 = load(hp)

try:
    import psutil
    psutil.cpu_percent(interval=None)  # prime per r319
    cpu = round(psutil.cpu_percent(interval=1.0), 1)
    ram = round(psutil.virtual_memory().available / (1024 ** 3), 1)
except Exception:
    cpu = hb.get("cpu_pct", 0.0)
    ram = hb.get("idle_ram_gb", 0.0)

st["round_no"] = 371
st["last_round_at"] = "r371"
st["last_round_ts"] = time.strftime("%m/%d/%Y %H:%M:%S")
st["updated"] = now_iso
st["heartbeat_epoch_utc"] = epoch
st["clock_read"] = now_iso
st["last_ts"] = now_iso
st["last_seen"] = now_iso
st["verify"] = ("r371: T-131 collector 2nd-hang cured (r340 law live-fire #2: pid alive + log/artifact "
                "36min double-stall @5076/5229 -> kill + stale-lock clear + checkpoint respawn todo=139, "
                "pid 42444, artifacts flowing 15:10:3x, ETA ~15:35) + root fixes landed: lock_alive "
                "pid-reuse false-positive cured (_pid_matches_collector psutil cmdline verify; killed pid "
                "23868 reused by a transient within 14s -> gate falsely read in-progress) + gate "
                "double-age stall self-heal leg (lock+log both >15min -> verified kill + throttle-bypass "
                "respawn), selftest 17/17; lane_io origin-ref heartbeat read leg landed (r366 fix "
                "candidate closed: origin-cross-veto before stale-takeover; live-fire this round = 7 S6 "
                "guard faces all correctly vetoed, local 67min stale view vs origin 16-18min fresh), "
                "selftest 18/18; S6 chain 37 legs rc0 (dualrun streak 47/3, WM green, attrition CLEAN); "
                "smoke 47/47; orders 144/0; D-19 937A373D MATCH-unchanged; self-heal 4/4 (watchdog was "
                "missing -> rebuilt 15:17); inbox 2 seat MSGs archived (bm-b W92 zero-cost yield + bm-a "
                "W93 yield/W94 seat); W92 finalize still FAIL-CLOSED on W91 bm-b (W90 landed 562,548)")
st["did"] = ("r371: T-131 hang #2 cured + collector gate hardened (pid-reuse verify + stall self-heal) "
             "+ lane_io origin-ref veto landed + S6 37 legs green")
st["current_task"] = ("T-131 respawn in flight todo~90 (ETA ~15:35 complete); W92 finalize waiting W91 "
                      "bm-b (W90 landed -> unblocked); T-144(c) D-06 remaining domains due 10-07; "
                      "CODELY 89.3KB hot-cold compile due (GM ruling face)")
st["next"] = ("(r372)(a) T-131 completion three-face verify + ticket progress note; (b) W91 bm-b lands -> "
              "W92 finalize one-pass (r518 origin live-head derive + r310 ls-tree completeness + r538 "
              "one-pass law + sec.7/8 backfill); (c) T-144(c) D-20261002-06 remaining domain splits "
              "(engine/data/pool/protocol + flow-sinking, due 10-07); (d) T-143 month-exam prep (10-29); "
              "(e) CODELY 89.3KB hot-cold compile window report to GM; (f) W95 seat publication at next "
              "never-dry step after W94 bm-a completes")
st["last_round"] = ("2026-10-02 r371 bm-c: T-131 hang#2 cured + collector hardened (pid-reuse + stall "
                    "self-heal) + lane_io origin-ref veto landed (7 faces live-fire) + S6 all-green + "
                    "smoke 47/47 + orders 144/0")
save(sp, st, enc)

hb["round_no"] = 371
hb["updated_at"] = now_iso
hb["last_seen"] = now_iso
hb["last_seen_at"] = now_iso
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["cpu_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["cpu_idle_pct"] = round(100.0 - cpu, 1)
hb["idle_ram_gb"] = ram
hb["free_ram_gb"] = ram
hb["ram_free_gb"] = ram
hb["verdict"] = ("healthy: T-131 collector respawned after hang#2 cure (pid-reuse gate fix + stall "
                 "self-heal landed, selftest 17/17); lane_io origin-ref veto landed (18/18, 7 faces "
                 "live-fire); W92 finalize pending W91 bm-b (W90 landed 562,548); WM green; engine alive "
                 "(W93 12/12 origin, W94 bm-a in flight); claws both installed MATCH")
hb["current_task"] = ("r371 done: T-131 hang#2 cured + collector gate hardened + lane_io origin-ref "
                      "veto landed; next = T-131 completion verify + W92 finalize on W91")
hb["activity_now"] = ("r371: T-131 respawn in flight (todo~90, ETA ~15:35) + lane_io origin-ref veto "
                      "live-fire 7/7 + S6 37 legs green")
hb["latest_artifact"] = ("scripts/update_fund_history.py (pid-reuse verify + double-age stall self-heal, "
                         "selftest 17/17, 2026-10-02 15:2x) + config/lane_io.py (origin-ref heartbeat "
                         "veto, selftest 18/18) + docs/daily_report/REPORT-2026-10-02.md + "
                         "docs/live_usage/LIVE-2026-10-02.md")
hb["next_milestone"] = ("T-131 full-universe completion ~15:35 today; W92 finalize after W91 bm-b lands "
                        "(<=48h); T-144(c) D-06 remaining domains 10-07; T-143 month-exam prep 10-29; "
                        "month-boundary first exam 10-31")
hb["prod_lanes"] = ("r371: T-131 collector hang#2 cured + gate hardened (pid-reuse + stall self-heal) + "
                    "lane_io origin-ref veto landed; chain W1..W90 landed (562,548), W91 bm-b "
                    "finalize-ready, W92 bm-c burned 12/12 finalize-pending; W93 12/12 origin (bm-b), "
                    "W94 bm-a in flight")
save(hp, hb, enc2)

for p in (sp, hp):
    with open(p, "rb") as fh:
        d = json.loads(fh.read().decode("utf-8-sig"))
    e = d["heartbeat_epoch_utc"]
    assert isinstance(e, int) and not isinstance(e, bool), p
print("bookkeep ok: round=371 epoch=%d cpu=%s ram_free=%s" % (epoch, cpu, ram))
print("self-verify PASS: heartbeat_epoch_utc int in state + heartbeat")
