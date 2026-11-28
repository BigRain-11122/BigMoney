"""r2209 close-out: append the round row, bump state, refresh heartbeat.

Written as a script (not an inline format string) because r2208's row landed as
an unformatted template -- the exact defect this round repaired. Every literal
here is single-line on purpose: this round also repaired a file that never
parsed because a string literal was left open.
"""
import io
import json
import time
import datetime as dt

ROUND = 2209
NOW = dt.datetime.now().astimezone()
STAMP = NOW.isoformat(timespec="seconds")

ROW = "".join([
    "| " + STAMP + " | 2209 | ",
    "本轮主产出=修两个「自己说自己坏」的实缺陷（不是新面）：",
    "①`Tools/_r820bmc_close.py` 自提交起不可解析（L130 字符串未闭合）→ 补两枚引号后 py_compile rc=0，",
    "并重 derive `import_git_coverage` 面：`committed files that cannot be parsed: 1 broken → 0 broken`",
    "（面原文 EVERY_IMPORTED_MODULE_AND_EVERY_NAMED_LEG_IS_IN_GIT，2953 文件 / 21055 imports / 3569 边，",
    "imports missing in git: 0，链名脚本 345 全在盘全在 git）——清掉 r2200/r2203 挂了两轮的 repair-or-retire 欠账；",
    "②`round_reports-bm-c.md` L2895（r2208 那行）是没被格式化的模板，字面 `| %s | %d |` 加 `%%` → 就地代入 ",
    "2026-11-28T08:06+08:00 / 2208 并还原 `%`，正文一字未改、残留 %s 与 %% 双 False。",
    "| 验证：py_compile rc=0（修前 SyntaxError L130）·treasure_guard prescan rc=0 零命中·",
    "rg 证明无任何代码 import 该文件·import_git_coverage run rc=0 且 0 broken·轮报行 L2895 修后自检双干净 ",
    "| 水印红牌=false lane=healthy；decisions.md origin blob 250,586B sha 79e3083b85c1 == 自持水位（零新决策）；",
    "orders.md 115,550B sha 9ff2f31c4d38 与上轮同（零新增涉本司行）；fleet/orders 119 文件 vs 心跳 ack 337 → 未回执 0；",
    "fleet/inbox 空；board open=0；孤儿面=0（py_faces=6 orphans=0 resident_servers=2）；",
    "竞争探针 rc=0 CLEAN（results/_repo_write_contention.bm-c.json，单宿主 pid=24212）；",
    "本地未达 origin commit 数=0。",
    "**在飞链占共享面（如实）**：pid 33880 `python -u Tools\\s6_chain_bmc.py 2209` 09:04:54 起、",
    "round=2209 已 leg_done 106/415，非零腿仅 capital_marginal_road rc=3；当前腿 ",
    "`etf_book_pre2020.py refresh` 09:20:49 起 21 分钟、8 秒采样 CPU +7.98s=活性正常非死锁 → ",
    "按 r1907 同树多宿主律本轮不重跑链、不抢共享面，故**不宣称红数下降**；",
    "`live_book_section_bars` check=CHECK_OK verdict=PAGE_MIXES_BARS headline=2026-11-27 off=36 unknown=4，",
    "其中 lag=1 的 30 节由在飞链负责（etf_book_spanning 已被它刷到 11-27 实证）。",
    "CEO 三行：当前活=收两枚实缺陷 + 让出共享面给在飞全链 | 最近实物=results/import_git_coverage.json（0 broken）与 ",
    "round_reports-bm-c.md L2895 修好 | 下个里程碑=等全链落地后复核 36 节代差是否闭合并复跑全量冒烟拿真实红数，窗 ≤48h ",
    "| QA qa/fix-broken-close-script-r2209.md",
])

P_RPT = "round_reports-bm-c.md"
s = io.open(P_RPT, encoding="utf-8", newline="").read()
crlf = "\r\n" in s
if not s.endswith("\n"):
    s += "\r\n" if crlf else "\n"
s += ROW + ("\r\n" if crlf else "\n")
io.open(P_RPT, "w", encoding="utf-8", newline="").write(s)
print("round report row appended")

sot = json.load(io.open("state-bm-c.json", encoding="utf-8"))
sot["round_no"] = ROUND
sot["last_round_no"] = ROUND
sot["last_round_at"] = STAMP
sot["last_round_summary"] = (
    "r2209: repaired two faces that named their own defect -- Tools/_r820bmc_close.py never parsed "
    "(L130 open string) and the r2208 round-report row was an unformatted template. import_git_coverage "
    "re-derived: 0 broken (was 1). Full S6 chain was already flying on this tree (pid 33880, leg 106/415), "
    "so no shared face was re-run and no red-count reduction is claimed."
)
sot["last_verdict"] = "A_FILE_THAT_NEVER_PARSED_IS_NOW_PARSEABLE"
sot["last_face"] = "results/import_git_coverage.json"
sot["contention_r2209"] = {
    "probe": "Tools/repo_write_contention.py --lookback-min 45",
    "rc": 0,
    "verdict": "CLEAN",
    "why": "fewer than two codely hosts alive",
    "policy": "chain already in flight from 09:04:54 -> only new files + the two named repairs; no chain re-run",
    "evidence": "results/_repo_write_contention.bm-c.json",
}
sot["s6_note_r2209"] = (
    "S6 NOT run by this round: a detached full chain (pid 33880) started 09:04:54 and owns the shared faces. "
    "Progress: results/_s6chain_progress.bm-c.jsonl round=2209, leg_done=106/415, only non-zero leg = "
    "capital_marginal_road rc=3. Current leg etf_book_pre2020.py refresh alive (CPU +7.98s per 8s sample)."
)
sot["smoke_note_r2209"] = (
    "full smoke NOT run (~950s) and the chain is still writing shared faces; previous snapshot (07:18) is not "
    "evidence of the current red count -- no reduction claimed."
)
sot["carrier_debt_r2209"] = (
    "paid: repair-or-retire of Tools/_r820bmc_close.py (carried since r2200/r2203) and the unformatted r2208 report "
    "row. still owed: live_book_section_bars 36-section drift (waits for the flying chain to land), full smoke, and "
    "the S4U re-register of Bigmoney-LoopWatchdog (physical item, needs elevation)."
)
sot["记账_r2209"] = "轮报告1 + QA1 + results(修复脚本2)2 + state1 + 心跳1 = 5 处（记账律内·S6 产物不计）"
sot["下个里程碑_r2209"] = (
    "等 pid 33880 全链落地后：复核 36 节代差是否闭合（live_book_section_bars 应回到 off≈0）+ 复跑全量冒烟拿真实红数，窗 ≤48h"
)
io.open("state-bm-c.json", "w", encoding="utf-8", newline="\n").write(
    json.dumps(sot, ensure_ascii=False, indent=1) + "\n")
print("state bumped to", ROUND)

HP = "fleet/machines/bm-c.json"
hb = json.load(io.open(HP, encoding="utf-8"))
epoch = int(time.time())
hb.update({
    "machine_id": "bm-c",
    "last_seen": STAMP,
    "ts": STAMP,
    "clock_read": STAMP,
    "heartbeat_epoch_utc": epoch,
    "round_no": ROUND,
    "round": ROUND,
    "current_task": "r2209 收口：两枚实缺陷已修（不可解析文件 + 未格式化轮报行）",
    "当前活": "收两枚实缺陷 + 把共享面让给在飞全链",
    "最近实物": "results/import_git_coverage.json（0 broken，原 1）+ round_reports-bm-c.md L2895 修好",
    "下个里程碑": "全链落地后复核 36 节代差 + 复跑全量冒烟（≤48h）",
    "CEO 三行": "当前活=收两枚实缺陷让出共享面｜最近实物=import_git_coverage 0 broken｜下个里程碑=链落地后复核代差+冒烟（≤48h）",
    "ram_free_gb": 28.1,
    "cpu_cores": 32,
    "gpu_free_vram_mib": 14259,
    "gpu_total_vram_mib": 16384,
    "idle_rounds": 0,
    "agenda_starved": False,
    "verdict": "A_FILE_THAT_NEVER_PARSED_IS_NOW_PARSEABLE",
    "orphans": 0,
    "py_faces": 6,
    "local_unreached_commits": 0,
    "竞争_r2209": "CLEAN（单宿主 pid=24212）",
    "chain_in_flight": "pid 33880 s6_chain_bmc.py 2209 since 09:04:54, leg 106/415",
})
io.open(HP, "w", encoding="utf-8", newline="\n").write(
    json.dumps(hb, ensure_ascii=False, indent=1) + "\n")
hb2 = json.load(io.open(HP, encoding="utf-8"))
assert isinstance(hb2["heartbeat_epoch_utc"], int), "epoch must be int"
print("heartbeat written, epoch int OK =", hb2["heartbeat_epoch_utc"])
