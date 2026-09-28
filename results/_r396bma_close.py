# r396 bm-a: state round_no 396 + heartbeat refresh (epoch int, T-separated clock)
import json
import time
import datetime as dt

now_local = dt.datetime.now().astimezone()
now_iso = now_local.isoformat(timespec="seconds")
now_ts = now_local.strftime("%Y-%m-%d %H:%M:%S")

# state-bm-a.json
with open("state-bm-a.json", encoding="utf-8") as fh:
    st = json.load(fh)
st["round_no"] = 396
st["round"] = 396
st["loop_round"] = 396
st["did"] = ("R396: TRIAL_LABOR_W4 prereg 冻结轮（T-98 claim-and-start 同轮）：外源扫描先行（Wikipedia 低波异象 90y 链+仓内三源交叉验+"
             "Moreira-Muir 未验证宣称律）→VOL 门探针（3483 行/calm 1523 wild 1441/七极端日全 wild/2014-12-31 wild∧bull 非同构）→"
             "七元组语法 32,256 轴组合（R/X/S/T/STOP/GATE/VOL）新 sha16 合法开法→排除簿七源+G-VOL 门+judge 序门（bm-b r369 瓶颈裁定采纳="
             "W4-JUDGE 排 RAM 门后）→SEED_REGISTRY 三键同 commit（R250）selftest 37/37→冻结 commit 3aec0868 push FAST")
st["verify"] = ("smoke 25/25 + science_gates selftest 37/37 + reconcile 14 faces ZERO-DRIFT + S6 33 legs rc=0 零掩盖 + "
                "IntradayMarks 09:25 首拍 PASS（result 0·pre-open no-op 合法·09:35 起 capture）+ post_review 15 NO 全历史翻 YES 零 P0 + "
                "orders 99/99 双扫零未回执 + claw IDENTICAL + pin=8 no-op + CODELY 10,238B<=10KB")
st["next"] = ("r397 候选=runner scripts/trial_labor_w4.py build（import w1/w2/w3/mass+VOL overlay+selftest 含 vol 因果腿/双门交叠腿/G-VOL 锚腿/"
              "vol=none==W3 基线恒等腿）→池条目 TRIAL-LABOR-W4-GENERATE；W3-JUDGE=bm-b RAM 门后串行（bma 二机验证位）；"
              "IntradayMarks 09:35 起 marks capture watch+15:30 首 bar 全链接力（T-91 s3·sysv1 首 SIG=bm-b BARS 晚间）；下轮 5x=R400 HANDOVER")
st["last_round_at"] = now_iso
st["current_task"] = "r396 closed: W4 prereg frozen+pushed (T-98); next = W4 runner build + judge burn watch"
st["updated"] = now_iso
st["last_round_ts"] = now_iso
st["ts"] = now_ts
with open("state-bm-a.json", "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)

# heartbeat bm-a
epoch = int(time.time())
with open("fleet/machines/bm-a.json", encoding="utf-8") as fh:
    hb = json.load(fh)
hb["machine_id"] = "bm-a"
hb["last_seen"] = now_ts
hb["current_task"] = ("R396 done: TRIAL_LABOR_W4 prereg FROZEN+pushed (T-98 claim-and-start; VOL axis seven-tuple 32,256 combos; "
                      "bm-b r369 ruling disposition = W4-JUDGE sequenced behind RAM r354 in-flight judge faces) + IntradayMarks 09:25 first-fire PASS "
                      "(pre-open legal no-op) + S6 33 legs rc=0 + CODELY recompile batch-42 10,238B<=10KB")
hb["cpu_cores"] = 32
hb["cpu_pct"] = 8.0
hb["free_ram_gb"] = 42.9
hb["gpu_free_vram_gb"] = 5.5
hb["verdict"] = ("py_low_board_clear legal idle (board closed 0 open; W4 prereg frozen = next-wave prep zero-latency for RAM window; "
                 "pool 1 ready W2B census bm-b lane guard; judge faces waiting = bmb flip executor serial + RAM r354; "
                 "IntradayMarks armed 09:25 first-fire PASS, marks capture from 09:35 tick)")
hb["heartbeat_epoch_utc"] = epoch
hb["clock_read"] = now_iso
hb["round_no"] = 396
hb["round"] = 396
hb["loop_round"] = 396
with open("fleet/machines/bm-a.json", "w", encoding="utf-8") as fh:
    json.dump(hb, fh, ensure_ascii=False, indent=1)

# orders_ack: verify all O-*.md acked (no new orders this round)
import os, glob
orders = [os.path.basename(p) for p in glob.glob("fleet/orders/O-*.md")]
unacked = [o for o in orders if o not in hb.get("orders_ack", [])]
assert not unacked, f"unacked orders: {unacked}"

# self-proof: epoch int + clock T-separated
assert isinstance(json.load(open("fleet/machines/bm-a.json", encoding="utf-8"))["heartbeat_epoch_utc"], int)
assert "T" in hb["clock_read"] and "+" in hb["clock_read"]
print("state 396 + heartbeat OK; epoch:", epoch, "clock:", now_iso, "; orders unacked:", len(unacked))
