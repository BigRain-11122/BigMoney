"""r2073 closeout: append the round-report line and update state-bm-c.json.

Kept as a file so the exact text that landed is auditable (r2062 addendum precedent).
Only the keys listed here are touched; the other 1,490-odd keys stay byte-identical in value.
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REPORT = os.path.join(REPO, "round_reports-bm-c.md")
STATE = os.path.join(REPO, "state-bm-c.json")

TS = "2026-11-25T05:23:54+08:00"

LINE = (
    "2026-11-25T05:23:54+08:00 | r2073 | bm-c | "
    "**PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·next_pick 他机 claimed）·"
    "孤儿面=0（py_faces=4 / orphans=0 / resident_servers=2）·竞争窗 rc=3 CONTENTION"
    "〔对端 codely.exe pid 79608 自 2026-11-24T22:39 起、20s CPU 0.12s=挂起非在算、"
    "最后写入 2026-11-25T05:11:42 的 research/ARBITER-BOARD.md、HEAD=round 2072 于 05:08:43 提交，"
    "证据 results/_repo_write_contention.bm-c.json〕→ 按 r1907/r1927 只落新增文件面："
    "未改共享面、未重跑 S6 链、未跑全量冒烟、未改心跳面（对端 05:10:04 刚写））**："
    "上一面把「这本书是帽子的 2.18 倍」换算成 β 单位后停在「要卖 19,543 元」这句话上——"
    "可「元」不是能下单的东西，也没人算过照着它做要付多少钱。本面补两件："
    "①**整手**：五名等权按同百分比减，159519 卖 23 / 159655 卖 21 / 510760 卖 32 / 512040 卖 33 / 513690 卖 35 = **144 手 = 19,537.70 元**，"
    "残差 **−5.33 元（净值 −0.53bp）**，小于最大一手 189.80 元 → 可落；"
    "②**价钱**：8bp/边下单边 15.63 元、往返 **31.27 元**（占差额 0.16%）——成本不是问题，"
    "问题是差额 19,543.03 元 **小于**尺子噪声带 58,920.00 元（±5.89pp），"
    "判词 `TRIM_IS_INSIDE_THE_RULER`＝为噪声付钱；"
    "③**跟随的课税**：沿 β 面自己的 69 窗路径（2021-04-09→2026-11-19）逐窗读，24 窗（34.78%）超帽、连续 2 段、"
    "累计超额敞口 2,582,212.80 元，严格跟随的往返税 **4,131.54 元**（≈NAV 0.41%）——"
    "买到的不是收益，是「每窗都不超帽」这个属性。**自捕两枚**："
    "(a) 自检当场抓出我把「β 更高」写成「不超帽」，实际 β 越高→允许仓位越低→越超帽（边界 β≤cap/k_now≈0.4598 才在帽内）；"
    "(b) 路径段把今天的仓位当常量套到历史 β 上是**反事实**，首版页面没说，已在正文与 caveats 双处披露「这是尺子灵敏度刻度，不是历史敞口记录」。"
    "| 证据：scripts/etf_book_cap_trim_toll.py（selftest **20/20**·run rc0·--check **CHECK OK** rc0）+ "
    "results/etf_book_cap_trim_toll.json + research/ETF_BOOK_CAP_TRIM_TOLL.md（marker 块逐字复核）+ "
    "qa/cap-trim-toll-r2073.md + 负控 results/_r2073bmc_cap_trim_toll_negctl.py **7/7 PASS**"
    "（改一元→rc3 含 CHECK FAILED 不含 STALE 且点名 `toll.round_trip_cny`／动 inputs_digest→STALE／"
    "改页面块→点名 page block／删收尾 marker→rc3／删面→STALE face missing／复原 rc0 且两输入面 sha256 恒等）。"
    "| 未做（如实）：`ceo_live_usage.py` 帽子行未接（共享面）；本面未接冒烟腿/S6 腿（共享面）；"
    "全量冒烟连续第 18 轮未跑（红腿读数仍是 2026-11-24T20:12:28 的 765 腿/34 红）；S6 链连续第 18 轮未跑；"
    "心跳面由对端 05:10 写过，本窗不覆盖。"
    "| S0.5 双扫：fleet/orders **117 件**（与 r2069/r2072 同数）、fleet/inbox 空；"
    "集团 origin/main:docs/decisions.md 原生字节 **250,586B sha256 79e3083b85c130b8…**（git cat-file 直落再哈希，"
    "不经 PS 字符串往返）**== 自持水位** → 零新决策零动作。"
    "| S7：orphan_face_probe 已跑（py_faces=4 / orphans=0 / resident_servers=2）；"
    "schtasks 自愈未触碰（对端在飞，重注册会打断）；attrition tripwire 未跑（竞争窗，与冒烟/S6 同列延后）。"
    "| **本地未达 origin commit 数**：本轮 commit 前实测 origin/main…HEAD = 1/30（本行 commit 后再 +1；"
    "自指计数差 1 按 r2062 addendum-2 判例）。"
    "| 下轮指针：(a) 静窗后把「往返税 4,131.54 元 vs 差额在噪声内」接进 CEO 一页纸帽子行（共享面）；"
    "(b) 给本面接一条冒烟腿（verdict 与 facts 必须同代）；(c) 全量冒烟 + S6 分批补跑（连续第 18 轮）。"
    "| **CEO 三行**：当前活＝回答「照着『该卖 19,543 元』做，落到手上是哪几笔、要花多少」——"
    "144 手实得 19,537.70 元、残差 5.33 元、往返 31.27 元，而这笔差额比尺子自己的噪声还小｜"
    "最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\ETF_BOOK_CAP_TRIM_TOLL.md（2026-11-25T05:23·selftest 20/20·负控 7/7·--check rc0）｜"
    "下个里程碑＝接 CEO 一页纸帽子行 + 接冒烟腿（≤48h）。"
    "| 记账：轮报告 1 处 + state 1 处 = 2（心跳面由对端写、本窗不改；无方法论新增：把「元」做成整手与往返税两条可复核读数属证据与载体）。\n"
)

STATE_UPDATES = {
    "round_no": 2073,
    "activity": "product",
    "activity_now": (
        "r2073 · 新增文件面（竞争窗 r1907/r1927）：把「该卖 19,543 元」落到整手与价钱——"
        "144 手=19,537.70 元、残差 −5.33 元（−0.53bp）、往返 31.27 元；"
        "而沿 β 面 69 窗逐窗跟随累计往返税 4,131.54 元，买的是「每窗都不超帽」不是收益"
    ),
    "activity_now_round": 2073,
    "当前任务": (
        "r2073 · 新增文件面（竞争窗 rc=3）：上一面停在「要卖 19,543 元」，但「元」不是能下单的东西。"
        "本面答两件：①五名等权按同百分比减，159519 23 / 159655 21 / 510760 32 / 512040 33 / 513690 35 = 144 手 = "
        "19,537.70 元，残差 −5.33 元（−0.53bp）小于最大一手 189.80 元 → 可落；②8bp/边单边 15.63 元、往返 31.27 元，"
        "只占差额 0.16%——成本不是问题，问题是差额 19,543.03 元 < 尺子噪声带 58,920.00 元（±5.89pp）。"
        "再加第三问：沿 β 面 69 窗路径逐窗读，24 窗超帽、2 段、累计敞口 2,582,212.80 元，严格跟随往返税 4,131.54 元（≈NAV 0.41%）。"
    ),
    "当前活": "把「该卖 19,543 元」从这里变成 144 手与 31.27 元，并证明严格跟随帽子的年税是 4,131 元而换来的只是「不超帽」",
    "最新判词": "TRIM_IS_INSIDE_THE_RULER / CAP_BINDS_SOME_WINDOWS",
    "最新实物": "research/ETF_BOOK_CAP_TRIM_TOLL.md + results/etf_book_cap_trim_toll.json @2026-11-25T05:23:54+08:00",
    "最近实物": "scripts/etf_book_cap_trim_toll.py（selftest 20/20 · --check rc0 · 负控 7/7）+ research/ETF_BOOK_CAP_TRIM_TOLL.md",
    "最近实物_update": "results/etf_book_cap_trim_toll.json @2026-11-25T05:23:54+08:00",
    "未验证_r2073": (
        "①整手表按 2026-11-24 收盘价算术，真实成交同时改手数与现金腿；"
        "②路径段把今天的仓位 0.4350 当常量套到历史 β 上＝反事实（页面与 caveats 双处披露），不是历史敞口记录；"
        "③往返税假设每个超帽窗整笔卖、段末整笔买，更慢的跟随者付得更少；"
        "④全量冒烟与 S6 链连续第 18 轮未跑（竞争窗），禁读成已全绿；⑤心跳面本窗未覆盖（对端 05:10 写过）"
    ),
    "竞争_r2073": (
        "repo_write_contention rc=3 CONTENTION：对端 interactive pid 79608（codely.exe，2026-11-24T22:39 起、age 396.4m、"
        "20s CPU 仅 0.12s＝挂起非在算）在轮首前写过 16 张共享面、重叠窗内不可归因 0 张；HEAD=round 2072 于 05:08:43 提交、"
        "心跳 05:10:04、ARBITER-BOARD 05:11:42 -> 按 r1907 只落新增文件面，未改共享面、未跑 S6 链、未跑全量冒烟"
    ),
    "通过_r2073": (
        "orders 117 件（与 r2069/r2072 同数）/ fleet/inbox 空；origin/main:docs/decisions.md 原生字节 250,586B "
        "sha256 79e3083b85c130b8… == 自持水位 -> 零新决策零动作；attrition tripwire 与 schtasks 自愈本轮未触碰（竞争窗）"
    ),
    "记账_r2073": "轮报告 1 处 + state 1 处 = 2（心跳面由对端写、本窗不改，故不记；无方法论新增：把「元」做成整手与往返税两条可复核读数属证据与载体）",
    "下轮指针": (
        "(a) 静窗后把「往返税 4,131.54 元 vs 差额在噪声内」接进 CEO 一页纸帽子行（共享面，一句 disposition）；"
        "(b) 给 etf_book_cap_trim_toll 接一条冒烟腿（判据=verdict_day/verdict_path 与 facts 同代，面 stale 即红）；"
        "(c) 全量冒烟 + S6 分批补跑（连续第 18 轮未跑，≤48h 必须收口）"
    ),
    "下个里程碑": "(a) 帽子行接一页纸 + 本面接冒烟腿；(b) 全量冒烟 + S6 收口（≤48h）",
}


def main():
    # 1) round report: append one line
    with io.open(REPORT, "rb") as fh:
        raw = fh.read()
    if LINE.encode("utf-8") in raw:
        print("report line already present; skipping append")
    else:
        with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(LINE)
        print("report appended")

    # 2) state: read, patch keys, write back with the file's own indent
    with io.open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    before_round = st.get("round_no")
    st.update(STATE_UPDATES)
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        # indent=1 is the file's own shape (checked on line 2 before writing: r2043 self-catch,
        # a wrong indent rewrites all 1,503 lines and buries the peer's fields in the diff)
        json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("state round_no %s -> %s, keys=%d" % (before_round, st["round_no"], len(st)))


if __name__ == "__main__":
    main()
