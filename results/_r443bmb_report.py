import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

line = (
    "2026-09-30T01:06:00+08:00 | r443 bm-b | WM-VERDICT: 绿 red=false @00:54 probe (insufficient_history 窗 n=1 非阻塞·"
    "local_batch_running=true W11 SCREEN/JUDGE 烧批在飞=合法负载) | 当前活: TRIAL-LABOR-W11-JUDGE 烧批在飞 pid16392 "
    "01:04:15 点火（229 存活者全量判决·W10 同型 ~33min ETA ~01:35）| 最近实物: results/trial_labor_w11/w11_screen.json "
    "@01:03 finalize（1462/1462 cells·null p95 0.5148 IN [0.50,0.52]·存活 229/1262=18.15%·RESEARCH FACT: STD 轴首次筛面富集 "
    "std10_hi 24.66%>none 17.59%>std20_hi 12.59% 正10日/负20日不对称·MOM 延续 1.25x 弱于 W10 1.88x·账本 350018 线性）+ "
    "w11_candidates.json n=1262 GENERATE 遗产收编 commit 8d03c4126 + 轮工作 commit 703f2fa48 | 下个里程碑: W11 judge-finalize "
    "落地→intake(D6)→CEO-REPORT-WAVE11 48h 钟（本窗 ~01:35 或下轮 autofill 承接·窗 ≤48h 即 2026-10-02 01:35 内）| did: "
    "(1) S0 轮首脏树取证=死轮遗产非并发（process 探针 3 codely=Phantom/tick/本会话零同仓并发）→ bm-c r243 同法 pre-pull "
    "absorb 收编 31 件（w11_candidates+grammar ledger row+死轮 S6 drift 64/64 parse-verified+x2_watch 追加写吞换行腐败修复 "
    "1800 对象零丢失）→ pull --rebase 撞 31-UU=classifier 31/31 零 UNKNOWN→r442 resolver 机制复用（rolling-ledger union "
    "compute_audit 201+201→203·regime_state 3+3→3·append-log union x2_watch 1805+1800→1814+post_review 3807+3780→3856·"
    "snapshot take-new R350-hardened 26 面 paper bar 数监督零 stale）→ **r444 fork-point 律命中：continue 前 fetch 发现 origin "
    "越基点（cb4734950→eab3a15f3 bm-a r450-close 风暴窗）→abort 后 --onto 显式重放零丢失**→push PASS 8d03c4126；"
    "(2) screen-prep PASS（panel 48/48+census 冻结）→池双面翻（GENERATE=done+SCREEN ready armed）→手动 tick 点火 pid14156 "
    "00:53:27→1462/1462 烧完 10min→screen-finalize 落地（上列判面）→judge-prep PASS（manifest 48·STD meta 120-bar warmup "
    "1511 decidable）→JUDGE armed+host_gates 5383 parquet 验过→01:00 tick 认领 push 撞拒 yield（committed=True 本地保留）→"
    "会话 S7 收编 commit+push 后 01:04 二次 tick 自续认领点火成功 pid16392（r282 fill-latency 律自愈面）；(3) S6 37 腿："
    "全 rc=0 除 update_lhb rc=3 源改史隔离（r229 族第 3 观察零本地写·42→67 行翻面级重述+107.6M→-117.4M 净买额整段重述=旗标"
    "隔离正确）；astock refresh 锁活 in-flight（r440 pid20888 续）；rev_osc 面板 cutoff 09-28 未齐=等 astock 完备诚实 no-op；"
    "scorecard/daily_scorecard/t35_verify=bm-a 心跳 31-33min 陈旧合法 stale-takeover（O-2100 s2.4 STALE_MIN 律）；LIVE/REPORT-"
    "20260930 新鲜落盘（ORANGE cap50）；(4) S0.5 令差集 122/122 零新令+decisions.md 不在本机零动作；(5) S1 smoke 26/26；"
    "(6) S7：attrition guard scan CLEAN（4 ledgers 含 bm-a r450 修复后历史 shrink 全 healed）+loop 任务在跑+watchdog 就绪+"
    "claw OK+inbox MSG slot-4 berth 处理（bm-b 本轮 W11 满载不 adopt·bm-c 下轮自续·processed 归档）| verify: 候选批 grammar "
    "sha16==FROZEN 针 128962592feeb8d3 断言过+selftest prep/finalize 判面 stdout 实读+账本 350018 线性（348556+1462）+guard "
    "scan rc0+smoke 26/26+dualrun ZERO-DRIFT streak 31/3+push 三段全落（8d03c4126/35b42f00e 认领/703f2fa48）| next: 收 judge "
    "finalize（本窗或下轮）→w11_judge.json G1'v2/G2/DSR/PBO 判面→intake D6→CEO-REPORT-WAVE11 48h 钟→W12 prereg 供结带 "
    "（null p95 0.5148 入 W1-W11 谱系表+STD 轴筛面发现注记） [via bm-b]\n"
)
with open("logs/iteration-loop/round_reports.md", "a", encoding="utf-8") as f:
    f.write(line)
print("round report appended", len(line), "bytes")
