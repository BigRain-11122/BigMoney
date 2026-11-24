"""r2076 bm-c closeout: append the round row and heal the round_no double-face drift.

Two shared faces only (round report row + state round_no); the report is read fresh, appended and
written back in one pass so a concurrent writer's row cannot be swallowed (r1005 law: never use the
replace tool on a multi-writer ledger).
"""
import io
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "round_reports-bm-c.md")
STATE = os.path.join(ROOT, "state-bm-c.json")

ROW = (
    "2026-11-25T06:22:00+08:00 | r2076 | bm-c | **PRODUCT（产品优先律·watermark 绿（red=false·lane=healthy·next_pick 他机 claimed）·"
    "孤儿面=0（py_faces=5 / orphans=0 / resident_servers=2）·竞争窗 rc=3 CONTENTION〔对端 codely.exe pid 79608 自 2026-11-24T22:39 起仍活、"
    "HEAD=round 2075 于 06:01:43 提交、21 张共享面在轮首前被动过，证据 results/_repo_write_contention.bm-c.json〕→ 按 r1907/r1927 只落新增文件面："
    "未改共享面、未重跑 S6 链、未跑全量冒烟、未改心跳面）**：前几面把「ETF 书 43.5% 是不是超帽」「要不要削 19,543 元」算透了，可没人把 "
    "**同一笔钱在三只书上并排**算过——而账上真正的约束不是帽子，是容量。同一笔 1,129,565.88 元：ETF 复合书 **125,495/年**（11.11%）、"
    "1 手 IC carry **79,953/年**（对资金 7.078%；tape 面净读数 6.361pp=77,070）、现金 **20,002/年**（废弃 1.7708%）。carry 比 ETF 少 **45,541/年**"
    "（tape 读数少 48,425）——所以「再加 129,566 去跳一手 carry」这一步付的是 7.078%，离开的是 11.11%。而离开的那本书也接不住：今天的 1% ADV 容量线在 "
    "**1,043,800.91**，走完这一步超线 **85,764.97**，且这笔资金在最近 60 个交易日里只有 **4 天**在线内（6.67%）；carry 一侧整手跳 12.96%、但容量万倍级。"
    "判词 `THE_STEP_IS_PRICED_WORSE_AND_THE_RICHER_BOOK_HAS_NO_ROOM`＝**钱不是瓶颈，容量与整手才是**，下一份研究该找的是「接得住的第三条腿」。"
    "| 证据：scripts/capital_marginal_road.py（selftest **14/14 OK**·run rc0·--check **CHECK OK** rc0）+ results/capital_marginal_road.json + "
    "research/CAPITAL_MARGINAL_ROAD.md（marker 块逐字复核）+ qa/marginal-road-r2076.md + 负控 results/_r2076bmc_marginal_road_negctl.py **9/9 PASS**"
    "（改数→CHECK FAILED 且点名 `books.carry.income_cny_upper` 且不含 STALE／动 inputs_digest→STALE 且不含 CHECK FAILED／改页一行→点名 page block（先断言该行真在页面里）／"
    "丢 marker→rc3／缺面→STALE face missing／复原→绿／七张上游面 sha256 前后恒等）。**自捕两枚**：①首版判词分支里「现金档」腿不可达（恒假腿），自检当场抓出并把 "
    "classify 改成「两本书都输给现金才算现金档」；②首版 check 只比 inputs_digest 与 facts_digest 两个哈希，**发布面自己改一个数不会被抓**（页块比对先拦下），"
    "负控当场抓出后加「发布面必须哈希到自己的 facts_digest」+ `_leaf_diffs` 点名叶子。| 未做（如实）：`ceo_live_usage.py` 帽子行未接（共享面）——建议一句「下一笔钱三去处：ETF 超容量线 85,765、carry 缺 129,566、现金 1.77%」；"
    "本面未接冒烟腿/S6 腿（共享面）；全量冒烟连续第 20 轮未跑（红腿读数仍是 2026-11-24T20:12:28 的 765 腿/34 红）；S6 链连续第 20 轮未跑；心跳面由对端在写，本窗不覆盖。"
    "| S0.5 双扫：fleet/orders **117 件**、心跳 orders_ack 331 条、**未回执 44 件（2026-11 内 0 件）**（44 件全为他机 lane 广播，按 r2066 判例不逐令补 ack）；"
    "集团 origin/main:docs/decisions.md 原生字节 **250,586B sha256 79e3083b85c130b8…**（git cat-file 直落临时件再 Get-FileHash，不经 PS 字符串往返，r1911/r2048 律）"
    "**== 自持水位** → 零新决策零动作；fleet/inbox 空（仅 processed/）。| S7：orphan_face_probe 已跑（py_faces=5 / orphans=0 / resident_servers=2）；"
    "schtasks 自愈未触碰（对端在飞，重注册会打断）；attrition tripwire 未跑（竞争窗，与冒烟/S6 同列延后）。| 轮号双面漂移当窗 heal（r1020 判例）："
    "HEAD 提交已称 round 2075 而 state round_no 仍是 2074 → 本轮按仓根叙事取 **2076** 并写回 state，报告里记明。"
    "| **本地未达 origin commit 数**：本轮 commit 前实测 origin/main…HEAD = 2/34（本行 commit 后再 +1，读者此刻应为 2/35；自指计数差 1 按 r2062 addendum-2 判例）。"
    "| 下轮指针：(a) 静窗后把「三去处」一句接进 CEO 一页纸（共享面，一句披露非新判据）；(b) 本面接一条冒烟腿（判据=verdict 与两个读数同代，面 stale 即红）；"
    "(c) 全量冒烟 + S6 分批补跑（连续第 20 轮，≤48h 必须收口）；(d) 研究面：找「容量接得住的第三条腿」——供给块红的根因正是没人写第 21 张卡。"
    "| **CEO 三行**：当前活＝回答「手里这 1,129,566 元放哪更赚钱」——同样的钱，ETF 书 125,495/年、carry 一手 79,953/年、现金 20,002/年；"
    "下一笔 129,566 元进 ETF 书会超容量线 85,765（60 天里只有 4 天装得下），跳 carry 一手则少赚 45,541/年｜"
    "最近实物=K:\\Fluxgroup\\FluxGroup\\quant\\bigmoney\\research\\CAPITAL_MARGINAL_ROAD.md（2026-11-25T06:22·selftest 14/14·负控 9/9·--check rc0）｜"
    "下个里程碑＝把三去处接进 CEO 一页纸 + 接冒烟腿（≤48h）。| 记账：轮报告 1 处 + state 1 处 = 2（心跳面由对端写、本窗不改；无方法论新增：把「同一笔钱三只书」做成可复核读数属证据与载体）。"
)


def main():
    with io.open(REPORT, "r", encoding="utf-8", newline="") as fh:
        text = fh.read()
    if "| r2076 | bm-c |" in text:
        print("row already present, no double append")
    else:
        if not text.endswith("\n"):
            text += "\n"
        text += ROW + "\n"
        with io.open(REPORT, "w", encoding="utf-8", newline="") as fh:
            fh.write(text)
        print("appended r2076 row (%d bytes)" % len(ROW))

    with io.open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    old = st.get("round_no")
    st["round_no"] = 2076
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")
    print("state round_no %s -> %s" % (old, st["round_no"]))


if __name__ == "__main__":
    main()
