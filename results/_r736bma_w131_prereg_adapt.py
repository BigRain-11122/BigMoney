# -*- coding: utf-8 -*-
"""r736 bm-a W131 per-wave prereg: verbatim-adapt research/PERPETUAL_N1_W130_PREREG.md
-> research/PERPETUAL_N1_W131_PREREG.md. Needle-asserted (fail-fast, counts
verified against the W130 source text); sec7/sec8 reset to placeholders
(the W130 file carries the r736 finalize backfill -- W131 starts empty)."""
import io

SRC = "research/PERPETUAL_N1_W130_PREREG.md"
DST = "research/PERPETUAL_N1_W131_PREREG.md"

t = io.open(SRC, encoding="utf-8").read()

def rep(t, pairs):
    for old, new, expect in pairs:
        n = t.count(old)
        assert n == expect, "needle count=%d expect=%d: %r" % (n, expect, old[:70])
        t = t.replace(old, new)
    return t

t = rep(t, [
    ("# PERPETUAL-N1-W130 预注册", "# PERPETUAL-N1-W131 预注册", 1),
    ("泵第 128", "泵第 129", 1),
    ("第一百二十枚引擎波", "第一百二十一枚引擎波", 2),
    ("第四十六枚自有波〔r735〕", "第四十七枚自有波〔r736〕", 1),
    ("engine_owner 行 119+本候选", "engine_owner 行 120+本候选", 2),
    ("波号 130=注册表 W129 行后首个自由号", "波号 131=注册表 W130 行后首个自由号", 1),
    ("〔本冻结窗 fetch 实核表尾时 W130 号位净空", "〔本冻结窗 fetch 实核表尾时 W131 号位净空", 1),
    ("＋全 inbox/processed/ W130 席位零外机命中", "＋全 inbox/processed/ W131 席位零外机命中", 1),
    ("**单态零席位空档**：W116=bm-b r677 freeze（bc1e82773）+W117=bm-a r683 freeze（c36a087ea）+",
     "**单态零席位空档**：W117=bm-a r683 freeze（c36a087ea）+W118=bm-b r678 freeze（565e5b0b4）+", 1),
    ("+W129=bm-a r734 freeze（5e8d140ef·表尾）**均已注册**（表尾=W129 行）·W130=无 skip-past-published 链面",
     "+W130=bm-a r735 freeze（0b8b308db·表尾）**均已注册**（表尾=W130 行）·W131=无 skip-past-published 链面", 1),
    ("本机席位公示=MSG-2026-10-05-1658-bma-w130-seat 已推 origin 02e151b0a 先于本冻结 r565 律",
     "本机席位公示=MSG-2026-10-05-1726-bma-w131-seat 已推 origin fde20e3a1 先于本冻结 r565 律", 1),
    ("ADMIT 回执=results/_r735bma_w130_band_gate.py 单态门全腿实跑·pre-seat probe results/_r735bma_w130_probe.py 先跑·双窗 derive 恒等）",
     "ADMIT 回执=results/_r736bma_w131_band_gate.py 单态门全腿实跑·pre-seat probe results/_r736bma_w131_probe.py 先跑·双窗 derive 恒等）", 1),
    ("results/_r735bma_w130_band_gate.py rc0 实跑", "results/_r736bma_w131_band_gate.py rc0 实跑", 1),
    ("pre-seat 机证=results/_r735bma_w130_probe.py rc0（ADMIT-derive·回执 results/_r735bma_w130_probe_receipt.txt）",
     "pre-seat 机证=results/_r736bma_w131_probe.py rc0（ADMIT-derive·回执 results/_r736bma_w131_probe_receipt.txt）", 1),
    ("冻结窗 gate 重跑 derive 逐位恒等（A 303_004..305_003 hops 0·B 68_502..68_701 hops 1——B 算术窗 68_401..68_600 拒收点=SEED_REGISTRY **68_500 t19_phantom_p1 + 68_501 perpetual_n4_b1**〔D-20261002-05 越 hit 起窗钉死语义〕·终窗 CLEAN）",
     "冻结窗 gate 重跑 derive 逐位恒等（A 305_004..307_003 hops 0·B 68_702..68_901 hops 0——双 CLEAN 算术续带窗·零拒绝点·终窗 CLEAN）", 1),
    ("**席位推送窗实录**（r735 窗口实况）：席位+probe+回执三件单 commit 推送=**零 UU 净推**（fetch 实核 behind 0·无竞态窗·DELIVERED 02e151b0a）",
     "**席位推送窗实录**（r736 窗口实况）：席位+probe+回执三件单 commit 推送=**首推撞拒 origin 前进 3 commit（r524 落后信号·bm-c r559 同窗波）→merge-mode 零 UU 收口→DELIVERED fde20e3a1（送达 commit d09d5fe6a）**", 1),
    ("**A-ext seed=303_004..305_003**（**A 面算术续带**==W129 行 A 尾 303_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=68_502..68_701**（**B 面越 hit 起窗带**==W129 行 B 尾 68_400+1 算术窗 68_401..68_600 拒收（拒绝事实=SEED_REGISTRY 68_500 t19_phantom_p1+68_501 perpetual_n4_b1 两点·D-20261002-05 越 hit 起窗·hops=1）→首净窗 **68_502..68_701**）·与 r734 W129 gate-tail W130+ 投影逐位收敛=跨窗交叉验证（r587 律·拒绝事实本窗机证披露=W129 §8 遗留指针的承诺兑现）",
     "**A-ext seed=305_004..307_003**（**A 面算术续带**==W130 行 A 尾 305_003+1 起·步长 2_000·CLEAN 零拒绝点·refusal hops=0）；**B-ext exit seed=68_702..68_901**（**B 面算术续带**==W130 行 B 尾 68_701+1 起·步长 200·CLEAN 零拒绝点·refusal hops=0·双 CLEAN 窗）·与 r735 W130 gate-tail W131+ 投影逐位收敛=跨窗交叉验证（r587 律·W130 §8 遗留指针的承诺兑现）", 1),
    ("**W1..W129 N1 finalize 已全部落账**〔W128 finalize one-pass bm-a r734+W129 finalize one-pass 同窗 bm-a r735·§7 回填同 commit 在场〕——净账本链头 **679,811**（W129 finalize 落账·K=281,720 合并池·voids LOWAMP-P1/P2）",
     "**W1..W130 N1 finalize 已全部落账**〔W129 finalize one-pass bm-a r735+W130 finalize one-pass 同窗 bm-a r736·§7 回填同 commit 在场〕——净账本链头 **682,011**（W130 finalize 落账·K=283,920 合并池·voids LOWAMP-P1/P2）", 1),
    ("累计 null 池投影=281,720+2,200（本波）=**283,920 投影**", "累计 null 池投影=283,920+2,200（本波）=**285,520 投影**", 1),
    ("本机 r734 收口指针 W129 gate-tail「W130+ 投影 A CLEAN/B hops=1」=表尾后新首个自由号自领",
     "本机 r735 收口指针 W130 gate-tail「W131+ 投影 A CLEAN/B hops=0 双 CLEAN」=表尾后新首个自由号自领", 1),
    ("T-2026-10-01-141 s1 引擎线第 120 波·bm-a 第四十六枚自有波〔机面 derive：engine_owner==bm-a 行 45+本候选·以 gate leg0 机证为准·含 W127/W128/W129 最近自有波〕",
     "T-2026-10-01-141 s1 引擎线第 121 波·bm-a 第四十七枚自有波〔机面 derive：engine_owner==bm-a 行 46+本候选·以 gate leg0 机证为准·含 W128/W129/W130 最近自有波〕", 1),
    ("第四十六枚自有波", "第四十七枚自有波", 1),  # remaining ordinal-anchor note occurrence (title + claim-section needles ran first)
    ("engine_owner==bm-a 行 45+本候选·gate leg0 机证在场", "engine_owner==bm-a 行 46+本候选·gate leg0 机证在场", 1),  # ordinal-anchor note row count
    ("（波号=注册表 W129 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1658-bma-w130-seat 先推 origin 02e151b0a r565 律〕；lane-free；部门 dept:研究）",
     "（波号=注册表 W130 行后首个自由号·单态零席位空档〔席位公示=MSG-2026-10-05-1726-bma-w131-seat 先推 origin fde20e3a1 r565 律〕；lane-free；部门 dept:研究）", 1),
    ("entry rng seed=**303_004+j**（法典 §4 W130 行 A=303_004..305_003·**算术续带**==W129 行 A 尾 303_003+1 起",
     "entry rng seed=**305_004+j**（法典 §4 W131 行 A=305_004..307_003·**算术续带**==W130 行 A 尾 305_003+1 起", 1),
    ("exit rng=**68_502+j**（法典 §4 W130 行 B=68_502..68_701·**越 hit 起窗带**==W129 行 B 尾 68_400+1 算术窗 68_401..68_600 拒收〔拒绝事实=SEED_REGISTRY 68_500 t19_phantom_p1+68_501 perpetual_n4_b1·D-20261002-05 越 hit 起窗·hops=1〕→首净窗 CLEAN·与 r734 gate-tail 投影逐位收敛·ADMIT 回执在场）",
     "exit rng=**68_702+j**（法典 §4 W131 行 B=68_702..68_901·**算术续带**==W130 行 B 尾 68_701+1 起·步长 200·CLEAN 零拒绝点·hops=0·双 CLEAN 窗·与 r735 gate-tail 投影逐位收敛·ADMIT 回执在场）", 1),
    ("entry rng=**303_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）",
     "entry rng=**305_004+j**（与 A[j] 同源配对语义逐字·runner 实证 entry=A_SEED_BASE+j）", 1),
    ("W130 带与 v1 在用带", "W131 带与 v1 在用带", 1),
    ("W2..W129 在用带（**全注册·单态**）", "W2..W130 在用带（**全注册·单态**）", 1),
    ("selftest W130 face（A 算术窗净腿+B 越拒收点起窗净腿〔拒绝事实机证=恰 68_500/68_501 两点〕+W129 行 parity 腿）",
     "selftest W131 face（A 算术窗净腿+B 算术续带净腿〔双 CLEAN 窗·零拒绝点〕+W130 行 parity 腿）", 1),
    ("本波机验 ADMIT 回执在场=r735 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）",
     "本波机验 ADMIT 回执在场=r736 bm-a 冻结窗（pre-seat probe 先跑·双窗 derive 恒等）", 1),
    ("起草窗实测 W1..W129 已落账 281,720 实测", "起草窗实测 W1..W130 已落账 283,920 实测", 1),
    ('batch_name="PERPETUAL-N1-W130", batch_trials=2200, file_name="results/perpetual_faces/n1_w130_results.json"',
     'batch_name="PERPETUAL-N1-W131", batch_trials=2200, file_name="results/perpetual_faces/n1_w131_results.json"', 1),
    ("**W1..W129 N1 finalize 已全部落账**——净账本链头 679,811=W129 finalize 落账〔one-pass·bm-a r735·§7 回填同 commit 在场〕·**K=281,720 合并池**",
     "**W1..W130 N1 finalize 已全部落账**——净账本链头 682,011=W130 finalize 落账〔one-pass·bm-a r736·§7 回填同 commit 在场〕·**K=283,920 合并池**", 1),
    ("本波 §5 预测键=**W129 finalize 实测值**〔results/perpetual_faces/n1_w129_results.json·N1 面最新已落账键〕",
     "本波 §5 预测键=**W130 finalize 实测值**〔results/perpetual_faces/n1_w130_results.json·N1 面最新已落账键〕", 1),
    ("1. W130-only mu 与累计池 merged mu（W129 实测键 **−0.092716**·K=281,720 合并池·W129-only 实测 **−0.085087**）差异 **|Δ|<0.02**（W2..W129 共三十+面实测 mu 稳定先例·单波跨键律）",
     "1. W131-only mu 与累计池 merged mu（W130 实测键 **−0.092774**·K=283,920 合并池·W130-only 实测 **−0.100175**）差异 **|Δ|<0.02**（W2..W130 共三十+面实测 mu 稳定先例·单波跨键律）", 1),
    ("键 **0.244918**=W129 合并池实测）", "键 **0.244947**=W130 合并池实测）", 1),
    ("3. A 档 full_sharpe_p95 与 W129 A 档 p95（**0.3223** 实测锚）差 **<0.05**（门标准注记法 W5..W129 先例",
     "3. A 档 full_sharpe_p95 与 W130 A 档 p95（**0.3256** 实测锚）差 **<0.05**（门标准注记法 W5..W130 先例", 1),
    ("W3..W129 先例·W125 −0.0001/W126 −0.0002/W127 +0.0003/W128 +0.0003/W129 **+0.0002** 正负交替如实报正负）；键 W129 实测 K-lift **+0.0002**（line_merged@K281,720 **1.1764**·line_pre 1.1762·n_eff 677,611；se_mu 收窄链 W126 0.000467→W127 0.000465→W128 0.000463→W129 **0.000461**）",
     "W3..W130 先例·W126 −0.0002/W127 +0.0003/W128 +0.0003/W129 +0.0002/W130 **+0.0001** 正负交替如实报正负）；键 W130 实测 K-lift **+0.0001**（line_merged@K283,920 **1.1767**·line_pre 1.1766·n_eff 679,811；se_mu 收窄链 W127 0.000465→W128 0.000463→W129 0.000461→W130 **0.000460**）", 1),
    ("5. **W131+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 305_004..307_003 **CLEAN**（hops=0）；B first-clean **68_702..68_901** **CLEAN**（hops=0·双 CLEAN 窗）（r735 冻结窗 gate 回执尾行·与本席位 MSG W131+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）",
     "5. **W132+ 投影（gate 机证·下波冻结方必复核非转抄）**：A 307_004..309_003 **CLEAN**（hops=0）；B first-clean **68_902..69_101** **CLEAN**（hops=0·双 CLEAN 窗）（r736 冻结窗 gate 回执尾行·与本席位 MSG W132+ 投影披露交叉验证一致=自机 derive 非转抄 r587 律）", 1),
    ("selftest/status/run --shard k --of 12 --wave 130/finalize --wave 130", "selftest/status/run --shard k --of 12 --wave 131/finalize --wave 131", 1),
    ("results/p2cal_ext/n1_w130/shard-<k>-of-12.json", "results/p2cal_ext/n1_w131/shard-<k>-of-12.json", 1),
    ("results/perpetual_faces/n1_w130_results.json`（finalize 合并件", "results/perpetual_faces/n1_w131_results.json`（finalize 合并件", 1),
    ("（engine_owner==bm-a 45 行注册+本候选〔以 gate leg0 机证为准·含 W127/W128/W129 最近自有波〕）",
     "（engine_owner==bm-a 46 行注册+本候选〔以 gate leg0 机证为准·含 W128/W129/W130 最近自有波〕）", 1),
    ("finalize 链序前置=**起草窗零在飞上游（W1..W129 全落账）**", "finalize 链序前置=**起草窗零在飞上游（W1..W130 全落账）**", 1),
])

# --- sec7/sec8 reset to placeholders (W130 file carries the r736 finalize backfill) ---
i7 = t.find("## §7 跑后实证。【finalize")
i_end = t.find("- **跑前冻结=本件 commit**")
assert 0 < i7 < i_end, (i7, i_end)
t = t[:i7] + "## §7 跑后实证。【占位·finalize 收口机械回填】\n\n## §8 批后复盘。【占位·跑前为空·终 7-T】\n\n" + t[i_end:]

# residual audit: remaining W129 mentions must all be legitimate chain-history references
import re
res_w129 = [ln[:90] for ln in t.splitlines() if "W129" in ln]
res_w130 = [ln[:90] for ln in t.splitlines() if "W130" in ln]
print("residual W129 lines (%d):" % len(res_w129))
for ln in res_w129: print("  |", ln)
print("residual W130 lines (%d):" % len(res_w130))
for ln in res_w130: print("  |", ln)

io.open(DST, "w", encoding="utf-8", newline="\n").write(t)
print("W131 prereg written: %d chars" % len(t))
