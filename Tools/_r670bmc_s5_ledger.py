# -*- coding: utf-8 -*-
"""r670 bm-c S5 ledger row append (canonical path constant per r646 law;
byte-level append, tail EOL gate, count==1 post-verify per r503 v2 law)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ROW = (
 "2026-10-07T10:50:40+08:00 | r670 bm-c | dept:工程/舰队（金周值守轮+D-06 lineage 让位 sub-split+主件增量批+5x HANDOVER 义务+派单回执核收闭口） | "
 "当前活: r670 值守轮（S0 萮首脏=3 daemon live-wins 面零 rebase〔落后 0/领先 0〕·S1 48/48·S0.5 双扫 DEC 635C3024/ORD B687D867 零 delta×2+orders 164/164 零未回执+inbox bm-b capability receipt 核收=O-20261007-0935-bm-c 派单正主收口〔JSON 证据件 cat-file rc0 验达 origin+MSG 转 processed+票面 bm-b 勾选+回执节 md 表写入·两机回执全收提前交付 ≤10-09 窗·bm-a r817+bm-b r803 派单闭口〕·S3 SAT 活 rc0+水位绿〔next_pick=claimed moneyflow IC batch 面板 parked EM 源阻 30min 自愈不变〕+板 0 open+job_list 0+试用劳力线不触发〔W172 bm-a r818 预坐席+trio finalize bm-b 在飞=在飞判决工作存在〕；"
 "主产品=pit-lineage.md 30,552B 满员让位 sub-split〔r669 next 指针窗兑现〕：收据可复核律族 12 条〔r554/r555/r559/r560/r569/r570/r578/r583/r587/r629/r637/r646〕verbatim 零丢失迁出→research/pit-lineage-receipt.md 新子件 15,198B〔字节对账+md5 行〕+母件 30,552→18,527B〔−12,803B 迁出+778B 指针行〕+主件增量批：r653 close 尺寸声明陈旧收据坑 677B→receipt 子件〔r646 同族归位〕+r669 双 derive 恒等门坑 802B→pit-git.md 拆件断言层族〔r651 前例〕·主件 30,527→30,101B 回线余 619B·**构造式×方程式双 derive 恒等门首次实装**〔r669 S4 坑正法落地·四文件构造==方程全过·尺寸 gate 当场 len() derive〕·prescan rc3 留痕+登记册预登记行+收据+--verify 93/93 PASS；"
 "三坑当场实弹全 fail-closed 零写出：①needle 同轮号异坑撞车〔裸轮号「r637」撞 pit-git-resolver.md 同轮号 marker 扫描坑条目·sibling already-migrated 门拦截〕→S4 直写 pit-git.md 913B〔r668 同窗直写先例·主件零占用〕②r653 收据-实测律第三活例〔r669 next 声明 676/803B vs 实测 677/802B 双陈旧·声明值再证不可信〕③拆件头部行数假设错〔real[4] blank gate fail-closed 拦截·probe 实况 6 行头后修正〕） | "
 "验证证据: results/_r670bmc_lineage_receipt_split.json（零丢失收据·93 checks --verify PASS·双 derive 方程四文件全过·prescan rc3）+research/pit-lineage-receipt.md（新子件 12+r653 条）+research/pit-lineage.md（18,527B+指针行）+research/pit-git.md（r669 坑+直写行 26,991B）+CODELY.md（主件 30,101B）+knowledge/TREASURE_REGISTRY.md（r670 预登记行）+qa/smoke-r670.md 5/5+qa/equity-curve-r670.png（93 trades·determinism=True·equity 1,017,839 跨轮恒等·png 66,379B）+results/_r670bmc_s6_log.txt 38/38 rc0（NON-ZERO LEGS none·bm-a hb 陈 29min→4 宿主面 stale-takeover derive 合法）+results/_r670bmc_s05_facts.json（DEC/ORD 零 delta）+fleet/orders/O-20261007-0935-bm-c.md（bm-b 回执节+双勾）+fleet/inbox/processed/MSG-2026-10-07-095x-bmb-bmc-capability-receipt.md | "
 "下轮指针: 10-08（周四）复市首交易日=数据链 re-arm〔S6 legs 25-28 复活〕+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥10-01 当日核验）+纸盘 marks 地板推进+external run-11/run-7（bm-a r714 readiness owns preflight）；trio finalize 窗观察至 10-09（bm-b 道 D 1674→）；W172 冻结窗 bm-a 预坐席在册；月界首考 10-31；下个 5x=r675；主件余量 619B=下批 direct-write pit 续压面 | "
 "watermark: 绿（red=false lane healthy·板 0 open·池 401 done+1 ready bm-b keepalive+1 治理停泊 W14 零触碰·金周无 bar 合法 idle） | "
 "本地未达 origin commit 数=0（S0 fetch 实测·收口推送后复验）"
)

raw = open(LEDGER, "rb").read()
assert raw.endswith(b"\r\n") or raw.endswith(b"\n"), "tail EOL gate"
guard = "r670 bm-c | dept:".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
sep = b"" if raw.endswith(eol) else eol
new = raw + sep + ROW.encode("utf-8") + eol
open(LEDGER, "wb").write(new)
post = open(LEDGER, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
print("S5 row appended; ledger now", len(post), "B")
