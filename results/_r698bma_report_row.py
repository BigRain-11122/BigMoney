# -*- coding: utf-8 -*-
"""r698 bm-a: append round report row (EOL-preserving, append-only marker guard
per r679/r645 family)."""
import io

P = "round_reports-bm-a.md"
with open(P, "rb") as fh:
    raw = fh.read()
# detect dominant EOL from tail
crlf = raw.count(b"\r\n")
lf_only = raw.count(b"\n") - crlf
eol = b"\r\n" if crlf >= lf_only else b"\n"
assert raw.count(b"r698 (bm-a)") == 0, "marker already present (double-append guard)"

ROW = (
    "2026-10-04T21:3x+08:00 | r698 (bm-a) | watermark=green (red=false; satengine alive rc0 queue0 idle; "
    "py_watermark py_low_with_work_cands->daemon auto-burn active; compute_audit CLEAN v2.4.2 cpu~4%; "
    "pool dualrun DRIFT $.entries[379].done_at missing-left = 378->390 enrollment observation-phase data, "
    "streak reset recorded honestly) | "
    "当前活: N2-W15 SCREEN 12 分片三机并行烧录——本机 SHARD-1 已烧完翻面 done（97/97 格·21:26:04），"
    "daemon 自动续认领剩余分片（SHARD-2 竞速让路 bm-b claim_lost_yield 正确）；W3 judge finalize bm-c 在飞"
    "（ETA ~22:1x·--live 探针已就绪 _r693bma_w3_adopt_probe.py）；CONTEST-RC bm-b 重认领在烧 | "
    "最近实物: results/n2_w15/checkpoint/n2_screen_shard_1of12.jsonl（97 格 90,777B·21:24:28 落盘=点火证据）"
    "+ pool SHARD-1 翻面 done_by=bm-a + autofill claim commit 74386194f 已推 + S6 38/38 rc0"
    "（results/_r698bma_s6_log.txt·CEO 面 REPORT/LIVE-2026-10-04/scorecard/dashboard 面板再生）@ 21:2x | "
    "下个里程碑: (1)N2-W15 screen 12 分片烧完→screen-finalize→judged verdict（窗≤48h·今晚起）；"
    "(2)W3 judge 产物落地收口+CEO 48h 钟兜算（今晚 ~22:3x）；"
    "(3)moneyflow 面板刷新落地（21:07 spawn·全宇宙 5222 股·ETA ~00:40）→IC reference batch prereg（bandit next_pick 已指向） | "
    "DONE-1 S0: merge origin 两波零冲突（bm-c r497 enrollment 378->390 wave + bm-b r695/claims wave·"
    "daemon-treadmill r437-4 merge-over-rebase 律）；本机零并发会话（r643 三证：reflog 干净/进程单/inbox 闪变无） | "
    "DONE-2 S0.5: orders 154/154 双扫（轮首+S7 收尾）零未回执（r477 全名同形态）+ D-19 decisions/orders 双键 MATCH"
    "（4E5BE321 经 Tools/d19_check.py 正典·Desktop 实径 GROUP=ROOT/../..自动命中）+ inbox 0 未读 | "
    "DONE-3（主产出·计 2）: N2-W15 screen SHARD-1 全链=pool 同步 390 基座（本机池视图停在 378 旧基座·fetch+merge 修复）"
    "->daemon 21:22 认领（anti-double 门过）->runner pid 69880 8-worker BelowNormal 烧录 97 格"
    "->checkpoint 97/97 行（r670 扫描器配对律非空 payload）->21:26:04 翻面 done+harvest 字段；"
    "SHARD-2 认领竞速 bm-b origin-first 21:26:27 -> 本机让路（claim_lost_yield·r648 让路律零双烧） | "
    "DONE-4 S1: smoke 48/48 PASS 0 FAIL | "
    "DONE-5 S3: satengine alive rc0（heartbeat 55s）+ 任务板 0 open 票 + watermark next_pick=claimed"
    "（moneyflow IC reference batch·面板刷新在途 throttle 21:07 spawn 诚实 no-op） | "
    "DONE-6 S6: 38/38 rc0 110s（_r698bma_s6_chain.py==canon _r433bmc parity PASS·golden-week 无新 bar 各腿诚实 no-op·"
    "CALL-2026-09-30 ORANGE_COOL sleeves4 activated0·live.paper/t35/t24/aggr/grid/system_v1 纸盘面全过·"
    "t35_export 2026-09-30 traders6 pos18 equity 5,998,496·token L2 12944+29433） | "
    "DONE-7 S7: 自愈 4/4（loop pin8 no-op+watchdog -Force 重注册+双 claw LF 归一重装）+ attrition guard CLEAN 4 账本"
    "（healed 2+4+1 行照录）+ state 697->698 绝对值写+reparse 自证 + heartbeat epoch int 1791120724 自证 clock T 格式 | "
    "计分: 2（可跑/能看实物=screen 分片真烧录 97 格+checkpoint+池翻面+CEO 面板全再生——供给链消费增量） | "
    "记账预算: 5/5（state+心跳+轮报+orders 双扫+自愈扫描） | "
    "本地未达 origin commit 数: 0（absorb+merge 后 push_verify 自证） | "
    "承接判定: 本批无新方法论（screen=W14 same engine face 先例机器复用·generate bm-c 烧录正主·本机纯算力分片贡献） | "
    "宝藏捕获: 无（判决批未落地——W3 finalize bm-c 在飞非本机收口窗；screen-finalize 未到） | "
    "坑例捕获: 无新坑（state round_no 字符串形态按 r697 律件内约定写·断言防呆改型自愈；D-19 正典探针 Desktop 实径"
    "候选命中=GROUP_CANDIDATES ROOT/../.. 布局面，r697 实径坑未复发） | "
    "下轮指针: (1)screen 剩余分片 daemon 自动续烧+12/12 齐→screen-finalize 观察（bm-c 席位/bm-b 复核权 MSG-1845）；"
    "(2)W3 产物首查 python results/_r693bma_w3_adopt_probe.py --live->ADOPTION_READY->收口 commit+CEO 48h 钟；"
    "(3)moneyflow 面板落地->IC reference batch prereg 起草（bandit 指针·T-167 判决批族谱系）；"
    "(4)trio NULLS finalize watch 10-05..09（bm-b canonical）；(5)W117 finalize on W116 landing（bm-b RAM 闸）"
)

with open(P, "ab") as fh:
    if not raw.endswith(b"\n"):
        fh.write(eol)
    fh.write(ROW.encode("utf-8") + eol)

# verify append-once + reparse-safe
with open(P, "rb") as fh:
    raw2 = fh.read()
assert raw2.count(b"r698 (bm-a)") == 1, "marker count must be 1 after append"
print("round report row appended (eol=%r, marker=1)" % eol)
