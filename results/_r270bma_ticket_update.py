# -*- coding: utf-8 -*-
"""R270 bm-a：T-83 票面 progress_r270 写回（字节面镜像：no-BOM/CRLF/indent=1/trailing-nl/ensure_ascii=False）。"""
import json, subprocess, sys

P = r"fleet\tasks\T-2026-09-26-83-P1.json"
TXT = (
    "bm-a R270 (GM 专管会话): s3 GM seven-deliverable batch slice 2 of 3 LANDED —— 件③ firm/DOC_HIERARCHY.md v1.0 "
    "(L2 21件层级序 H0-H6 + 裁决规则5条 + 指针纪律4条; 集团层指针标注律 §二.4 入法) + 件⑤ research/ORDERS_INDEX.md v1.0 "
    "(84令全量索引; GM 原文精读裁定: 1 条款级取代边 O-20260924-1136→O-20260923-1738「保留20%」+ 3 机制修正 O-2205/O-1730/O-2012 "
    "+ 5 关键词假面 O-1705/O-2134/O-2210/O-2313c/O-1355; s1 九面计数裁定归真; 生成器 results/_r270bma_orders_index_md.py 幂等可重跑) "
    "+ 件⑥ research/AUDIT-20260926-S2-ADJUDICATION.md (12裁定: t22双链=车道本地大文件面假阳(.gitignore:65·产机在位实证); 集团层指针3面合法"
    "(FluxGroup仓在位实证·检测器白名单候选); SYSTEM_LOGIC 8遗留名/FACTOR_BLEND_V2 5链头注记(归档不删); HANDOVER 历史行 append-only 零改写裁定; "
    "local-coding 01-10 十脚本不晋升(消费驱动晋升律)+任务11/12未实现(tasks 01-10实证); 活文档指针修复8件 fixer=results/_r270bma_pointer_fixes.py "
    "字节级幂等13操作(CASH_LEG=子串假面零改·执行器自捕); BACKTEST_PLAN 引O-1738 算力动员政策=未取代条款合法零改) + 件⑦ STRATEGY_LIBRARY §〇 "
    "产品线状态单源表 (12线×状态×判据面×载体 + 判负库存6面 zoo 升格; MATRIX/MAP 单源指针行接入; WILD-S1 首判 negative 0/1569 g2注册空如实入表) "
    "—— s3 GM 七件套至此全落地(件①②④ R269 + 件③⑤⑥⑦ R270), s4 季度接线 R266 已交; 票四片全齐, owner(bm-b)可翻 done 收口(result_ref 指针已齐)。"
    "post_review 行 T-83-S3-GM-SLICE2 注册(锚稳定产物件·R264 律)。"
)

b = open(P, "rb").read()
assert b[:3] != b"\xef\xbb\xbf" and b"\r\n" in b and b.endswith(b"\n"), "byte face drifted"
t = json.loads(b.decode("utf-8"))
t["progress_r270"] = TXT
nb = (json.dumps(t, ensure_ascii=False, indent=1) + "\n").replace("\n", "\r\n").encode("utf-8")
open(P, "wb").write(nb)
r = subprocess.run(["git", "diff", "--stat", "--", P], capture_output=True, text=True, encoding="utf-8")
print(r.stdout.strip())
lines = [l for l in r.stdout.splitlines() if "|" in l]
added = sum(int(l.split("|")[1].split("+")[1].split(" ")[0] or 0) for l in lines if "+" in l.split("|")[1])
removed = sum(int(l.split("|")[1].split("-")[1].split(" ")[0] or 0) for l in lines if "-" in l.split("|")[1])
print(f"field-level gate: +{added}/-{removed} (expect small, one new key => ~+2/-1)")
assert added <= 4 and removed <= 2, "diff not field-level — investigate"
print("ticket update OK")
