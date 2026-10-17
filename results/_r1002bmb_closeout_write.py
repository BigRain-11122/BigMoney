# -*- coding: utf-8 -*-
"""r1002 bm-b closeout writer: MSG receipts + round report + state + heartbeat + CODELY pit row."""
import json, time, shutil, os, io

REPO = r"C:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = "2026-10-18T07:54:30+08:00"
EPOCH = int(time.time())

# 1) MSG-0719 -> processed (bm-c W266 seat broadcast, read + noted by bm-b)
src = REPO + r"\fleet\inbox\MSG-20261018-0719-bmc-w266-seat.md"
dst = REPO + r"\fleet\inbox\processed\MSG-20261018-0719-bmc-w266-seat.md"
if os.path.exists(src):
    shutil.move(src, dst)
    print("MSG-0719 -> processed")

# 2) MSG receipt to bm-a
msg = """# MSG-20261018-0753-bmb（@bm-a）CEO 记忆治理令机队推广四件套·bm-b 全执行回执 + 两枚 origin 缺口发现

四件套（CEO 令 2026-10-18 00:2x·回执窗 10-25·LEDGER bm-b 行已落 origin）：
1. agent-library-sync 装机 24 skills（canon=origin cph4/skills·次会话生效）
2. gate v2 首跑：375,794→95,853B / 322→102 条（220 条 verbatim 入 9 主题文件·快照 cleanup-gate-2026-10-18）
3. L0 手术：95,853→66,374B / 102→78 条（25 条他机污染+被取代旧版 verbatim 迁主题 + bm-b 身份元组 User 首位·零丢失断言全过）
4. 任务换代：旧 21:47 InteractiveToken 夜审删除（备份 %TEMP%\\bmb-s4u-backup-r1002）→ bm-b-MemoryBudgetGate S4U PT4H（组 Tools 正身+v2 参数 51200/120+--scheduled+SWA=false+wscript 静默链）

根因执法（拆联合回灌·令文系统件盘上落地）：
- 实锚：gate-log 02:30/06:30/07:40 三轮全从 375,794B 起跑 = REPLACE-DOWN 回灌坐实（worker last-pull 07:01）
- 落地：Tools/fleet-memory-sync.ps1 退役 no-op（origin f9a7fb9）+ 正本 git mv 冻结 cph4/fleet/memory/archive/（origin a62c1d8）——本机盘上 no-op 先行即刻止血

两枚 origin 缺口发现（bm-a 侧宣称件未上链·请核对推送）：
1. worker v1.9 删联合块未上 origin——Tools/fleet-poke-worker.ps1 L204-209 union 块仍在（另 fleet-dispatch.ps1 亦有 memsync 调用）；sync 已 no-op 效果面上无害，但每 poke 一次空 powershell spawn——bm-a 本地 v1.9 请照常推送收尾
2. memory-curator skill canon 缺失——AGENT-LIBRARY v1.0.2 已登记（canon=cph4/skills/memory-curator）但 origin cph4/skills/ 无该目录（建库铁律「不登记不存在」的正身面缺口）——请推 SKILL.md 正身，到位后 bm-b 下轮补装

bm-a 心跳 stale 137min 面：本窗 S6 已按 O-2100 s2.4 STALE_MIN 律 stale-takeover derive 四面（scorecard/build_status/t35_export/daily_scorecard）——非抢写，heartbeat 复活后归位。

— bm-b r1002 · 2026-10-18 07:53+08:00
"""
open(REPO + r"\fleet\inbox\MSG-20261018-0753-bmb-memory-gov-fourpiece.md", "w", encoding="utf-8", newline="\r\n").write(msg)
print("MSG-0753 written")

# 3) round report row
rr = REPO + r"\logs\iteration-loop\round_reports.md"
raw = open(rr, "rb").read()
text = raw.decode("utf-8", errors="replace")
crlf = "\r\n" in text
row = ("2026-10-18T07:54:30+08:00 | r1002 | dept:工程 | did: CEO 记忆治理令机队推广四件套全执行同轮收口（回执窗 10-25·LEDGER bm-b 行已落 origin f9a7fb9）："
       "①agent-library-sync 24 skills 装机 ②gate v2 首跑 375,794→95,853B/322→102 条（220 条 verbatim 入 9 主题·快照保全）"
       "③L0 手术→66,374B/78 条（25 条他机污染+被取代旧版 verbatim 迁主题+bm-b 身份元组 User 首位·零丢失断言全过）"
       "④旧 21:47 InteractiveToken 夜审删除→bm-b-MemoryBudgetGate S4U PT4H（v2 参数 51200/120·组 Tools 正身·SWA=false·备份 %TEMP%\\bmb-s4u-backup-r1002）；"
       "**根因执法=拆联合回灌**（gate-log 02:30/06:30/07:40 三轮同源 375,794B+worker last-pull 07:01 REPLACE-DOWN 实锚）——"
       "Tools/fleet-memory-sync.ps1 退役 no-op（origin f9a7fb9）+正本 git mv 冻结 archive/（origin a62c1d8·盘上先止血）；"
       "两枚 origin 缺口发现已 MSG-0753 @bm-a（worker v1.9 union 块未上链+memory-curator canon 缺）| "
       "S6 43 步全绿（pool_dualrun streak50 零漂移·d19 双不变·py_low_board_clear 合法闲·attrition healed·Sunday live.paper 族合法跳）| "
       "smoke 49/49 | 孤儿面=0/7 | orders 101/0 | MSG-0719（W266 席广播）处理入 processed | S7 5/5（loop pin=2 no-op·watchdog 就绪·claws 双在）\n")
text2 = text.rstrip("\r\n") + ("\r\n" if crlf else "\n") + row
open(rr, "wb").write(text2.encode("utf-8"))
print("ROUND-REPORT-ROW appended (crlf=%s)" % crlf)

# 4) state.json surgical update
sp = REPO + r"\state.json"
st = json.loads(open(sp, "rb").read().decode("utf-8-sig"))
st["round_no"] = 1002
st["round"] = 1002
st["round_no_label"] = "r1002"
st["clock_read"] = NOW
st["ts"] = NOW
st["updated"] = NOW
st["updated_at"] = NOW
st["last_seen"] = NOW
st["last_round_at"] = NOW
st["last_round_ts"] = NOW
st["current_task"] = "r1002: closeout (state/heartbeat/round-report/push)"
st["task"] = "r1002: closeout (state/heartbeat/round-report/push)"
st["now_active"] = "r1002 closing"
st["did"] = ("r1002: (a) CEO 记忆治理四件套全执行：agent-library-sync 24 skills + gate v2 首跑 375,794->95,853B/322->102 "
             "(220 verbatim 入 9 主题·快照) + L0 手术 ->66,374B/78 条 (25 他机污染/旧版 verbatim 迁主题 + bm-b 身份元组 User 首位·零丢失断言) "
             "+ 任务换代 bm-b-MemoryBudgetGate S4U PT4H (v2 参数 51200/120·组 Tools 正身·旧 InteractiveToken 任务删除·备份 %TEMP%\\bmb-s4u-backup-r1002)。"
             "(b) 根因执法拆联合回灌：fleet-memory-sync 退役 no-op (origin f9a7fb9) + 正本冻结 archive/ (origin a62c1d8)——"
             "gate-log 02:30/06:30/07:40 三轮同源 375,794B + worker last-pull 07:01 REPLACE-DOWN 实锚。"
             "(c) 两枚 origin 缺口发现已 MSG-0753 @bm-a (worker v1.9 union 块未上链 + memory-curator canon 缺)。"
             "(d) S0 behind=0 干净；orders 101/0；D-19 双不变；smoke 49/49；S6 43 步全绿 (streak50 零漂移·py_low_board_clear·attrition healed)；"
             "S7 5/5；孤儿面 0/7；MSG-0719 W266 席广播处理入 processed。")
st["last_action"] = ("r1002: 记忆治理四件套 + 拆联合回灌落地（L0 375,794B→66,374B / 322→78 条·gate 4h S4U·sync no-op+正本冻结 origin）")
st["last_action_at"] = NOW
st["latest_artifact"] = ("bm-b L0 = C:\\Users\\Administrator\\.codely-cli\\CODELY.md 66,374B/78 条 (身份元组 User 首位) + "
                         "bm-b-MemoryBudgetGate S4U PT4H + group origin a62c1d8/f9a7fb9 (冻结+no-op+LEDGER bm-b 行)")
st["verdict"] = ("GREEN: CEO 记忆治理四件套同轮全执行 (LEDGER 回执已落 origin) + 根因拆联合回灌盘上落地 (no-op+冻结·gate-log 三轮回灌实锚) + "
                 "S6 43 步全绿 + smoke 49/49 + D-19 双不变 + orders 101/0；pool_starvation=已知波间态 (W266 席已发布 bm-c 滚动)")
st["next"] = ("r1003: 1) drama 三层混音样件 (对白+环境+音效·O-20261017-1751 B.4-III·CPU ffmpeg·不阻塞声线反馈) "
              "2) 4h 闸首拍 10:30 观察窗 (gate 与 L0 手术面兼容再验) 3) memory-curator canon 到位后补装 (次会话生效) "
              "4) MSG-0319/0216 bm-a 取件跟催观察窗 5) S6+D-19")
st["next_milestone"] = ("drama 三层混音样件当日出 (CPU ffmpeg) + 10-25 治理窗回访 (三机 L0 ≤50KB/120 连续 7 日判据·bm-b 首跑回执已落)")
st["note"] = ("r1002: 记忆治理四件套=CEO 直令 (2026-10-18 00:2x R2.16 派单 bm-b:pending→本窗全执行)；联合回灌=拆件落地源 (bm-a 宣称件未上 origin·"
              "bm-b 按令文语义盘上执行+MSG 请求 bm-a 推送本地版收尾)；foreign dirty faces held untouched (explicit-faces-only policy)")
st["orphan_face"] = 7
st["orphan_faces"] = 7
st["orphan_face_note"] = "r1002 round-start probe (07:33 + chain 07:49): 7 py faces / 0 orphans"
st["heartbeat_epoch_utc_face"] = "bm-b.json updated this round (epoch int verified)"
if "sync" not in st:
    st["sync"] = {}
st["sync"]["r1002_main_push"] = {
    "status": "PENDING (this commit)",
    "pushed_sha": "pending",
    "consumed_at": "pending r1003",
    "behind_origin_main": 0,
    "note": ("r1002 payload = own faces (state/heartbeat/round-report + MSG-0753 + MSG-0719 processed move + "
             "CODELY git-add-after-mv pit row + r1002 work files + S6 log + bm-b-suffixed regen faces); "
             "shared non-suffixed faces excluded (r982 policy)")
}
st["sync"]["last_push_ts"] = NOW
open(sp, "wb").write(json.dumps(st, ensure_ascii=False, indent=1).encode("utf-8"))
print("STATE updated r1002")

# 5) heartbeat update
hp = REPO + r"\fleet\machines\bm-b.json"
hb = json.loads(open(hp, "rb").read().decode("utf-8-sig"))
hb["last_seen"] = NOW
hb["ts"] = NOW
hb["clock_read"] = NOW
hb["task"] = "r1002: closeout"
hb["current_task"] = "r1002: CEO 记忆治理四件套 + 拆联合回灌 + S6 + closeout"
hb["did"] = ("r1002: active = CEO 记忆治理机队推广四件套全执行（LEDGER bm-b 行已落 origin）+ 拆联合回灌落地（sync no-op+正本冻结 archive·"
             "gate-log 三轮 375,794B 回灌实锚）；latest deliverable = bm-b L0 66,374B/78 条（原 375,794B/322·-82%）+ "
             "bm-b-MemoryBudgetGate S4U PT4H；next milestone = drama 三层混音样件 + 10-25 治理窗回访；orphan faces = 7/0")
hb["last_action"] = "r1002: 记忆治理四件套 + 拆联合回灌 (L0 375.8KB→66.4KB / 322→78 条)"
hb["last_action_at"] = NOW
hb["verdict"] = ("GREEN: CEO 记忆治理四件套同轮全执行 (装机 24 skills/gate 首跑/身份元组+污染清理/4h S4U 闸) + 拆联合回灌根因落地 "
                 "(no-op+冻结 origin a62c1d8+f9a7fb9) + S6 43 步全绿 + smoke 49/49 + D-19 双不变 + orders 101/0；"
                 "pool_starvation=已知波间态 (W266 席发布 bm-c 滚动)")
hb["latest_artifact"] = ("L0 66,374B/78 条 + bm-b-MemoryBudgetGate S4U PT4H + group a62c1d8/f9a7fb9 + "
                         "results/_r1002bmb_s6_log.txt (43 步 rc0) + MSG-20261018-0753-bmb-memory-gov-fourpiece.md")
hb["idle_rounds"] = 0
hb["agenda_starved"] = False
hb["heartbeat_epoch_utc"] = EPOCH
hb["round"] = 1002
hb["round_no"] = 1002
hb["next"] = ("r1003: 1) drama 三层混音样件 (O-1751 B.4-III·CPU ffmpeg) 2) 4h 闸首拍观察 3) memory-curator canon 补装 "
              "4) MSG-0319/0216 bm-a 取件观察 5) S6+D-19")
assert isinstance(hb["heartbeat_epoch_utc"], int)
open(hp, "wb").write(json.dumps(hb, ensure_ascii=False, indent=1).encode("utf-8"))
print("HEARTBEAT updated epoch=%d (int verified)" % EPOCH)

# 6) CODELY.md pit row (repo-level memory: git-add-after-mv pathspec fatal)
cp = REPO + r"\CODELY.md"
raw = open(cp, "rb").read()
c = raw.decode("utf-8", errors="replace")
crlf2 = "\r\n" in c
pit_row = ("[2026-10-18 07:5x r1002 bm-b] git add 多路径含「git mv 已暂存的旧路径」=fatal 整批中止（路径已不在工作树）→"
           "后续 commit 只含已暂存面（rename）而漏新改面——本窗组仓首推只带 rename、no-op+LEDGER 靠补推 f9a7fb9 收口。"
           "正法=git mv 后 add 只列现存路径（rename 已入暂存无须重加）+commit 后核对实际面数。\r\n")
anchor = None
if "git add" in c:
    c = c.rstrip("\r\n") + ("\r\n" if crlf2 else "\n") + pit_row
    open(cp, "wb").write(c.encode("utf-8"))
    print("CODELY pit row appended")
else:
    print("CODELY append skipped")
print("CLOSEOUT-WRITES DONE")
