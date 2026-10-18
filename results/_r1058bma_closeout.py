# -*- coding: utf-8 -*-
# r1058 bm-a closeout: state + heartbeat + round report (waiting-state guard round)
import json, time, psutil
from datetime import datetime, timezone, timedelta

CST = timezone(timedelta(hours=8))
now_dt = datetime.now(CST)
now_iso = now_dt.isoformat(timespec="seconds")
epoch = int(time.time())

R = "r1058"

did = (R + ": (1) S0 pull --rebase fast-forward 3 commits (bm-c r1091 W268 CYCLE COMPLETE + W269 seat publish be60d5e075); "
       "round-start dirty own faces -> stash/pull/pop, watermark_red UU -> HEAD version (origin=bm-c 14:07 fresher write, "
       "derived file newer-wins r1028 family, zero loss); "
       "(2) S0.5: orders_ack_scan CLEAN 102/111/0 zero unacked zero face divergence; D-19 update --advance NOOP "
       "(dec 4cfdd17c hold / ord 5d871243 hold, heartbeat mirrors synced 3); orphan probe 0/16 py faces 1 resident server; "
       "(3) W269 seat MSG-1407 consumed: owner=bm-c (88th own wave, prereg derive = bm-c next window FIRST ACTION) "
       "-> bm-a yields per fleet README sec.4; r1057 next-face assumption 'seat names bm-a' superseded by seat text; "
       "zero skip-claim held (zero W269 bm-a artifacts on origin); seat MSG archived to processed; "
       "MSG-1200 stays in inbox (addressed bm-a director seat / BigStream lane, informational zero BigMoney loop obligation); "
       "(4) agenda census: T/E boards all done-closed, job_list empty, backlog zero bm-a claimable lines, "
       "watermark advisory=stale claimed (MF IC batch, panel source-blocked), satengine ALIVE queue0 (wave supply=bm-c lane); "
       "E14 daban line r874 close-confirmed, GATE-RECHECK-MP1 r870 closed-confirmed, remaining catalog items all blocked "
       "(P4 point-in-time factors=CEO physical six items / QDII #11=P1 signature gate / options #15=domain freeze 2027-09) "
       "-> honest waiting-state guard round (one-line declaration law); "
       "(5) S6 43 legs + live_paper all rc0 bad=0 (_r1058bma_s6chain.ps1 = r1057 face verbatim clone; Sunday data legs "
       "lawful no-op; MF Monday <=10-19 blockade adjudication armed with day-8..10 RemoteDisconnected chain); "
       "(6) smoke 49/49 + loop task pin=8 no-op + watchdog re-registered (S4U flip access-denied = carried "
       "C-20261016-04 elevation window) + pre-commit/pre-push claws reinstalled LF-normalized + "
       "idle --worked 1->0 (basis = S6 43-leg pipeline + guard faces per r1050 precedent)")

cur_task = (R + ": guard round executed (seat consume+yield, S6 all-green, self-heal faces); "
            "waiting faces: W270 owner naming rides bm-c W269 sec.7/8 backfill; MF Monday adjudication <=10-19; "
            "council sec.6 first ruling table <=10-20 12:00")

nxt = ("r1059: (1) W269 chain watch (bm-c prereg derive -> five-face splice -> engine self-burn -> finalize; "
       "W270 owner naming rides W269 sec.7/8 backfill -- bm-a window opens as FIRST ACTION when named, "
       "fresh live walk only, no probe reuse); "
       "(2) MF blockade Monday adjudication <=10-19 (day-8..10 RemoteDisconnected chain armed, Monday S6 retest "
       "adds day-11/12 evidence); (3) council sec.6 first ruling table watch <=10-20 12:00; "
       "(4) E20 three-axis synthesis (sentiment x index x fundamental) judged candidate = GM/council signature "
       "reserved face (PREREG_TEMPLATE front door), loop does not self-start; "
       "(5) dual-task S4U conversion awaits elevation window (C-20261016-04 carried)")

verdict = ("GREEN: " + R + ": guard round all green -- W269 seat consumed owner=bm-c bm-a yielded zero skip-claim + "
           "S6 43 legs + live_paper bad=0 + smoke 49/49 + ack scan CLEAN 102/111/0 + D-19 NOOP hold + "
           "satengine ALIVE + orphan 0/16 + claws x2 + idle --worked 1->0; honest face = 0-point waiting-state "
           "guard round (wave supply = bm-c lane, boards drained, all other channels blocked/reserved)")

verify = ("orders_ack_scan CLEAN 102/111/0 + smoke 49/49 + S6 chain 43 rc0 bad=0 (results/_r1058bma_s6chain_rc.log) + "
          "D-19 read-back full-string equality (dec 4cfdd17c / ord 5d871243 NOOP) + orphan probe 0/16 + "
          "seat MSG-1407 processed-archive move asserted + watermark probe red=false healthy + idle --worked receipt 1->0")

artifact = ("_r1058bma_s6chain.ps1 + results/_r1058bma_s6chain_rc.log (gitignored local evidence per r1054 face) + "
            "results/_r1058bma_closeout.py + S6-derived same-day idempotent faces "
            "(docs/daily_report/REPORT-2026-10-18 + docs/live_usage/LIVE-2026-10-18 + results/strategy_scorecard.json + "
            "results/dashboard_status.json/js + results/token_usage.bm-a.json) + "
            "fleet/inbox/processed/MSG-20261018-1407-bmc-w269-seat.md")

ack_note = (R + ": fleet/orders zero new orders (orders_ack_scan CLEAN 102/111 zero divergence, closeout dual-scan same verdict); "
            "D-19 group face NOOP hold (dec 4cfdd17c / ord 5d871243, heartbeat mirrors synced 3); "
            "seat MSG-1407 consumed as fleet-wide informational (yield decision, zero bm-a obligation)")

notes_r1058 = (R + ": (1) W269 seat text supersedes r1057 next-face expectation: owner=bm-c 88th own wave "
               "(sixth consecutive bm-c own wave W264..W269), bm-a yields per fleet README sec.4 + seat-first law; "
               "W270 owner naming rides W269 sec.7/8 backfill, alternation observation stays a fleet-health face; "
               "(2) round-start S0 dirty-tree pull recipe: own live faces stash -> pull --rebase ff -> stash pop, "
               "watermark_red pop-UU resolved take-HEAD (origin=bm-c same-day fresher write of a derived probe face, "
               "r1028 newer-wins family; self probe re-derives in-round); "
               "(3) agenda census confirms waiting state: boards T/E drained (r1043 face held through r1058), "
               "backlog zero bm-a lines, satengine queue0 with wave supply on bm-c lane, all remaining "
               "EXTERNAL_IDEAS_CATALOG rows blocked (CEO physical / P1 signature / domain freeze) -- "
               "supply floor 0<3 gap = O-1645 standing structural supply decision face, GM/council domain; "
               "(4) watchdog S4U flip access-denied = carried C-20261016-04 (elevation window, physical CEO machine)")

# ---------- state ----------
sp = "state-bm-a.json"
with open(sp, "r", encoding="utf-8") as f:
    st = json.load(f)

prev_epoch = st.get("heartbeat_epoch_utc")
st["round"] = 1058
st["loop_round"] = 1058
st["round_no"] = 1059
st["round_no_label"] = R
st["last_round"] = R
st["last_round_label"] = R
st["last_round_at"] = now_iso
st["last_round_ts"] = now_iso
st["last_round_closed"] = now_iso
st["last_run"] = now_iso
st["last_action_at"] = now_iso
st["updated"] = now_iso
st["updated_at"] = now_iso
st["last_seen"] = now_iso
st["ts"] = now_iso
st["now_active"] = "bm-a loop " + R + " closeout (W269 seat guard round: consumed+yield, S6 all-green, zero skip-claim)"
st["current"] = did
st["did"] = did
st["task"] = did
st["last_action"] = did
st["current_task"] = cur_task
st["next"] = nxt
st["verdict"] = verdict
st["verify"] = verify
st["last_artifact"] = artifact
st["recent_artifact"] = artifact
st["latest_artifact"] = artifact
st["orders_ack_note"] = ack_note
st["notes_r1058"] = notes_r1058
st["heartbeat_epoch_utc"] = epoch
st["heartbeat_epoch_utc_type_int"] = True
st["last_heartbeat_epoch_utc"] = prev_epoch
st["last_orders_read_at"] = now_iso
st["last_decisions_read_at"] = now_iso
st["last_orders_seen"] = R + ": ord 5d871243 hold (D-19 NOOP zero-delta)"
st["last_decisions_seen"] = R + ": dec 4cfdd17c hold (D-19 NOOP zero-delta)"
st["last_orders_at"] = now_iso
st["last_decisions_at"] = now_iso
st["orphan_face"] = 0
st["orphan_faces"] = 0
st["next_milestone"] = ("W269 chain watch on bm-c lane (W270 naming rides sec.7/8 backfill, <=48h) + "
                        "MF blockade Monday adjudication <=10-19 + council sec.6 table <=10-20 12:00")

vm = psutil.virtual_memory()
st["ram_free_gb"] = round(vm.available / 1024**3, 1)
st["free_ram_gb"] = round(vm.available / 1024**3, 1)
st["idle_ram_gb"] = round(vm.available / 1024**3, 1)
st["ram_free_pct"] = round(vm.available * 100.0 / vm.total, 1)
st["free_ram_pct"] = round(vm.available * 100.0 / vm.total, 1)
st["ram_load_pct"] = round(100.0 - vm.available * 100.0 / vm.total, 1)
cpu = psutil.cpu_percent(interval=1)
st["cpu_load_pct"] = cpu
st["cpu_pct"] = cpu
st["cpu_total_pct"] = cpu
st["cpu_util_pct"] = cpu

with open(sp, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---------- heartbeat ----------
hp = "fleet/machines/bm-a.json"
with open(hp, "r", encoding="utf-8") as f:
    hb = json.load(f)

hb["machine_id"] = "bm-a"
hb["active"] = True
hb["health"] = "green"
hb["round"] = 1058
hb["loop_round"] = 1058
hb["round_no"] = 1059
hb["round_no_label"] = R
hb["last_round"] = R
hb["last_round_label"] = R
hb["last_round_at"] = now_iso
hb["last_round_closed"] = now_iso
hb["last_round_ts"] = now_iso
hb["last_run"] = now_iso
hb["last_action_at"] = now_iso
hb["updated"] = now_iso
hb["updated_at"] = now_iso
hb["last_seen"] = now_iso
hb["ts"] = now_iso
hb["clock_read"] = now_iso
hb["now_active"] = st["now_active"]
hb["current"] = R + ": W269 seat consumed owner=bm-c -> bm-a yields (fleet README sec.4); S6 43 legs + live_paper bad=0; smoke 49/49; ack scan CLEAN; D-19 NOOP hold; waiting-state guard round honest face"
hb["did"] = hb["current"]
hb["task"] = R + ": guard round (seat consume+yield + S6 all-green + self-heal + closeout)"
hb["last_action"] = hb["current"]
hb["current_task"] = cur_task
hb["next"] = nxt
hb["next_milestone"] = st["next_milestone"]
hb["verdict"] = verdict
hb["last_artifact"] = artifact
hb["recent_artifact"] = artifact
hb["latest_artifact"] = artifact
hb["orders_ack_note"] = ack_note
hb["last_orders_seen"] = st["last_orders_seen"]
hb["last_decisions_seen"] = st["last_decisions_seen"]
hb["last_orders_sha"] = st.get("last_orders_sha", "")
hb["last_decisions_sha"] = st.get("last_decisions_sha", "")
hb["last_orders_ts"] = st.get("last_orders_ts", now_iso)
hb["last_decisions_ts"] = st.get("last_decisions_ts", now_iso)
hb["last_orders_at"] = now_iso
hb["last_decisions_at"] = now_iso
hb["last_orders_read_at"] = now_iso
hb["last_decisions_read_at"] = now_iso
hb["last_heartbeat_epoch_utc"] = hb.get("heartbeat_epoch_utc", prev_epoch)
hb["heartbeat_epoch_utc"] = epoch
hb["heartbeat_epoch_utc_type_int"] = True
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["orphan_face"] = 0
hb["orphan_faces"] = 0
hb["ram_free_gb"] = st["ram_free_gb"]
hb["free_ram_gb"] = st["free_ram_gb"]
hb["idle_ram_gb"] = st["idle_ram_gb"]
hb["ram_free_mb"] = int(vm.available / 1024**2)
hb["idle_ram_mb"] = int(vm.available / 1024**2)
hb["ram_free_pct"] = st["ram_free_pct"]
hb["free_ram_pct"] = st["free_ram_pct"]
hb["ram_load_pct"] = st["ram_load_pct"]
hb["cpu_load_pct"] = cpu
hb["cpu_pct"] = cpu
hb["cpu_total_pct"] = cpu
hb["cpu_util_pct"] = cpu
hb["gpu_source_note"] = "idle_trigger face 2026-10-18 (CEO weekend machine, llm-mode resident honest)"

with open(hp, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
    f.write("\n")

# ---------- round report ----------
rp = "round_reports-bm-a.md"
line = (now_iso + " | " + R + " | 守门轮：S0 pull --rebase ff 3 commits（bm-c r1091 W268 全链收口+W269 seat publish）"
        "·轮首脏=own live faces stash/pull/pop（watermark_red pop-UU→取 HEAD 版=origin bm-c 14:07 更新·派生件 newer-wins 零损·本机探针轮中重derive）"
        "+orders_ack_scan CLEAN 102/111/0+D-19 update --advance NOOP hold（dec 4cfdd17c/ord 5d871243·mirrors synced 3）"
        "+orphan 0/16·W269 席位 MSG-1407 消费=owner bm-c 88th own wave→bm-a 让位 fleet README §4 零抢跑"
        "（r1057 next-face『点名 bm-a』假设被席位实文 superseded·零 W269 bm-a 产物在 origin 验毕）·件归档 processed"
        "·MSG-1200 留 inbox（致 bm-a 导演席 BigStream 车道 informational 零本 loop 义务）"
        "+议程清点=板面 T/E 全 done·job 空·backlog 无本机行·satengine ALIVE queue0（波供给=bm-c 车道）"
        "·E14 打板线 r874 关门确认·GATE-RECHECK-MP1 r870 收口确认·目录余项全堵（P4 点时因子=CEO 物理六件/QDII=P1 署名/期权=域冻结 2027-09）"
        "=诚实等待态守门轮（一行声明律·0 分如实）；S6 43 腿+live_paper rc0 bad=0（_r1058bma_s6chain.ps1=r1057 面 verbatim 克隆·MF 周日合法 no-op·周一 <=10-19 裁决 armed day-8..10 链）"
        "+smoke 49/49+loop pin=8 no-op+watchdog 重注册（S4U flip 拒=carried C-20261016-04）+双爪重装+idle --worked 1→0（basis=S6 管线+守门面·r1050 先例）"
        " | 证据=results/_r1058bma_s6chain_rc.log bad=0+orders_ack_scan CLEAN 回执+watermark_red.json probe face red=false healthy"
        "+seat MSG processed 归档断言+idle_trigger --worked 回执 | 本轮=守门轮 0 分如实（波链在飞=bm-c 车道·板空·余通道全堵/保留）"
        " | 下轮指针=r1059：W269 链观察（bm-c prereg→五面 splice→自燃→finalize·W270 owner 命名随 W269 sec.7/8 backfill）"
        "+MF 周一裁决 <=10-19（S6 重测补 day-11/12 证据）+委员会 §六 首轮裁决表 <=10-20 12:00"
        "+E20 三轴合壁=GM/委员会署名保留面（正门律）+S4U 提权窗 carried\n")
with open(rp, "a", encoding="utf-8") as f:
    f.write(line)

# ---------- self-verify ----------
for p in (sp, hp):
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    e = d.get("heartbeat_epoch_utc")
    assert isinstance(e, int) and not isinstance(e, bool), p + " epoch must be JSON int"
    assert "T" in d.get("clock_read", now_iso), p + " clock_read must be ISO T-sep"
with open(rp, "r", encoding="utf-8") as f:
    tail = f.read()[-200:]
assert R in tail, "round report append failed"
print("CLOSEOUT_OK", R, "epoch", epoch, "cpu", cpu, "ram_free_gb", st["ram_free_gb"])
