"""r731 bm-c ledger appendix row: S7 tail-window honest disclosure
(wrapper -m quoting re-offense r849 family + amend-on-pushed-commit
self-caught cure + second-sweep CLEAN + delivery proofs).
Append-only, UTF-8 explicit."""
import os

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
RP = os.path.join(REPO, "logs", "iteration-loop", "round_reports-bm-c.md")

ROW = ("2026-10-08T05:0x+08:00 | r731-S7附加 | S7 尾随窗实录（诚实披露三面）："
       "①tail 登记 -m 经 silent-git 包装器内层引号吞=r849 族在册坑重踏"
       "（自捕·-F 消息件正法改道 tail1 30276874a/tail2 b41e6240e 送达零损失）；"
       "②tail2 已 push（b41e6240e）后又 amend 补登记 tail 消息件=改写已推提交"
       "→push 必非快进死局·禁 force 律下无合法出路→同窗自愈=ls-remote 核实 "
       "origin tip 后 reset --soft 回 b41e6240e（staged 保全）+新 tail3 提交 "
       "02c8ab3d4 快进 push CLEAN（b41e6240e..02c8ab3d4）——零 force 零远端改写"
       "零内容丢失·新坑律 916B verbatim 直写 pit-git-staged.md（commit 入场门族"
       "·r806/r689 同域）·主件 30,606B 水位超线→r853 行 338B 同窗 verbatim 迁 "
       "pit-tooling.md+341B 短指针行置换·收据 results/_r731bmc_codely_minisplit.json"
       "（主件术后 30,609B≤30,720 断言过·零丢失断言过）；③S0.5 收尾二扫 CLEAN"
       "（orders 51 unacked=0·DEC EE659451/ORD 17accc40 双 UNCHANGED·facts 字节"
       "恒等零脏·inbox 0）·三证送达 HEAD==origin==ls-remote==02c8ab3d4·"
       "behind=0/ahead=0·残余脏=2 satengine daemon churn 面（轮间活写·下轮吸收"
       " r628/r730 正典） [via bm-c r731]\n")


def main():
    with open(RP, "a", encoding="utf-8", newline="") as f:
        f.write(ROW)
    tail = open(RP, "rb").read()[-120:]
    assert b"r731-S7" in tail, "appendix row must be at ledger tail"
    print("appendix row appended; ledger tail verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
