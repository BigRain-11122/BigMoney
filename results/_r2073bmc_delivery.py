"""r2073 addendum: delivery facts (commit sha, branch, ls-tree proof).

Second commit by design: the delivery line cannot contain the sha of the commit that carries
it (r2062 addendum-2 precedent).
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REPORT = os.path.join(REPO, "round_reports-bm-c.md")
STATE = os.path.join(REPO, "state-bm-c.json")

TS = "2026-11-25T05:31:00+08:00"

LINE = (
    "2026-11-25T05:31:00+08:00 | r2073a | bm-c | 送达补记：commit **5481cc49ae**（10 件·+1261/−110——"
    "新建 scripts/etf_book_cap_trim_toll.py / results/etf_book_cap_trim_toll.json / research/ETF_BOOK_CAP_TRIM_TOLL.md / "
    "qa/cap-trim-toll-r2073.md / 负控与收口 results/_r2073bmc_*.py（-f 入册·results/_ 白名单外），"
    "改 round_reports-bm-c.md / state-bm-c.json（2072→2073·indent=1 与原档同形·+16/−12 只动目标键）/ "
    "本轮探针证据 results/_repo_write_contention.bm-c.json）。"
    "main 直推被拒（non-fast-forward：origin/main 独有 1、本机独有 31；远端那 1 件是他机的 "
    "ingest INVENTORY-DASHENG-20261124，与本轮零文件重叠，未 rebase 以避开工作树既有 30+ 张他机脏件），"
    "按 D-20260925-01③ 推 **origin/machine/bm-c-r2073**（新分支）；fetch 后 "
    "`git rev-list --left-right --count origin/machine/bm-c-r2073...HEAD` = **0/0**，"
    "`git ls-tree -r --name-only origin/machine/bm-c-r2073` 六件实物全在位"
    "（scripts/etf_book_cap_trim_toll.py、results/etf_book_cap_trim_toll.json、research/ETF_BOOK_CAP_TRIM_TOLL.md、"
    "qa/cap-trim-toll-r2073.md、results/_r2073bmc_cap_trim_toll_negctl.py、results/_r2073bmc_closeout.py）。"
    "**本地未达 origin/main commit 数**：本条 commit 前实测 origin/main…HEAD = 1/31；本 addendum 自身再加 1 → "
    "读者此刻应为 1/32（自指计数差 1 按 r2062 addendum-2 判例写清）。"
    "S7：attrition tripwire 未跑（竞争窗）；schtasks 自愈未触碰（对端在飞）；pre-commit/pre-push 爪未触发新装。"
    "| 记账：本行 1 处 + state 1 处（累计 4）。\n"
)

STATE_UPDATES = {
    "送达自证_r2073": (
        "commit **5481cc49ae** 已推 origin/machine/bm-c-r2073（新分支；main 直推被拒=non-fast-forward，"
        "origin/main 独有他机 ingest 1 件、零文件重叠，未 rebase 以避开工作树 30+ 张他机脏件）；"
        "fetch 后 rev-list --left-right --count origin/machine/bm-c-r2073...HEAD = **0/0**；"
        "ls-tree origin 分支六件实物全在位（scripts/etf_book_cap_trim_toll.py、results/etf_book_cap_trim_toll.json、"
        "research/ETF_BOOK_CAP_TRIM_TOLL.md、qa/cap-trim-toll-r2073.md、结果负控与收口两件）→ 本地未达 origin/main commit 数=1/32"
    ),
    "本地未达 origin commit 数": "1",
    "本地未达origin": "32",
    "记账_r2073": "轮报告 2 处（本轮行 + 送达 addendum）+ state 2 处（本轮 + 送达）= 4（无方法论新增：把「元」做成整手与往返税两条可复核读数属证据与载体）",
}


def main():
    with io.open(REPORT, "rb") as fh:
        raw = fh.read()
    if LINE.encode("utf-8") in raw:
        print("addendum already present")
    else:
        with io.open(REPORT, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(LINE)
        print("addendum appended")

    with io.open(STATE, "r", encoding="utf-8") as fh:
        st = json.load(fh)
    st.update(STATE_UPDATES)
    with io.open(STATE, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(st, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write("\n")
    print("state updated, round_no=%s keys=%d" % (st.get("round_no"), len(st)))


if __name__ == "__main__":
    main()
