# r672 bm-a round report line append (append-only, UTF-8, zero console CJK)
import io, os, datetime

RP = r"round_reports-bm-a.md"
now = datetime.datetime.now().astimezone()
ts = now.strftime("%Y-%m-%dT%H:%M:%S+08:00")

line = (
    f"{ts} | r672 (bm-a) | watermark=green (red=false; compute_audit flags=[] CLEAN -- r671 supply_gap "
    "self-resolved with theme burn landed) | 当前活=T-167 THEME-JUDGE-P1 判决批收口补全 | 最近实物="
    "knowledge/TREASURE_REGISTRY.md 判决 finalize 类行 + results/theme_judge_p1/ 判决面五件 (10:26) | "
    "下个里程碑=10-05 fund trio NULLS 烧完→三族 judged finalize (rehearsal ALL-GREEN x3)、piece-4 prereg "
    "trio-gated ETA 10-05..09 | DONE-1: T-167 收口补全 -- finalize redo 幂等复证 (attrition 单条 10:26:19 "
    "d8004/ledger_total 633,981·r259 prev-echo guard 实证) + TREASURE_REGISTRY 判决 finalize 类行补登 "
    "(r670 漏腿·judged_negative 族级诚实关线: 主面 TJ-SOLO-x1 Sharpe 0.2735<同mask随机点火 null μ 0.3734·"
    "skill_line 1.3172 未达·g1/g2/DSR x4 全 fail·PBO 0.4286·M1 t 1.194<3.0·12/20 点火年 cohort 负边→"
    "撤回判定成立·famous 幸存者溢价塌缩 famous +2.65pp vs rest -4.64pp·bl=0.75 深破线变体披露=改道候选面"
    "须另立预注册 E24-ii) + 语法登记簿消费行核验已在册 (r670 已落) | DONE-2: S0.5 orders 153/153 "
    "zero-unacked + D-19 decisions/orders 双 MATCH (per-key sha256 口径·r458 近重犯当场抓回=值长度 64-hex "
    "自证非 SHA-1·探针 _r669bma_d19_check.py) | DONE-3: S0 churn-absorb + merge origin 9 commits zero-UU "
    "(r437 netpath·交集空) + 并发探活仅本会话 (r643 三证) + 轮号取自轮报告表尾 (state.last_round 陈旧 r668 "
    "vs 报表已进 r670/r671 -- 轮号判定以报表 max+1 为准) | DONE-4: S6 37/37 rc0 84.4s (dualrun streak47 "
    "ZERO-DRIFT·fund-statement gate 活证 r671 dash-normalize 修复后 no-op panel-complete 86x3·CALL "
    "ORANGE_COOL sleeves4 activated0·t35 PASS 0 pending·t24 22/22+promotion 0/22 NOT-ELIGIBLE·黄金周 "
    "no-op 族·live.paper skipped r660 先例) | DONE-5: S7 pin8 no-op + watchdog 重注册 + 双爪 MATCH + "
    "attrition CLEAN 4 ledgers + state/heartbeat 程序化写回自证 | 下轮: r673 fund trio NULLS 烧完检查 "
    "(10-05 V-NULLS→三族 judged finalize)、T-166 promotion done-flip 核验、G-SEG 裁决窗 10-06..09、"
    "10-08 开市 dual-jump+治理日、W14 GM-parked 维持 | 本地未达 origin commit 数=0 (push_verify 三证后记)"
)

with io.open(RP, "a", encoding="utf-8", newline="\n") as f:
    f.write(line + "\n")
# verify
t = io.open(RP, encoding="utf-8", errors="replace").read()
assert "r672 (bm-a)" in t, "append failed"
print("ROUND REPORT OK lines:", t.count("\n"))
