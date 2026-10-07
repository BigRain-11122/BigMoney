# -*- coding: utf-8 -*-
"""r679 bm-c S5 ledger row append (canonical path per r646 epoch law;
byte-level append, tail EOL gate, count==1 post-verify per r503 v2 law).
Pattern credit: Tools/_r678bmc_s5_ledger.py."""
import datetime as dt
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
TS = dt.datetime.now().astimezone().isoformat(timespec="seconds")
ROW = (
 TS + " | r679 bm-c | dept:工程/舰队（金周尾日值守轮·复市前夜窗 T-1） | "
 "当前活: r679 值守轮（S0 轮首脏 6=自家 daemon live-face→absorb commit b980e255d〔r620 律·落后 origin 0 无需 rebase〕·S0.5 双扫×2=DEC 4C32527B/ORD A8B02C8A 双零 delta〔轮首+收口两腿全零新面〕+fleet orders 166/166 零未回执+inbox 0 未读·S1 48/48·S3 SAT 活 rc0〔alive_flag=true·burns_active=[]·queue_next=[]=O-2115 §2 N1 收口维持〕+水位红牌 red=false·probe verdict py_low_with_work_cands=§四诚实披露〔候选=S6 链自身在飞腿 top_proc_cores 1.07≥0.5 核阈值自检面·update_lhb 拉取窗口·非未认领批；板 0 open+bandit 0+burns 队空=合法 idle 白名单成立·金周无 bar〕+板 0 open+job_list 0+post_review 45Y/0N/5W 零红零 P0+试用劳力线不触发〔O-2115 §2 N1 收口维持+fund-trio D 族 bm-b 在飞 eta~10-08+金周无 bar+W174 席 bm-a 已发布=下 freezer 再 derive 义务已由 bm-a 席链消耗 per r822 note〕·S6 38/38 rc0〔dualrun ZERO-DRIFT streak 51 @404·CA 双旗=[supply_gap,supply_floor]=W174 席位间隙窗延续〔pool ready 2<floor 3·unclaimed 0·bm-a freeze+burn 点火后自然清预期·r676/677/678 同族一行不重扫〕·bm-a origin 心跳回鲜〔15-16min〕→9 lane-io 宿主面全 skip derive 自然归还 bm-a〔本环零 stale-takeover 需求·优于 r678 前段腿〕·REPORT-2026-10-07+LIVE-2026-10-07 幂等再生 ORANGE·fund_premium pre-15:30 no-op〔bm-c 车道 10-08 15:30 首采就绪〕·regime_guard v3 enforce 请求→诚实 shadow 降级〔首 bar 激活 10-08〕·token_meter 落盘〕·S4 零新坑零主件 append〔三克隆件 s05/s6/qa_ignite 裸数字律全过·QA ignite 首行轮标 r679 正确〕·QA r679 5/5 零误标〔显式 --round 679 detached pid 36468 终态轮询过门·93 trades·determinism=True·equity 终值 1,017,839 跨轮面恒等·png 66,161B·latest_panel_bar=2026-09-30 金周 no-op 诚实〕·S7 四自愈件幂等过〔loop pin=5 no-op 首跳 13:55·watchdog 幂等重注册首跳 13:51·precommit/prepush 双爪装 LF 归一〕+tripwire CLEAN〔append 后复扫 E09 律〕+attrition CLEAN〔4 台账·healed 行注记照录〕） | "
 "验证证据: results/_r679bmc_s6_log.txt（38/38 rc0）+qa/smoke-r679.md（5/5·首行轮标 r679 零误标）+qa/equity-curve-r679.png（66,161B）+docs/daily_report/REPORT-2026-10-07.md+docs/live_usage/LIVE-2026-10-07.md（再生 ORANGE）+results/_r679bmc_s05_facts.json（轮首+收口双扫·双零 delta）+results/post_review/REPORT-20261007.md（45Y/0N/5W 零红再生）+results/_attrition_guard_scan.json CLEAN+results/_r679bmc_qa_runner.out（terminal 5/5）+results/watermark.jsonl〔probe 行 py_low_with_work_cands 候选面留痕〕 | "
 "下轮指针: r680=5x HANDOVER 窗（research/HANDOVER.md 核对更新）；10-08（周四）复市首交易日——数据链 re-arm+REGIME_GUARD v3 首 bar enforce 激活+纸盘 marks 地板推进+fund_premium 15:30 首采（bm-c 车道·r671/673/675 就绪核已过）+O-2115 验收包复跑（治理日）；W174 freeze/burn 观望（supply 双旗自然清预期）；trio finalize 窗至 10-09（bm-b 正典道）；月界首考 10-31（T-143 交付 10-29）；每轮收口 tripwire scan（E09 律） | "
 "watermark: 绿（red=false·probe py_low_with_work_cands=S6 链自检面 §四 已披露·板 0 open·SAT 活·post_review 零 ✗） | "
 "本地未达 origin commit 数=2（S0 吸收件+本轮收口件·收口推送后复验）"
)

raw = open(LEDGER, "rb").read()
assert raw.endswith(b"\r\n") or raw.endswith(b"\n"), "tail EOL gate"
guard = "r679 bm-c | dept:".encode("utf-8")
assert raw.count(guard) == 0, "rerun guard"
eol = b"\r\n" if raw.count(b"\r\n") >= 10 else b"\n"
sep = b"" if raw.endswith(eol) else eol
new = raw + sep + ROW.encode("utf-8") + eol
open(LEDGER, "wb").write(new)
post = open(LEDGER, "rb").read()
assert post.count(guard) == 1, "post-verify count==1"
print("S5 row appended; ledger now", len(post), "B")
