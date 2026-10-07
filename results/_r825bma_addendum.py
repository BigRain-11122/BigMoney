# -*- coding: utf-8 -*-
"""r825 bm-a closeout addendum: CODELY new-pit line + round-report postscript +
heartbeat refresh. One pit entry (four-gate law: long-term value / no
restatement / lesson-first / one-thing <=1.5KB)."""
import json
import time
import datetime

# --- CODELY.md new pit line (four-gate law pass) -----------------------------
pit = (
    "- [2026-10-07 14:3x r825 bm-a] **rebase UU 标记污染活 daemon 状态面=引擎假死坑（r825 收口实弹·当场治愈零数据伤）**："
    "git rebase 冲突窗把冲突标记写入工作树的饱和引擎状态三件（state/face/history_bm-a）→下一 1-min tick 读到标记态 JSON 解析崩"
    "→status 报 engine_alive:false（state unreadable）=假死面（真引擎任务未死·修复窗内 tick 空转数分钟）；"
    "正法=UU 面以双侧 stage blob deep-ts 取 freshest 完整侧立即落盘（本例 :2: origin 13:28:05 胜 local 13:25:05）"
    "→rebase 收口后引擎下一 tick 自愈（heartbeat_age 回落秒级·无需重注册）；"
    "连带律=活 daemon 机的 rebase 冲突集含 daemon 活面时=最高优先解面（每分钟 tick 都在空转烧窗）·禁拖到收口后才解。"
    "How to apply：daemon 机 rebase 撞 UU 先扫状态面文件有无标记（grep '<<<<<<<'）·有则 stage blob 取新立即覆写·收口后必验 status 活性三面。"
)
with open("CODELY.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(pit + "\n")
print("CODELY pit line appended")

# --- round report postscript --------------------------------------------------
ps = (
    "\n| 2026-10-07 14:4x | r825 postscript (bm-a) | close-push-race resolve ledger: push behind-10 (bm-b r803 wave + autofill keepalives same-window burst) -> churn absorb -> pull --rebase 11-UU -> "
    "_r825bma_close_resolver.py 分域解（席位件 O-1157 回执 union=三机回执齐/bm-b 同窗填 bm-b 行实证零丢失；池面 claim-refresh 竞态=W14-SCREEN bm-b@13:22:36 vs 陈旧 bm-c@13:16:08+FUND-DIVLOWVOL bm-b@13:22:08 vs @13:08:08 双差异 max-merge 取 origin 侧·id 集 404/404 恒等断言后整侧取·r474/r311 律；7 快照面 deep-ts 本机 13:20-13:21 全胜 origin 13:08-13:13；compute_audit/token_usage 双子 canon resolve）"
    " -> rebase continue 假拒（EDITOR env 跨 shell 失活·r659 面）commit --no-edit 收口 r799 前例 -> 末 pick 撞自家 saturation 三活面 UU=标记污染引擎状态面（引擎假死窗·新坑律已入 CODELY r825 行）freshest stage blob 侧立即落盘引擎 tick 自愈（heartbeat 104s 实证·零重注册）"
    " -> push LANDED 468cfacf9..56fa4edc4 behind-0/ahead-0 -> r376 同窗 reconcile token_usage ZERO-DRIFT 首过+compute_audit DRIFT=单行 13:07:48 lane 在场共享缺席（D-03 全 diff 过闸=仅 history 一键差异·state 键恒等）sync_face settle 幂等补 207 行 -> reconcile 双面 ZERO-DRIFT"
    " -> smoke 复验 48/48（rebase 手术后全绿）。交付=56fa4edc4（W174 prereg+全收口面）·本地未达 origin commit 数=0（fetch 双向复核）。 | [r825 bm-a]"
)
with open("logs/iteration-loop/round_reports-bm-a.md", "a", encoding="utf-8", newline="\n") as f:
    f.write(ps + "\n")
print("round report postscript appended")

# --- heartbeat refresh ---------------------------------------------------------
now = datetime.datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S") + now.strftime("%z")[:3] + ":" + now.strftime("%z")[3:]
hp = "fleet/machines/bm-a.json"
hb = json.load(open(hp, encoding="utf-8"))
hb["last_seen"] = iso
hb["heartbeat_epoch_utc"] = int(time.time())
hb["clock_read"] = iso
hb["ts"] = iso
hb["current_task"] = "r825 closed (W174 prereg delivered 56fa4edc4); W174 freeze chain next window (two-window law)"
json.dump(hb, open(hp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
chk = json.load(open(hp, encoding="utf-8"))
assert isinstance(chk["heartbeat_epoch_utc"], int) and "T" in chk["clock_read"]
print("heartbeat refreshed (epoch int + T-sep verified)")
