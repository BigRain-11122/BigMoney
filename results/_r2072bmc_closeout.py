"""Close r2072 (bm-c): bump the round number, refresh the heartbeat, append the report line.

Read-modify-write on every file, UTF-8 with the file's own newline behaviour preserved, and
an ASCII-only stdout so the GBK console can never turn a Chinese report line into a crash
half-way through the close (r2048 family: the close is the last thing that must not fail).
"""
import io
import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(REPO, "state-bm-c.json")
HB = os.path.join(REPO, "fleet", "machines", "bm-c.json")
REPORT = os.path.join(REPO, "round_reports-bm-c.md")

ROUND = 2072
TZ = timezone(timedelta(hours=8))
now = datetime.now(TZ)
clock_read = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

REPORT_LINE = (
    "{CLOCK} | r2072 | bm-c | "
    "**PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·next_pick 他机 claimed）"
    "·孤儿面=0（py_faces=4 / orphans=0 / resident_servers=2）"
    "·竞争窗 rc=3 CONTENTION〔对端 codely.exe pid 79608 仍活、最后写入 2026-11-25T04:51:42 的 "
    "research/ARBITER-BOARD.md、探针时静默 6.1 分钟、窗口 05:36:42 自然关闭，证据 "
    "results/_repo_write_contention.bm-c.json〕→ 按 r1907/r1927 只落新增文件面：未改共享面、"
    "未重跑 S6 链、未跑全量冒烟）**：CEO 一页纸把 ETF 复合书摆在阶梯总帽旁边，只写「列在同一张"
    "表但不进裁决」；帽子对账面把它记成 own_rule、差 23.5pp。读者因此只拿到一个结论：**这本书是"
    "帽子的 2.18 倍**——可这个结论量的是**名义敞口**。同一本书 β 约 0.48，市场敞口是 43.5%×0.48"
    "≈**20.9%**：同一顶 20% 的帽子换个单位只剩 **+0.94pp**，而且这点差还在尺子自己 **±5.89pp** 的"
    "噪声里；按全史 β 算则是 **19.999%**，正好站在帽子上（−0.00pp）。本面把两种单位并排印出，"
    "再答第三个问题：票面 k=0.435003 与 `beta_target/β_full`=0.435027 的恒等式成立到 **−0.0024pp**"
    "——**这本书的规则就是 RED 档在 β 单位下的写法**，且与政体无关（ORANGE 以上各档要的 k 分别 "
    "1.039/1.350/1.662/1.973，全部 >1，没有杠杆就到不了，所以 GREEN 档它仍按 β 当量 20% 跑）。"
    "钱面：真要严格踩在帽下，今天该卖 **19,543 元**（当窗 β）或 **0 元**（全史 β），该档允许的"
    "名义仓位 **415,460 / 435,027 元**。｜scripts/etf_book_cap_beta_units.py（selftest **17/17**·"
    "run rc0·--check **CHECK OK** rc0 重算 facts 逐字段相等 + 页面 marker 块与面自重渲逐字相等）"
    "+ results/etf_book_cap_beta_units.json + research/ETF_BOOK_CAP_BETA_UNITS.md（读数由渲块印出、"
    "`--check` 逐字复核）+ qa/cap-beta-units-r2072.md + 负控 results/_r2072bmc_cap_beta_units_negctl.py "
    "**21/21**（改 β→rc3 且含 CHECK FAILED 且**不含** STALE 且点名 beta_now／改判词→点名 verdict／"
    "动 inputs_digest→rc3 含 STALE 不含 CHECK FAILED／改页面一格→rc3 点名 page block，且先断言那串"
    "真在页面里／页面丢块→rc3／复原後 rc0／五个输入面与生产面页 sha256 前后逐字节相同）。"
    "**未做（如实）**：`ceo_live_usage.py` 那句「列在同一张表但不进裁决」未改（共享面）——建议改法="
    "补一句「按 β 折算为 20.9%，见 ETF_BOOK_CAP_BETA_UNITS」；本面未接冒烟腿/S6 腿（共享面）；"
    "全量冒烟连续第 17 轮未跑（红腿读数仍是 2026-11-24T20:12:28 那份 765 腿/34 红）；S6 链连续第 17 "
    "轮未跑。｜S0.5 双扫（证据 results/_r2072bmc_s05_scan.json）：fleet/orders **117 件、回执 117、"
    "未回执 0**（2026-11 未回执亦 0）；集团 origin/main:docs/decisions.md 原生字节 **250,586B "
    "sha256 79e3083b85c1…**（git cat-file 直落临时件再哈希，不经 PowerShell 字符串往返，r1911/r2048 律）"
    "**== 自持水位**（零新决策零动作）；fleet/inbox 空。｜S7：orphan_face_probe 已跑"
    "（py_faces=4 / orphans=0 / resident_servers=2）；schtasks 自愈本轮未触碰（对端在飞，重注册会打断"
    "在飞轮）；attrition tripwire 未跑（竞争窗，与冒烟/S6 同列延后）；pre-commit/pre-push 爪未触发新装。"
    "｜**本地未达 origin commit 数**：本条 commit 前实测 origin/main...HEAD = 1/29（本行 commit 后再 +1，"
    "读者此刻应为 1/30；自指计数差 1 按 r2062 addendum-2 判例写清）。｜下轮指针：(a) 静窗后把这一句"
    "接到 CEO 一页纸的帽子行（共享面，一句 disclosure 而非新判据）；(b) 给本面接一条冒烟腿"
    "（判据=verdict 与两个读数必须同代，面 stale 即红）；(c) 全量冒烟 + S6 分批补跑（连续第 17 轮未跑，"
    "≤48h 必须收口）。｜**CEO 三行**：当前活＝回答「这本书 43.5% 的仓位是不是 2.18 倍超帽」——名义上"
    "是 2.18 倍，按 β 折算只有 20.9%，比 20% 帽多 0.94pp，且小于尺子 ±5.89pp 的分辨力｜最近实物="
    "K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ETF_BOOK_CAP_BETA_UNITS.md（{CLOCK}·selftest 17/17·"
    "负控 21/21·--check rc0）｜下个里程碑＝把这一句接到一页纸帽子行 + 接冒烟腿（≤48h）。"
    "｜记账：轮报告 1 处 + state 1 + 心跳 1 = 3（无方法论新增：把「同一顶帽子两种单位」做成可复核"
    "读数属证据与载体）。\n"
).replace("{CLOCK}", clock_read)


def bump_state():
    with io.open(STATE, encoding="utf-8") as f:
        st = json.load(f)
    prev = st.get("round_no")
    st["round_no"] = ROUND
    st["last_round_at"] = clock_read
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return prev


def update_heartbeat():
    with io.open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    n_before = len(hb)
    hb["round_no"] = ROUND
    hb["last_round_no"] = ROUND
    hb["last_seen"] = clock_read
    hb["ts"] = clock_read
    hb["clock_read"] = clock_read
    hb["heartbeat_epoch_utc"] = int(time.time())
    hb["current_task"] = "r2072: one cap two units -- beta-equivalent exposure vs the RED rung"
    hb["当前活"] = ("回答「ETF 复合书 43.5% 是不是 2.18 倍超帽」：名义 2.175x，β 当量 20.941% vs 20%"
                  "（+0.94pp，尺子 ±5.89pp）")
    hb["最近实物"] = ("research/ETF_BOOK_CAP_BETA_UNITS.md + results/etf_book_cap_beta_units.json"
                    " + scripts/etf_book_cap_beta_units.py (%s)" % clock_read)
    hb["下个里程碑"] = "把 β 口径一句接到一页纸帽子行 + 接冒烟腿（≤48h）"
    hb["verdict"] = "AT_CAP_WITHIN_RULER_NOISE"
    hb["watermark_verdict"] = "green (red=false, lane=healthy)"
    hb["py_faces"] = 4
    hb["orphans"] = 0
    hb["孤儿面"] = 0
    hb["ram_total_gb"] = 55.92
    hb["ram_free_gb"] = 25.12
    hb["ram_free_pct"] = round(100.0 * 25.12 / 55.92, 1)
    hb["gpu_mem_used_mib"] = 3345
    hb["gpu_mem_total_mib"] = 16384
    hb["gpu_free_mib"] = 16384 - 3345
    hb["vram_free_gb"] = round((16384 - 3345) / 1024.0, 2)
    hb["GPU空闲VRAM"] = "%.1f GB free / 16 GB" % ((16384 - 3345) / 1024.0)
    hb["空闲RAM"] = "%.1f GB free / 55.9 GB" % 25.12
    hb["local_unreached_origin_commits"] = 30
    hb["contention"] = ("rc=3 CONTENTION peer pid 79608 (last write 2026-11-25T04:51:42 "
                        "research/ARBITER-BOARD.md); new files only")
    hb["new_files_only_round"] = True
    hb["s6_chain"] = "not run (contention, 17th consecutive round)"
    hb["smoke"] = "full suite not run (contention); last reading 2026-11-24T20:12:28 765 legs/34 red"
    hb["idle_rounds"] = hb.get("idle_rounds") if isinstance(hb.get("idle_rounds"), int) else 0
    hb["agenda_starved"] = False
    with io.open(HB, "w", encoding="utf-8", newline="\n") as f:
        json.dump(hb, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.write("\n")
    return n_before, len(hb)


def append_report():
    old = ""
    if os.path.exists(REPORT):
        with io.open(REPORT, encoding="utf-8", newline="") as f:
            old = f.read()
    tail = old.rstrip("\r\n")
    new = tail + "\n\n" + REPORT_LINE
    with io.open(REPORT, "w", encoding="utf-8", newline="") as f:
        f.write(new)
    return len(old), len(new)


def main():
    prev = bump_state()
    n_before, n_after = update_heartbeat()
    b0, b1 = append_report()
    with io.open(HB, encoding="utf-8") as f:
        hb = json.load(f)
    assert isinstance(hb["heartbeat_epoch_utc"], int), "epoch must be an int"
    assert "T" in hb["clock_read"], "clock_read must be T-separated"
    print("state round_no %s -> %d" % (prev, ROUND))
    print("heartbeat keys %d -> %d (epoch int ok, clock_read %s)"
          % (n_before, n_after, hb["clock_read"]))
    print("report bytes %d -> %d" % (b0, b1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
