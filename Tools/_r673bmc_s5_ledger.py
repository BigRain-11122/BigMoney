# -*- coding: utf-8 -*-
"""r673 bm-c S5 ledger row append (canonical path per r646 epoch law;
byte-level append, tail EOL gate, count==1 post-verify per r503 v2 law)."""
import datetime as dt
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
TS = dt.datetime.now().astimezone().isoformat(timespec="seconds")
ROW = (
 TS + " | r673 bm-c | dept:工程/舰队（金周值守轮+复市前夜就绪探针机器自适应扩展） | "
 "当前活: r673 值守轮（S0 首脏 5 件=本机 daemon 面+r672 commitmsg 遗件→absorb commit+pull --rebase 落 bm-a r821〔落后 1→0〕·S0.5 双扫 DEC 635C3024/ORD B687D867 零 delta+orders 164/164 零未回执+inbox 0·S1 48/48·S3 SAT 活 rc0+水位绿+板 0 open+job_list 0+池 401 done+1 ready bm-b DIVLOWVOL 在飞〔10:40 续认领〕+W14 停泊零触碰+试用劳力线不触发〔W3 judge-prep bm-a 在飞+trio 窗内〕+tripwire CLEAN〔r672 UU 窗零再翻倍〕+attrition CLEAN；"
 "主产品=open_market_readiness.py 机器自适应扩展〔加法·bm-a 座字节保持：MACHINE=fleet/machine.json 探测·face 函数 machine 参数化·R31 车道面 PANEL_LANES 只验本机自属面板（bm-c=fund_premium/bm-b=minute_feed）·他机面缺席=合法 fact·非 bm-a 座产物带机号后缀〕selftest 20→28 腿 ALL PASS〔新腿=机感回退/车道 RED/未知机无假红+lane_map_missing/md 后缀幂等/bm-a 标题字节保持〕+bm-c 座复市前夜实跑=verdict AMBER〔6 绿+2 黄：moneyflow EM 源断流自愈中+trio finalize 窗内·零红面〕→docs/open_market/READINESS-2026-10-07-bm-c.md；"
 "连带三件=MSG-2026-10-07-1200-bmc-ALL（扩展通知·bm-a 明日复跑零变化）+坑律直写 pit-tooling.md〔机感常量泄漏 fixture 坑·+939B·收据 sha16=1af419e6ac95f4b1·主件余量 322B 法〕+QA r673 5/5〔detached --round 673·equity 1,017,839 跨轮恒等〕） | "
 "验证证据: docs/open_market/READINESS-2026-10-07-bm-c.md+results/open_market_readiness.bm-c.json（AMBER 6绿2黄零红）+scripts/open_market_readiness.py（selftest 28/28）+qa/smoke-r673.md 5/5+qa/equity-curve-r673.png+results/_r673bmc_s6_log.txt 38/38 rc0（dualrun streak 51·REPORT/LIVE-2026-10-07 再生 ORANGE·fund_premium 15:30 前合法 no-op）+results/_r673bmc_s05_facts.json（DEC/ORD 零 delta 双扫）+results/_attrition_guard_scan.json CLEAN+results/_r673bmc_pit_tooling_increment.json（直写收据） | "
 "下轮指针: 10-08（周四）复市首交易日=数据链 re-arm〔S6 legs 复活〕+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar≥2026-10-01 当日核验）+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道·panel 就绪 r671 已核）；trio finalize 窗观察至 10-09（bm-b 道）；W172 bm-a 在烧·finalize 后 W173 坐席窗；月界首考 10-31（T-143 deliverable 10-29）；下个 5x=r675；每轮收口前 tripwire scan（E09 律） | "
 "watermark: 绿（red=false lane healthy·板 0 open·池 401 done+1 ready bm-b 在飞+1 停泊 W14 零触碰·金周无 bar 合法 idle） | "
 "本地未达 origin commit 数=2（S0 吸收件+本轮收口件·收口推送后复验）"
)

raw = open(LEDGER, "rb").read()
assert raw.endswith(b"\r\n") or raw.endswith(b"\n"), "tail EOL gate"
guard = "r673 bm-c | dept:".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
sep = b"" if raw.endswith(eol) else eol
new = raw + sep + ROW.encode("utf-8") + eol
open(LEDGER, "wb").write(new)
post = open(LEDGER, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
print("S5 row appended; ledger now", len(post), "B")
