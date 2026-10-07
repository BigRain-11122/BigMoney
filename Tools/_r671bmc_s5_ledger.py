# -*- coding: utf-8 -*-
"""r671 bm-c S5 ledger row append (canonical path constant per r646 law;
byte-level append, tail EOL gate, count==1 post-verify per r503 v2 law).
Row goes into the HEALED round_reports-bm-c.md (r671 heal same-round)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
ROW = (
 "2026-10-07T11:19:00+08:00 | r671 bm-c | dept:工程/舰队（金周值守轮+轮报台账 2\u00b3 整文件翻倍治愈批+tripwire 立线） | "
 "当前活: r671 值守轮（S0 首脏=本机 daemon live-wins 面吸收 commit 1 件+checkout 弃秒级 telemetry churn·pull 落后 0〔origin 无新 commit〕·S1 48/48·S0.5 双扫 DEC 635C3024/ORD B687D867 零 delta+orders 164/164 零未回执+inbox 1=W172 seat MSG=bm-a 车道〔bm-a r819 冻结已落地·观察不代处理〕·S3 SAT 活 rc0+水位绿〔next_pick 不变〕+板 0 open+job_list 0+池 401 done+1 ready bm-b 在飞+1 停泊 W14 零触碰+fund_premium 本车道复活就绪自查=48/48 NAV+dividends 全覆盖 cutoff 2026-09-30 假日地板正确+试用劳力线不触发〔DIVLOWVOL nulls bm-b 10:40 续认领在飞〕；"
 "主产品=round_reports-bm-c.md 2\u00b3 整文件翻倍治愈：S3 例行盘点发现 9,265 行/17.88MB/头行\u00d78/条目\u00d78——git blob 链实证 r666/r668/r669 三窗 push-race UU 收口整文件 bare-concat（2,230,045\u21924,461,521\u21928,933,204\u219217,873,611B 每窗 \u00d72）→prescan rc0 零命中→tripwire+治愈工具 _r671bmc_rr_dup_heal.py〔scan/heal/selftest 三模式·selftest 9/9〕→keep-first exact-line dedup〔r453 正典律整件面扩〕17,882,876\u21922,245,406B〔\u221215,637,470B·\u22128,106 行〕→集合恒等零丢失门+头\u00d71+300 条目全唯一+post-scan CLEAN+git diff 纯删除零插入〔healed=原文严格子序列〕→隔离区 7 天窗+收据；连带三件=坑律直写 pit-git-surgery.md〔r453 族第三面·+1,187B·主件零占用〕+方法论卡 E09〔append-only 翻倍 tripwire+keep-first 治愈法〕+登记册出入行；历史注记=r657-r666/r668/r669 条目行在翻倍前死窗已失〔commit message 存案·非本窗损失〕） | "
 "验证证据: results/_r671bmc_rr_dup_heal_receipt.json（集合恒等+shape 全门）+Tools/_r671bmc_rr_dup_heal.py（selftest 9/9+scan CLEAN 复扫）+results/_quarantine/20261007-1105_r671bmc_rr_predup/manifest.json（字节恒等隔离）+qa/smoke-r671.md 5/5（93 trades·determinism=True·equity 1,017,839 跨轮恒等）+qa/equity-curve-r671.png+results/_r671bmc_s6_log.txt 38/38 rc0（dualrun streak 51·REPORT/LIVE-2026-10-07 再生 ORANGE）+results/_r671bmc_s05_facts.json（DEC/ORD 零 delta）+results/_attrition_guard_scan.json CLEAN | "
 "下轮指针: 10-08（周四）复市首交易日=数据链 re-arm〔S6 legs 复活〕+REGIME_GUARD v3 首 bar 激活（t24 门 last_bar\u22652026-10-01 当日核验）+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道·panel 就绪已核）；trio finalize 窗观察至 10-09（bm-b 道）；W172 bm-a 在烧·finalize 后 W173 坐席窗（re-derive on post-W172 universe）；月界首考 10-31（T-143 deliverable 10-29）；下个 5x=r675；每轮收口前跑 tripwire scan（E09 律） | "
 "watermark: 绿（red=false lane healthy·板 0 open·池 401 done+1 ready bm-b keepalive+1 停泊 W14 零触碰·金周无 bar 合法 idle） | "
 "本地未达 origin commit 数=2（S0 后实测=churn 吸收件+治愈件·收口推送后复验）"
)

raw = open(LEDGER, "rb").read()
assert raw.endswith(b"\r\n") or raw.endswith(b"\n"), "tail EOL gate"
guard = "r671 bm-c | dept:".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
sep = b"" if raw.endswith(eol) else eol
new = raw + sep + ROW.encode("utf-8") + eol
open(LEDGER, "wb").write(new)
post = open(LEDGER, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
print("S5 row appended; ledger now", len(post), "B")
