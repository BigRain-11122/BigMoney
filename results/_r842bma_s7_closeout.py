# -*- coding: utf-8 -*-
"""r842 bm-a S7 closeout writes: round report line + state-bm-a.json +
heartbeat fleet/machines/bm-a.json. Fresh read-modify-write per multi-writer
law; epoch as JSON int; clock_read ISO8601 with T separator."""
import datetime
import io
import json
import time

now = datetime.datetime.now().astimezone().isoformat(timespec="seconds")
epoch = int(time.time())
assert "T" in now and now[-6] in "+-" , now

# --- 1. round report line (append, CRLF tail convention) -------------------
P = r"round_reports-bm-a.md"
t = io.open(P, encoding="utf-8", newline="").read()
assert t.endswith("\r\n")
assert "round 842" not in t, "r842 line already present"
LINE = (
    now + " | round 842 (bm-a, dept:研究+工程/舰队) | "
    "[watermark verdict: 绿 red=false·py 低位=假期窗合法 idle 白名单面（板全闭环·W177 已坐席·零在飞烧批·satengine alive rc0 queue0 idle·孤儿面=0）] | "
    "当前活: W177 prereg 构建窗完成（三窗律 r797/r799 第二窗：席位 r841→prereg r842→freeze 下窗）| "
    "最近实物: research/PERPETUAL_N1_W177_PREREG.md 20,840B/63 行（buildgen r833 血统·DRY 门 50/50 一次全过·"
    "A 404_204..406_203 阶梯 37th E36/B 406_204..406_403 own-A 保留·锚头 793,105·K 385,120+2,200=387,320 投影·"
    "席位 780a0cd30·freeze sha 15ec44ea6 机读锚全）+ r835-r841 七行账本补记（state r840 假引用补正）+ "
    "CODELY mini-increment（3 指针行迁域件 verbatim+新坑条 S5 账本丢失坑·主件 30,474B margin 246B·prescan rc3 披露）| "
    "下个里程碑: W177 freeze 5-face 窗（下一轮 r843·≤48h）+ 10-08 复市数据链重挂 | "
    "S6 27/27 rc0（dualrun streak 51 零漂移·假期 no-op 族合法 cutoff 2026-09-30·无新 bar→live.paper 族跳过）·"
    "S7 quartet 绿（IterLoop pin=8 no-op·Watchdog 活·双爪 OK）·attrition CLEAN·令差集零未回执·"
    "决策水位 4c32527b 恒等零动作·本地未达 origin commit 数=0（commit 后自证）"
)
t2 = t + LINE + "\r\n"
io.open(P, "w", encoding="utf-8", newline="").write(t2)
chk = io.open(P, encoding="utf-8", newline="").read()
assert chk == t2 and chk.count("round 842") == 1

# --- 2. state-bm-a.json -----------------------------------------------------
SP = r"state-bm-a.json"
st = json.load(io.open(SP, encoding="utf-8"))
st["round_no"] = 842
st["round"] = 842
st["last_round"] = "r842"
st["loop_round"] = "r842"
st["current_task"] = "W177 prereg built (r842, DRY 50/50); next = W177 FREEZE 5-face window then 10-08 reopen data chain re-arm"
st["did"] = ("r842: W177 per-wave prereg build window complete (three-window law 2nd window) -- "
             "research/PERPETUAL_N1_W177_PREREG.md built from W176 freeze-time blob 15ec44ea6 via buildgen "
             "r833 bloodline (AST BACK176/EXPECT x50, DRY full-file gate one-pass, S77 fact map: "
             "A 404_204..406_203 staircase 37th E36 / B 406_204..406_403 own-A reservation, anchor 793,105, "
             "K 385,120+2,200=387,320 proj, seat 780a0cd30); r835-r841 seven ledger lines backfilled "
             "(state r840 false report-line reference corrected); CODELY mini-increment (3 pointer lines "
             "verbatim out + 1 new pit in, main 30,474B margin 246B); S6 27/27 rc0; S7 quartet green")
st["last_action"] = ("W177 prereg build: A 404_204..406_203 (37th E36) / B 406_204..406_403 own-A; "
                     "ledger anchor 793,105 machine-read; K proj 387,320; prereg 63 lines CRLF")
st["last_round_at"] = now
st["last_round_ts"] = now
st["last_run"] = now
st["updated"] = now
st["ts"] = now
st["clock_read"] = now
st["next"] = ("W177 FREEZE window (next round r843): five-face insertion (pf N1_BANDS[177] row "
             "a=404_204..406_203/b_exit=406_204..406_403 + n1 WAVE_CONFIGS[177] + W177 materializer + "
             "PASS-claim) per r834 bloodline + banned-gate re-verify + tick self-ignite; then 10-08 "
             "market-reopen data chain re-arm (first trading day after golden week), window <=48h")
st["verify"] = ("buildgen DRY gate 50/50 one-pass (TOK counts+residue-zero+malformed-window CLEAN+r754 two-form); "
                "prereg spot-verify 37th/THIRTY-SEVENTH+seat 780a0cd30+freeze 15ec44ea6+K/p95/sigma/se_mu all "
                "machine-read; ledger backfill +7 lines (splitlines 1622->1629); CODELY increment receipt "
                "_r842bma_codely_increment.json; smoke 48/48; S6 27/27 rc0; dualrun ZERO-DRIFT streak 51; "
                "attrition CLEAN; quartet green; orphan face=0")
st["now_active"] = "W177 prereg built r842; FREEZE window next"
st["latest_artifact"] = "research/PERPETUAL_N1_W177_PREREG.md @" + now
io.open(SP, "w", encoding="utf-8", newline="\n").write(
    json.dumps(st, ensure_ascii=False, indent=1))

# --- 3. heartbeat -----------------------------------------------------------
HP = r"fleet\machines\bm-a.json"
hb = json.load(io.open(HP, encoding="utf-8"))
hb["last_seen"] = now
hb["ts"] = now
hb["clock_read"] = now
hb["heartbeat_epoch_utc"] = epoch
hb["current_task"] = st["current_task"]
hb["current"] = "W177 prereg built r842 (freeze next window)"
hb["verdict"] = "green"
io.open(HP, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1))

# --- self-verify ------------------------------------------------------------
h2 = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(h2["heartbeat_epoch_utc"], int), "epoch must be JSON int"
assert "T" in h2["clock_read"], h2["clock_read"]
s2 = json.load(io.open(SP, encoding="utf-8"))
assert s2["round_no"] == 842
print("S7 writes OK @", now, "epoch", epoch)
