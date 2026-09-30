# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
P = "CODELY.md"
src = open(P, encoding="utf-8").read()
old = (
    "- 冷层指针：r236 GBK 控制台吞链+r444 fork-point 过时基点重放两律全文 "
    "verbatim=archive 202609.md『热冷整编 2026-09-30 r452 bm-a 窗批』节"
    "（r440 撞批三查律=同窗 r245 bm-c 节在档去重单存·r449 dedupe 律；"
    "操作面活跃度=runner 入口 reconfigure 惯例/rebase 风暴窗两步——法面由 "
    "iteration_prompt S3+r444 步骤文承载，热层指针在位即可发现）。\n"
    "- 冷层指针：r229 LHB 源改史+r235 core48 源分层+r237 波级泊位窗先例三律全文 "
    "verbatim=archive 202609.md『热冷整编 2026-09-29 r447 bm-a 窗批』节"
    "（r440 bm-b 批曾热留=操作面活跃·本批水位 10,606B 复超线当窗即办·r237 "
    "先例已由 DECISION_CHAIN §四.7 法面+W12 draft 头部双载）。")
new = (
    "- 冷层指针（r464 合并）：r236 GBK 控制台吞链+r444 fork-point 过时基点重放"
    "两律（操作面=runner 入口 reconfigure 惯例/rebase 风暴窗两步·法面由 "
    "iteration_prompt S3+r444 步骤文承载=『热冷整编 2026-09-30 r452 bm-a 窗批』"
    "节）+r229 LHB 源改史+r235 core48 源分层+r237 波级泊位窗先例三律（r237 先例"
    "已由 DECISION_CHAIN §四.7 法面+W12 draft 头部双载=『热冷整编 2026-09-29 "
    "r447 bm-a 窗批』节），全文 verbatim=archive 202609.md。")
if src.count(old) != 1:
    print("count:", src.count(old))
    sys.exit(2)
src = src.replace(old, new)
open(P, "w", encoding="utf-8", newline="\n").write(src)
n = len(src.encode("utf-8"))
print("OK %d bytes (%s)" % (n, "UNDER" if n <= 10240 else "OVER"))
