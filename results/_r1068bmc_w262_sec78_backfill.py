# -*- coding: utf-8 -*-
"""r1068 bm-c: W262 prereg sec.7/8 backfill (placeholders -> finalize actuals).

Line-targeted replacement; all other lines byte-preserved. Idempotent guard:
runs only when the exact placeholder lines are present.
"""
import io, json

PATH = "research/PERPETUAL_N1_W262_PREREG.md"
PH7 = "- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1067 W261 §7 范式）"
PH8 = "- （占位·finalize 同窗回填：§5.5 W263+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1067 W261 §8 范式）"

NEW7 = (
    "- 账本恒等式：prev 998,535 + batch 2,200 = **1,000,735 EXACT**（science_gates.ledger 机读恒等断言过）；"
    "合并池 K：572,120 + 2,200 = **574,320 EXACT**。\n"
    "- merged mu = -0.09274509 / merged sigma = 0.24503074 / **se_mu@K574,320 = 0.000323**（对照 W261 键 0.000324，窄化续行）；"
    "W262-only mu = -0.09509205 / sigma = 0.24443248。\n"
    "- K-lift 对照：line_pre_w262 = line_merged@574,320 = 1.1952，delta = **0.0**（n_eff held 998,535）；"
    "canon flip = NOT performed by this wave（治理提案面 only，K2200 同律）。\n"
    "- §5 五预键机证：**6/6 ALL PASS**（key1 only-vs-merged gap 0.002347 / key1b merged-vs-W261键 0.0000090 / "
    "key2 sigma rel -0.0010% / key3 A p95 delta +0.0166〔0.2994→0.316，双向带内〕/ key4 K-lift 0.0 held-flat / "
    "key5 se_mu 0.000323≤0.000324 窄化续行）——收据 results/_r1068bmc_w262_fivekeys.json（W261 键=n1_w261_results.json 机读 r587 律）。\n"
    "- 六门探针：PRE-FINALIZE **ALL PASS 第 24 连正确相位**（results/_r1068bmc_w262_sixgate.json——splice 完整性三重恒等 "
    "n1 a3aeec1e8cd0e5f4 worktree==收据 post==落链 git blob @ e1a94b335；banned_direction_gate ADMIT rc0；"
    "pf/n1 selftest rc0；shards 12/12 全 >100KB；seed_admit_gate FREE x2〔base=591701 span=2000 / base=593701 span=200〕；"
    "wave_configs 行四面对齐）。\n"
    "- audit 段：machine=bm-c，finalize_only；shards_consumed 12/12；"
    "preregistered_doc=research/PERPETUAL_N1_W262_PREREG.md；evidence_cutoff=2026-09-22（P-5C 冻结窗同窗律）。"
)

NEW8 = (
    "- §5.5 W263+ 投影承接机证（finalize 产物 preregistered_doc 面机读）：W263 A naive first-clean 593_701..595_700 "
    "CLEAN（hops=0，零活 seed refuser）；B naive 593_901..594_100 hops=0 CLEAN at naive——first-clean **但落 W263 投影 A 窗内**"
    "（staircase re-emergence face 复现预期；seed-gap face 继承）——**W263 freezer 必须在 post-W262 宇宙上重derive 且派生 B 时预留 own-wave A 窗**"
    "（勿假设 A-base==prior-B-tail+1 或 B-base==own-A-tail+1 相等式）；**W263 seat = bm-a 窗口**（链条序；bm-a yield note + registration watch 已见 32d28ffb3）。\n"
    "- 宝藏与方法论捕获问：本批零新宝藏入册；builder P5e 配对字面 off-by-one roll（W259_W260_W262 误写）被 count-asserted "
    "OUTPUT-GATE fail-closed 0!=1 当场拦截（拼接前自愈 W259_W260_W261 收据逐字）=机制按设计执法，非新坑（E63 邻族披露）；"
    "五钥匙/六门首跑全过零返工。\n"
    "- 诚实披露面：(1) **第 58 代吸收续行**——拼接+引擎自烧+六门+finalize 由死窗（17:17-17:23，自标 r1068）执行，"
    "本窗（17:25 发射）落地前机验遗产（六门收据复读+finalize 台账恒等 EXACT+merged K EXACT+分片 12/12）后补五钥匙+sec.7/8；"
    "(2) 拼接 commit e1a94b335 = 死窗工作树字节直落，1 对针脚自愈已披露（builder P5e off-by-one，OUTPUT-GATE 拦截）；"
    "(3) 引擎 mtime-watch 自烧 12/12 分批台账 append（06dcd6c23 六片 + b83318440 六片，经 push-saga rebase 链上链）；"
    "(4) E63 w244_a 老化面 held 未滚动（r1062/r1065 双犯未三犯）；(5) W262=bm-c own-seat 第 82 拥有波，"
    "W261 前链 998,535/K=572,120 机读承接，sec.7/8 占位=0 本窗清零。"
)

with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    raw = f.read()
nl = "\r\n" if "\r\n" in raw else "\n"
lines = raw.split(nl)
assert lines.count(PH7) == 1, "PH7 count=%d" % lines.count(PH7)
assert lines.count(PH8) == 1, "PH8 count=%d" % lines.count(PH8)
i7 = lines.index(PH7)
i8 = lines.index(PH8)
new7_lines = NEW7.split("\n")
new8_lines = NEW8.split("\n")
lines[i7:i7+1] = new7_lines
i8 = lines.index(PH8)  # re-locate after shift
lines[i8:i8+1] = new8_lines
out = nl.join(lines)
with io.open(PATH, "w", encoding="utf-8", newline="") as f:
    f.write(out)

# verify: placeholders zero, backfill faces present
with io.open(PATH, "r", encoding="utf-8", newline="") as f:
    chk = f.read()
assert PH7 not in chk and PH8 not in chk, "placeholders remain"
assert "1,000,735 EXACT" in chk and "574,320 EXACT" in chk and "6/6 ALL PASS" in chk
assert "第 58 代吸收续行" in chk and "W263 seat = bm-a" in chk
print("BACKFILL-OK placeholders=0 sec7_lines=%d sec8_lines=%d nl=%r" % (len(new7_lines), len(new8_lines), nl))
