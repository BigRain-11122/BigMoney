# -*- coding: utf-8 -*-
"""r1077 bm-c: W264 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Idempotent guard:
runs only when the exact placeholder lines are present.
Clone lineage: _r1039bma_w263_sec78_backfill.py (canon).
"""
import io

PATH = "research/PERPETUAL_N1_W264_PREREG.md"
PH7 = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-a r1039 W263 §7 范式）"
PH8 = "- （占位·finalize 同窗回填：§5.5 W265+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-a r1039 W263 §8 范式）"

NEW7 = (
    "- 账本恒等式：prev 1,002,935 + batch 2,200 = **1,005,135 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：576,520 + 2,200 = **578,720 EXACT**。\n"
    "- merged mu = -0.09272766 / merged sigma = 0.24504297 / **se_mu@K578,720 = 0.000322**（对照本波冻结键 W263 0.000323，窄化并行续行）；"
    "W264-only mu = -0.08593818 / sigma = 0.24655443。\n"
    "- K-lift 对照：line_pre_w264 = 1.1954 → line_merged@578,720 = 1.1955，delta = **+0.0001**（n_eff held 1,002,935）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同例）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap 0.0067895 / key1b merged-vs-W263键 0.0000259 / "
    "key2 sigma rel +0.00242% / key3 A p95 delta -0.0162【0.3208→0.3046，双向带内】/ key4 K-lift +0.0001 十波内首次正微移 / "
    "key5 se_mu 0.000322≤0.000323 窄化并行）——收据 results/_r1077bmc_w264_fivekeys.json（键=n1_w263_results.json 机读 r587 律·"
    "本波预测键冻结于 W263 实测——W263 finalize 起草窗前已落地·活链头基准）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 26 连续正确相位**（results/_r1076bmc_w264_sixgate.json——splice 完整性 "
    "**CR-normalized 恒等** worktree==落链 git blob @ 216b578b0；banned_direction_gate ADMIT rc0；"
    "pf/n1 selftest rc0【W264 selftest 段 3 枚 un-rolled index token 已由 r1076 窗 heal 落地·minimality proof CR-norm 恒等·收据 _r1076bmc_w264_selftest_heal.json】；"
    "shards 12/12 全 >100KB；seed_admit_gate FREE x2【base=596101 span=2000 / base=598101 span=200】；"
    "wave_configs 行四面【对齐】）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed 12/12；"
    "preregistered_doc=research/PERPETUAL_N1_W264_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
)

NEW8 = (
    "- §5.5 W265+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W264 注册字宙已落地（A 596_101..598_100 + B 598_101..598_300，本波冻结收据"
    "_w264bmc_freeze_receipt.json）——W265 A naive 起点 598_101 将被注册 W264 B 带拒（staircase-affects-A 第十四次连续 A-hop 预期承接兑现）；"
    "B naive 598_301..598_500 CLEAN（hops=0）但落投影 W265 A 窗 598_101..600_100 内——**W265 冻结方必须在 post-W264 宇宙上重 derive 且派生时预留"
    "本波 A 窗 596_101..598_100 + 本波 B 带 598_101..598_300**（勿假设 staircase A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式·E36 卡/W141 先例）；"
    "**W265 seat 按 chain 序=bm-c 自有席**（席位公示候选·probe 承接本窗或下窗）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册零新方法论卡——staircase A/B 双 1-hop 形态连续第十三/十四波如预期复现（在册形态延续非新发现）；"
    "五锁/六门首跑全过零返工。\n"
    "- 诚实披露面：(1) splice 提交经 clean-filter CRLF→LF——六门 gate-1 以 CR-normalized 恒等断言（EOL 表示面差异·零内容差·收据见 sixgate json）；"
    "(2) r1076 窗 finalize 两度被会话击杀（0B log ×3 证据件 _r1076bmc_w264_finalize_log{,2}.txt/_err.txt）——finalize+五锁+回填由 r1077 存活窗收口"
    "（W264 selftest heal+六门第 26 连续由 r1076 窗落）；(3) 本波预测键冻结于 W263 实测（起草窗前 W263 finalize 已落地·活链头基准·prereg §5 头注记）。"
)

t = io.open(PATH, encoding="utf-8", newline="").read()
assert t.count(PH7) == 1, "PH7 placeholder count != 1 (idempotent guard)"
assert t.count(PH8) == 1, "PH8 placeholder count != 1 (idempotent guard)"
t2 = t.replace(PH7, NEW7).replace(PH8, NEW8)
io.open(PATH, "w", encoding="utf-8", newline="").write(t2)
print("backfilled: PH7->NEW7, PH8->NEW8; placeholders remaining:",
      t2.count(PH7), t2.count(PH8))
