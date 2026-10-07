# -*- coding: utf-8 -*-
"""r678 bm-c S5 ledger row append (canonical path per r646 epoch law;
byte-level append, tail EOL gate, count==1 post-verify per r503 v2 law).
Pattern credit: Tools/_r677bmc_s5_ledger.py."""
import datetime as dt
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
TS = dt.datetime.now().astimezone().isoformat(timespec="seconds")
ROW = (
 TS + " | r678 bm-c | dept:工程/舰队（金周尾日值守轮·复市前夜窗） | "
 "当前活: r678 值守轮（S0 轮首脏 6=自家 daemon live-face→absorb commit b6d63374d〔r620 律·rebase 1/1 干净〕+pull --rebase 落后 5→0〔bm-b r802/803 estate+autofill ticks 收编〕·S0.5 轮首扫 DEC 4C32527B/ORD A8B02C8A 双零 delta〔r677 收口 catch 水位已消费·零新面〕+fleet orders 166/166 零未回执+inbox 0 未读·S1 48/48·S3 SAT 活 rc0〔alive_flag=true·hb 46s·burns_active=[]·queue_next=[]=O-2115 §2 N1 收口维持〕+水位红牌 red=false lane healthy〔py_low_board_clear 合法 idle·金周无 bar〕+板 0 open+job_list 0+post_review 45Y/0N/5W 零红零 P0+试用劳力线不触发〔O-2115 §2 N1 收口维持+fund-trio D 族 bm-b 在飞 eta~10-08+金周无 bar+W174 席 bm-a 已发布=下 freezer 再 derive 义务已由 bm-a 席链消耗 per r822 note〕·S6 38/38 rc0〔dualrun ZERO-DRIFT streak 51 @404·CA flags=[supply_gap,supply_floor]=W174 席位间隙窗延续〔20 样本·span 226.8min·bm-a freeze+burn 点火后自然清预期〕·bm-a origin 心跳回鲜〔8min〕→t35_paper_export/daily_scorecard/build_status 三宿主面 skip derive 自然归还 bm-a〔r366 stale-view veto〕·前段腿（scorecard/live_paper/t35_open_fill/t24 对）本地陈视图 59-60min→stale-takeover derive by bm-c〔O-2100 s2.4 设计态〕·update_lhb no-op <30min 距 r677 季批·REPORT-2026-10-07+LIVE-2026-10-07 幂等再生 ORANGE·fund_premium pre-15:30 no-op〔bm-c 车道 10-08 15:30 首采就绪〕·regime_guard v3 enforce 请求→诚实 shadow 降级〔首 bar 激活 10-08〕〕·S4 零新坑零主件 append〔三克隆件 s05/s6/qa_ignite 裸数字律全过·QA ignite 首行轮标 r678 正确〕·QA r678 5/5〔显式 --round 678 detached pid 22288·93 trades·determinism=True·equity 终值 1,017,839 跨轮面恒等·png 66,170B·latest_panel_bar=2026-09-30 金周 no-op 诚实〕·S7 四自愈件幂等过〔loop pin=5 no-op 首跳 13:35·watchdog 幂等重注册首跳 13:35·precommit/prepush 双爪 MATCH〕+tripwire CLEAN〔append 后复扫 E09 律〕+attrition CLEAN〔4 台账·healed 行注记照录〕） | "
 "验证证据: results/_r678bmc_s6_log.txt（38/38 rc0）+qa/smoke-r678.md（5/5·首行轮标 r678 零误标）+qa/equity-curve-r678.png（66,170B）+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（再生 ORANGE）+results/_r678bmc_s05_facts.json（轮首+收口双扫）+results/post_review/REPORT-20261007.md（45Y/0N/5W 零红）+results/_attrition_guard_scan.json CLEAN+results/_r678bmc_qa_runner.out（terminal 5/5） | "
 "下轮指针: 10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce 激活+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道·r671/673/675 就绪核已过）+O-2115 验收包复跑（治理日 scripts/o2115_acceptance_pack.py run）；W174 freeze/burn 观望（bm-a 心跳本轮回鲜=supply 双旗自然清早期信号）；trio finalize 窗至 10-09（bm-b 正典道）；月界首考 10-31（T-143 交付 10-29）；下个 5x=r680（HANDOVER 窗）；每轮收口 tripwire scan（E09 律） | "
 "watermark: 绿（red=false lane healthy·py_low_board_clear 合法 idle·板 0 open·SAT 活·post_review 零 ✗） | "
 "本地未达 origin commit 数=2（S0 吸收件+本轮收口件·收口推送后复验）"
)

raw = open(LEDGER, "rb").read()
assert raw.endswith(b"\r\n") or raw.endswith(b"\n"), "tail EOL gate"
guard = "r678 bm-c | dept:".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
sep = b"" if raw.endswith(eol) else eol
new = raw + sep + ROW.encode("utf-8") + eol
open(LEDGER, "wb").write(new)
post = open(LEDGER, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
print("S5 row appended; ledger now", len(post), "B")
