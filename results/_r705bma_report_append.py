"""r705 bm-a: append round-report line (S5 ledger, byte-safe UTF-8)."""
LINE = (
    "2026-10-05T01:2x+08:00 | r705 (bm-a) | dept:研究:N2-W15 judge 链 step-1 落地轮 | "
    "watermark=green (red=false; satengine alive rc0 idle queue0; S6 38/38 rc0 "
    "dualrun ZERO-DRIFT streak 5; compute_audit FLAG:supply_gap=判后瞬态[11 ready "
    "judge 分片待 autofill 认领点火·非停摆]) | 当前活: N2-W15 judge 12 分片池面烧录窗已开"
    "（本机+机队 autofill claim-to-saturation·trio NULLS bm-b 侧照烧·W3 judge bm-c 探针 "
    "ETA 02:00 值守）| 最近实物: results/n2_w15/n2_w15_judge_state.json 01:10:23 "
    "(judge-prep PASS 188s·N_judge=281 定格·塌缩 eliminated 0·seed 545_500)+池 12 条 "
    "PERPETUAL-N2-W15-JUDGE-SHARD-0..11 入池 01:1x (r497 范式·403 entries·origin 送达 "
    "自证 ls-tree 2/2) | 下个里程碑: 12 judge 分片烧录+judge-finalize 判决（窗 "
    "≤10-08 治理日前·§9.1 排产锚 ≤10-12 全线）| 收据: MSG-0100-bmb-ALL 已消费（下游分工"
    "接 step-1·回执 MSG-0125-bma-ALL 已上 origin）；MSG-0042-bmc-ALL 已读（bm-c tailscale "
    "链接待 CEO 一次点击=https://login.tailscale.com/a/13ac0ce1015dd3·名册翻面权归 bm-a "
    "候 CEO 点击后执行窗）| 本地未达 origin commit 数=0（push 后 fetch+rev-list 双向 0 "
    "自证）| 集成披露: 本轮首推被 pre-push 爪正确拦截（本机 commit 基座陈旧缺 bm-c r505 "
    "4 commits·零 --no-verify）→ r501①/r507 净路 rebase 集成（18 UU 确定性再生态取本机"
    "新侧+x2_watch_log 双跑行 r630 union 零丢失断言 PASS·churn-absorb-4 被 daemon 新态"
    "自然取代）→ 推送过爪达 origin\n"
)
path = "round_reports-bm-a.md"
raw = open(path, "rb").read()
eol = b"\r\n" if b"\r\n" in raw[-500:] else b"\n"
if not raw.endswith(eol):
    raw += eol
raw += LINE.encode("utf-8")
open(path, "wb").write(raw)
print("appended; new size:", len(open(path, "rb").read()))
