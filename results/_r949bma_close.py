"""r949 bm-a closeout: state round_no advance + heartbeat + round report line.
Fresh read-modify-write in one process (multi-writer law). ASCII-safe script body.
"""
import json
import os
import time
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "state-bm-a.json")
HB = os.path.join(ROOT, "fleet", "machines", "bm-a.json")
RR = os.path.join(ROOT, "round_reports-bm-a.md")

now = datetime.now().astimezone()
ts = now.isoformat(timespec="seconds")
epoch = int(time.time())

VERDICT = ("green (r949: E6 P3 head consumed verdict-closed negative = microcap closed-family gate "
           "adjudication digest + queue flip + tech T18 gate seed; S6 32 legs rc0 paper-legs legally "
           "skipped no-new-bar; smoke 49/49; dualrun streak 7; DEC/ORD UNCHANGED zero re-consume; "
           "compute_audit FLAG supply_gap+ignition_sla on bm-c W17 -> MSG sent; push 0/0)")

st = json.load(open(STATE, encoding="utf-8"))
st["round_no"] = st.get("round_no", 948) + 1
st["round"] = 949
st["clock_read"] = ts
st["ts"] = ts
st["updated"] = ts
st["updated_at"] = ts
st["last_round"] = 948
st["last_round_closed"] = ts
st["last_round_at"] = ts
st["last_run"] = ts
st["last_seen"] = ts
st["verdict"] = VERDICT
st["did"] = ("r949: E6 microcap closed-family adjudication (digest + explore E6 closed line + tech T18 "
             "queue-seed gate) + S6 32 legs rc0 + S0 lane-sync absorb x2 rebase onto bm-b r825/826 + "
             "W205 watch held (W204 prereg frozen 1422ad767 but five-face row unregistered, no first-burn)")
st["current_task"] = ("r950: E7 P3 head (industry-rotation ETF grid-family candidate scan) + W205 watch "
                      "(W204 five-face/first-burn gate) + W17 ignition-sla reply watch (MSG sent to bm-c)")
st["now_active"] = st["current_task"]
st["next"] = st["current_task"]
st["task"] = st["current_task"]
st["last_artifact"] = ("research/digests/DIGEST-20261010-e6-microcap-closed-adjudication.md + "
                       "state/queue/explore.md E6 closed line + state/queue/tech.md T18 seed (09:4x)")
st["latest_artifact"] = st["last_artifact"]
st["next_milestone"] = ("r950: E7 industry-rotation ETF grid candidate scan; W205 seat after W204 "
                        "first-burn; PARKING-P1 closed; moneyflow IC batch parked on source-blocked panel")
st["orphan_faces"] = 1
st["last_orders_seen"] = "r949 scans zero unacked (60 files vs 199 ack, S0.5+S7 double-scan, ORD 0ddb01d9 unchanged)"
st["last_decisions_seen"] = "r949 scan hash b87a92b1 MATCH (D-20261010-01/02/03 already consumed r933); zero new group face"
st["idle_rounds"] = 0
st["agenda_starved"] = False
st["heartbeat_epoch_utc"] = epoch
st["last_heartbeat_epoch_utc"] = epoch
with open(STATE, "w", encoding="utf-8", newline="") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)

# heartbeat
hb = json.load(open(HB, encoding="utf-8"))
hb["last_seen"] = ts
hb["ts"] = ts
hb["updated"] = ts
hb["clock_read"] = ts
hb["heartbeat_epoch_utc"] = epoch
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["cpu_cores"] = 32
hb["ram_free_gb"] = round(__import__("psutil").virtual_memory().available / (1024**3), 1) if False else hb.get("cpu_cores", 32) and None or None
hb["verdict"] = VERDICT
hb["current_task"] = ("当前活: r949 E6 微盘闭合族裁定收口交付（P3 队头消费）+ S6 32 腿全绿；下轮 r950=E7 行业轮动 ETF 网格族扫描 + W205 watch")
hb["last_artifact"] = ("最近实物: research/digests/DIGEST-20261010-e6-microcap-closed-adjudication.md + "
                       "state/queue/explore.md E6 closed + state/queue/tech.md T18 gate seed @ " + ts)
hb["next_milestone"] = ("下个里程碑: r950 E7 P3 队头消费（行业轮动 ETF 网格族候选·48h 窗内）+ W205 席位（W204 首烧门）")
with open(HB, "w", encoding="utf-8", newline="") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)

# round report line
line = ("{ts} | r949 | bm-a | dept:研究 (P3 queue head consumption + N1 supply watch) | WM-VERDICT: green "
        "(red=false; engine ALIVE rc0 idle; DEC b87a92b1 UNCHANGED zero re-consume; ORD 0ddb01d9 UNCHANGED; "
        "py_low_board_clear = legal idle whitelist: board closed, pool ready all bm-c-lane W17, bandit "
        "next_pick moneyflow-IC parked source-blocked) | 孤儿面=1 (read-only probe) | 本地未达 origin commit 数=0 "
        "(pre-push) | E6 P3 队头判负收口出列：主面+副面双撞 CLOSED_FAMILIES #6 microcap_2024_crash "
        "(O-20260926-0926 集团令·复活门=CEO 一句话唯一·r822 队列消费律首步法核) -> digest "
        "research/digests/DIGEST-20261010-e6-microcap-closed-adjudication.md + explore.md E6 行翻 closed + "
        "tech T18 queue-seed 闭合族机检闸候选 (E6 建面晚于关面=陈旧面同型·治理教训) | W205 watch held: "
        "W203 finalize r938 verified in-file (results/perpetual_faces/n1_w203_results.json) + W204 prereg "
        "frozen by bm-c 1422ad767 BUT five-face band row unregistered in perpetual_faces_n1.py + no "
        "first-burn (bm-c engine queue 0) -> seat gate not met | S6 32 legs rc0: dualrun ZERO-DRIFT streak 7 "
        "/ compute_audit FLAG supply_gap+ignition_sla (W17 bm-c lane ready-unignited 35.5h streak -> MSG-"
        "20261010-0935-bma-bmc-W17-IGNITION-SLA sent) / paper legs legally skipped (no new bar, export asof "
        "2026-10-09 == panel cutoff) / lhb zt heat futures repo options moneyflow sina_mf ths ah fundprem "
        "fundamental fundstat all honest no-op rc0 | S0: pre+pre2 daemon-faces absorb (own lane) + rebase "
        "onto bm-b r825/826 (fd5a4e2b2) clean zero-UU, push c4fe07a59 0/0 verified | S7: self-heal 4/4 "
        "(loop pin=8/watchdog/precommit/prepush), attrition guard CLEAN, orders double-scan 60/199 zero "
        "unacked | smoke 49/49 | 下轮指针: r950 E7 行业轮动 ETF 网格族候选扫描（grid_paper 族先例）+ "
        "W204 first-burn watch -> W205 seat decision").format(ts=ts)
with open(RR, "a", encoding="utf-8", newline="") as f:
    f.write(line + "\n")

# verify epoch int type
st2 = json.load(open(STATE, encoding="utf-8"))
hb2 = json.load(open(HB, encoding="utf-8"))
assert isinstance(st2["heartbeat_epoch_utc"], int), "state epoch must be int"
assert isinstance(hb2["heartbeat_epoch_utc"], int), "hb epoch must be int"
assert "T" in hb2["clock_read"] and "+" in hb2["clock_read"], "clock_read must be ISO8601 T-form"
print("closeout ok: round_no=%d epoch=%d clock=%s" % (st2["round_no"], st2["heartbeat_epoch_utc"], hb2["clock_read"]))
