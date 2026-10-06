# -*- coding: utf-8 -*-
# r661 bm-c close-tail erratum line: churn-absorb-m1 commit message mislabel
# correction (r653/r307 erratum pattern -- pushed history never rewritten,
# correction carried by ledger line). Byte-exact CRLF append.
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RR = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
line = ("勘注 r661 (07:4x): 竞速尾窗 commit 'churn-absorb-m1 r661' 消息误标——实际载荷=CODELY over-gate 门修正"
        "（r656 条目 934B verbatim 迁出 CODELY.md→research/pit-git.md·CODELY 30,903→29,969B 门内 751B 余量"
        "·收据 results/_r661bmc_codely_minisplit.json·sha16 0fc3026f2536da2e·r651/r654 当窗即办）"
        "+minisplit 脚本/收据件+当窗 daemon tick 面；根因=git commit -- pathspec 对未跟踪新件 pathspec 报错致定向提交失败"
        "→竞速循环 add -A 兜底提交吞全载荷但吃下循环消息（零文件损失·r648 判侧面核毕）；已推不回改（r307 律）·本勘注行承载修正。"
        "轮 r661 全链已送达（race 链：b3a46ee24 主件+963f82f47/c98c5440d churn-absorb+f651a5d5e 尾批+a39f2d15e minisplit·N=0 双证）。")
raw = open(RR, "rb").read()
pre = b"" if raw.endswith(b"\n") else b"\r\n"
open(RR, "ab").write(pre + line.encode("utf-8") + b"\r\n")
print("erratum line appended", len(line.encode('utf-8')), "B")
