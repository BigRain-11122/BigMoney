"""r468 bm-c S7-close line append (bytes-safe, EOL-adaptive)."""
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
REPORT = os.path.join(REPO, "round_reports-bm-c.md")

LINE = ("2026-10-04T12:26｜r468 bm-c S7-close｜本地未达 origin commit 数=0（push_verify "
        "DELIVERED·tip 2dd10e0dd==remote·ahead=0/behind=0·round commit 1bbaf29b4+merge "
        "commit 2dd10e0dd 随 push_verify 自证）｜收口实录：round commit 1bbaf29b4（89 面）→fetch "
        "behind=9（bm-a r673/r675 wave+bm-b r669 收口波+merges）→merge origin/main 撞 20 UU"
        "（同日幂等再生态竞写族·r452/r455/r462/r465/r466 同型）→canon 解 20 面（resolver="
        "results/_r468bmc_merge_resolve.py·证据 _r468bmc_merge_resolve.json：regen 双胞胎 ts 诚实"
        "比较逐面 take-newer+compute_audit hist-union+token_usage per-key union〔r456 律断言〕）"
        "→merge commit 2dd10e0dd→push_verify DELIVERED 零爪拦零 --no-verify 零强推｜WM 红牌全链"
        "实证：12:14:02 red=true（T-168 开票未即认领→py_low_with_work_cands）→同窗认领+移植完成"
        "→py_watermark re-probe py_low_board_clear（open_tickets=0）→watchdog 12:20:02 "
        "red=false=红牌自愈闭环（CEO 即时律执法面=水位系统按设计运转·开票→红牌→认领→交付→红牌"
        "落空全程 <10min·round_reports 主行水印 verdict 已按轮中红牌+自愈双面如实记载）｜零清扫/"
        "归档/删除/恢复类动作轮：登记册零命中断言照实（treasure_guard 零调用面·五收口步零触发"
        "→TREASURE_REGISTRY/METHODOLOGY_ASSETS 零新行照实）｜轮产品计分：F-20261004-01 四行回执件"
        "+T-168 fix① 移植（claim→port→selftest 11 legs 同窗）+selftest/对账证据件+S6 管线产出"
        "=可跑/能看/能用实物（非空转·金周值守窗）")


def main():
    with open(REPORT, "rb") as f:
        raw = f.read()
    tail = raw[-400:]
    eol = b"\r\n" if b"\r\n" in tail else b"\n"
    add = LINE.encode("utf-8")
    with open(REPORT, "ab") as f:
        f.write(eol + add)
    with open(REPORT, "rb") as f:
        assert f.read().endswith(add), "append verify failed"
    print("CLOSE_APPEND_OK", len(add), "bytes")


if __name__ == "__main__":
    main()
