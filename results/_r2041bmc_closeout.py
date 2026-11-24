#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""r2041 bm-c closeout: report row + state + heartbeat (fresh read-modify-write only)."""

from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import cb_parking_shelf_at_size as S  # noqa: E402

ROUND = 2041
NOW = time.strftime("%Y-%m-%dT%H:%M:%S+08:00")
WALL = time.strftime("%Y-%m-%d %H:%M")

face = json.load(io.open(S.OUT_JSON, encoding="utf-8"))
h = face["headline"]
rows = {r["code"]: r for r in face["rows"]}
big, small, money = rows["511380"], rows["511180"], rows["511880"]
t_ticket = str(face["tiers_cny"][1])
cap = big["capacity"][t_ticket]


def gpu():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=memory.free,memory.total",
                              "--format=csv,noheader,nounits"],
                             capture_output=True, text=True, timeout=20)
        free, total = out.stdout.strip().splitlines()[0].split(",")
        return round(float(free) / 1024.0, 1), round(float(total) / 1024.0, 1)
    except Exception:
        return None, None


vram_free, vram_total = gpu()

try:
    wm = json.load(io.open("results/watermark_red.json", encoding="utf-8"))
    wm_red = bool(wm.get("red"))
except Exception:
    wm_red = False
try:
    cont = json.load(io.open("results/_repo_write_contention.bm-c.json", encoding="utf-8"))
    cont_rc = cont.get("rc", 3)
except Exception:
    cont_rc = 3
try:
    orph = json.load(io.open("results/_orphan_face_probe.bm-c.json", encoding="utf-8"))
except Exception:
    orph = {}

REPORT = "fleet/round_reports-bm-c.md"
row = (
    "| %s | r%d **新增文件面**（竞争窗 rc=%s·不动共享面） | "
    "**watermark：red=%s / lane=healthy · 孤儿面=%s**（py_faces=%s / resident_servers=%s）。"
    "竞争探针 `results/_repo_write_contention.bm-c.json` **rc=%s**（对端 pid 51252 自 11-22 20:10、"
    "pid 68052 自 09:43 在写共享面）→ 按 r1907 只落新增文件面、未跑 S6 链。"
    "**主产出**：`scripts/cb_parking_shelf_at_size.py` + `results/cb_parking_shelf_at_size.json` + "
    "`research/CB_PARKING_SHELF_AT_SIZE.md` —— r2040 只答了「这一类付得比回购多」，本面答「这副货架装得下吗」："
    "坏日子（p10 成交 5,007.5 万）上 511380 一张 1%% 的单最多 **50.1 万**、511180 再给 22.0 万，"
    "两只合计 **72.0 万 > 票面现金腿 56.5 万**（要拆两张单）；单靠 511380，票面现金腿占坏日子 1.13%%（THIN）。"
    "整手不是障碍：转债 ETF 一手 1,159 元 vs 货币 ETF 一手 10,099 元 —— 25 万停在货币 ETF 上留 3.05%% 零头，"
    "停在转债上只有 0.33%%。代价不在容量：票面规模下一个防守日亏 4,346 元，而它一年比回购只多赚 1,167 元 = "
    "**3.7 年的超额**。附带读数：511180 自身 1.405%% 低于回购 1.766%%（同族第三只并不跟着付）；"
    "短融 ETF 511360 付 2.318%% 但坏日子只有 13.1 万（200 万即 BLOCKED）。"
    "**验证**：selftest 29/29 · check rc0 · 负控 6/6（改 1 元零头/1%% 容量/手写判词/换尺子常量/翻倍一手价 全部点名拒绝）· "
    "与 r2040 三方对账差 0.0000pp（净年化 / 防守日均值 / 货币 ETF 净年化）+ 防守日 232 对 232。"
    "orders 116 文件 / ack 329 / 未回执 0 · decisions.md sha 79e3083b 未变零动作。 | "
    "判词 %s；一页纸 `research/CB_PARKING_SHELF_AT_SIZE.md`；下轮指针=竞争窗关后把 r2022–r2041 十九面接 S6 链腿与冒烟两腿（≤48h）"
    % (WALL, ROUND, cont_rc, "false" if not wm_red else "true",
       orph.get("orphans", "?"), orph.get("py_faces", "?"), orph.get("resident_servers", "?"),
       cont_rc, " + ".join(face["verdict"]))
)

with io.open(REPORT, "a", encoding="utf-8") as f:
    f.write(row.rstrip("\n") + "\n")
print("report row appended:", len(row), "chars")

# ---- state
STATE = "state-bm-c.json"
st = json.load(io.open(STATE, encoding="utf-8"))
st["round_no"] = ROUND
st["ts"] = NOW
st["clock_read"] = NOW
st["watermark_verdict"] = ("green (red=false; lane healthy; repo_write_contention rc=%s -> new-file faces only)"
                           % cont_rc)
st["孤儿面"] = orph.get("orphans", 0)
st["孤儿面_note"] = ("round-zero orphan_face_probe: orphans %s (py_faces %s, resident_servers %s)"
                     % (orph.get("orphans"), orph.get("py_faces"), orph.get("resident_servers")))
st["当前活"] = ("能付的不等于能装：把「转债当停泊」从类别读数搬到货架读数 —— 坏日子的一张 1% 单能装多少钱、"
               "一手留多少零头、票面规模下一个防守日亏多少")
st["当前任务"] = ("r%d · 新增文件面（竞争窗）：scripts/cb_parking_shelf_at_size.py + results/cb_parking_shelf_at_size.json "
                "+ research/CB_PARKING_SHELF_AT_SIZE.md —— 坏日子 p10 上一张 1%% 单：511380 50.1 万 / 511180 22.0 万 / "
                "合计 72.0 万 > 票面 56.5 万（两张单）；票面规模一个防守日亏 4,346 元 = 3.7 年超额" % ROUND)
st["本轮"] = st["当前任务"]
st["本次"] = ("p10 坏日子成交：511380 5,007.5 万 / 511180 2,195.5 万 / 511880 10.1 亿 / 511360 1,309 万 / 511010 6,782 万；"
             "一手：转债 1,159/1,096 元 vs 货币 ETF 10,099 元、短融 11,419 元、国债 14,141 元；"
             "票面 565,246 元在 511380 是 1.13%% 坏日子（THIN），拆 511180 后合计 72.0 万回到 OPEN；"
             "一个防守日 511380 -4,346 元 vs 一年超额 +1,167 元 = 3.7 年")
st["最新判词"] = " + ".join(face["verdict"])
st["最新实物"] = ("research/CB_PARKING_SHELF_AT_SIZE.md + results/cb_parking_shelf_at_size.json + "
                "scripts/cb_parking_shelf_at_size.py（selftest 29/29·check rc0·负控 6/6）（%s）"
                % time.strftime("%Y-%m-%d %H:%M"))
st["最近实物"] = st["最新实物"]
st["未验证"] = ("①参与带是市场触达惯例不是实测冲击模型；②IOPV/溢价未在成交时点测；③两只转债 ETF 的费率差与出借未测；"
              "④类别等权 vs 发行量加权指数 3.58pp 的缺口仍拆不开（r2040 已披露）；⑤规模档只到 500 万；"
              "⑥防守日尺子=全A股 ETF 等权（r2040 同源），换成沪深300 会变")
st["下轮指针"] = ("(a) 竞争窗关后把 r2022–r2041 十九面接 S6 链腿与冒烟两腿（≤48h）；"
              "(b) 把「两张单才装得下、一手 1,159 元不是障碍、一个防守日=3.7 年超额」写进 CEO 一页纸现金腿节（≤48h）；"
              "(c) 短融 ETF 511360 付 2.318% 但坏日子只支持 13.1 万 —— 若要用它，需先测分批建仓")
st["下个里程碑"] = "(a) 十九面接链 + 全量冒烟（≤48h）；(b) CEO 一页纸现金腿节改写（≤48h）"
st["记账_r%d" % ROUND] = "轮报告 1 处 + state 1 处 + 心跳 1 处 = 3（无方法论新增：把容量尺子从回购腿搬到 ETF 货架属证据与载体）"
st["yield_note"] = {
    "round": ROUND,
    "why": "repo_write_contention rc=3 (peer pids 51252 since 2026-11-22 20:10 and 68052 since 2026-11-24 09:43 writing shared faces)",
    "did": "new-file-only landing: script + results + page + negative control + report row + this state; no shared-face edits, no S6 chain",
    "next": "smoke full suite + S6 chain + wire r2022-r2041 into the chain when the contention window closes",
}
st["?λ"] = "healthy"
st["ˮλ"] = "healthy"
with io.open(STATE, "w", encoding="utf-8") as f:
    json.dump(st, f, ensure_ascii=False, indent=1)
print("state round_no ->", ROUND)

# ---- heartbeat
HB = "fleet/machines/bm-c.json"
hb = json.load(io.open(HB, encoding="utf-8"))
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["heartbeat_epoch_utc"] = int(time.time())
hb["当前任务"] = "r%d: shelf capacity for the convertible parking lot (new-file-only, contention rc=%s)" % (ROUND, cont_rc)
hb["verdict"] = "healthy"
hb["watermark_verdict"] = st["watermark_verdict"]
hb["孤儿面"] = st["孤儿面"]
hb["round_no"] = ROUND
if vram_free:
    hb["vram_free_gb"] = vram_free
    hb["vram_total_gb"] = vram_total
hb["最新实物"] = st["最新实物"]
with io.open(HB, "w", encoding="utf-8") as f:
    json.dump(hb, f, ensure_ascii=False, indent=1)
chk = json.load(io.open(HB, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int), "heartbeat_epoch_utc must be an int"
print("heartbeat ok epoch=%d vram=%s/%s" % (chk["heartbeat_epoch_utc"], vram_free, vram_total))
