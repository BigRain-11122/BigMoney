# -*- coding: utf-8 -*-
# r1113 bm-c: W277 prereg content spot-check (r1110 content_check.py precedent; 73-face
# positive panel + 18-face negative panel; run BEFORE the freeze commit; exit 0 = PASS).
import io, sys

REPO = io.open(__file__, encoding="utf-8", newline="").read()  # noqa: F841 (self-read guard)
t = io.open(__file__.rsplit("\\", 1)[0].rsplit("\\", 1)[0] + "\\research\\PERPETUAL_N1_W277_PREREG.md",
           encoding="utf-8", newline="").read()
faces = ['PERPETUAL-N1-W277', 'research/PERPETUAL_N1_W277_PREREG.md', 'A-ext seed=624_701..626_700', 'B-ext exit seed=626_701..626_900',
'624_701..626_700', '626_701..626_900', '624_501..624_700', 'A 624_701..626_700/B 626_701..626_900',
'第二十六次连续 A-hop', '第二十七次连续 above-own-A', '〔第二十六次连续〕',
'626_701..628_700', '626_901..627_100', 'W278p_B_lands_inside_W278p_A_naive=true', 'verify at W278 prereg',
'1,031,535', 'K=605,120', '607,320 投影', '−0.09278451', '0.24508562', '−0.08705886', '（**0.305** 实测锚）', '实差 0.0057 在带内',
'键 W276 实测 K-lift **+0.0001**', 'line_merged@K605,120 **1.1969**', 'line_pre_w276 1.1968', 'n_eff_held_equal 1,029,335',
'→W271 **0.000319**→W272 **0.000319**→W273 **0.000318**→W274 **0.000317**→W275 **0.000316**→W276 **0.000315**→W277 投影 0.000315】',
'MSG-20261019-080x-bmc-w277-seat', 'c5f8b88f91', '770a47fa1f', '354a645155', 'e781164e41', 'df7dedfd07', '627c4e10f2',
'estate chain r1110/r1111 W276 全周期', 'bm-c r1111 W276 §7 范式', 'bm-c r1111 W276 §8 范式',
'注册 W276 B 带 624_501..624_700 落 naive A 窗内', 'refuser band 624_501..624_700〕', 'W278 freezer 承接面强制注记',
'engine_owner==bm-c 95 行注册', 'engine_owner 行 266 注册在册', '第 96 枚', '第 267 波', '池第 275 枚', '波号 277', '零 277 行',
'probe leg0 bmc_rows=95', 'bm-c 循环班 r1112 席位窗 2026-10-19 08:1x', 'r1112 席位窗实跑：origin inbox 零 W277 席位外机命中',
'results/p2cal_ext/n1_w276/ 12/12', 'seed_admit_gate rc0 双带 FREE',
'A_staircase_hop_past_W276_B=true', 'B_lands_above_own_A=true', 'W277=bm-c own-wave window per chain-order law',
'（占位·finalize one-pass 后回填', '（占位·finalize 同窗回填', '07:4x', '07:2x', '08:1x',
'W263 冻结窗 26G bm-a 实锚', '_w277bmc_freeze_edits.py', '_w276bmc_freeze_edits.py 模板派生',
'saturation_engine.py status live-read r1113', '（W276 注册+烧录+finalize 全落地）', '（上游 W276 席位已闭链', 'hops=1', 'hops=0']
miss = [f for f in faces if f not in t]
print("SPOT-CHECK %d/%d PASS" % (len(faces) - len(miss), len(faces)))
if miss:
    print("MISSING:", miss)
    sys.exit(1)
# negative panel: stale faces that must be consumed (1,029,335 EXEMPT: the single honest
# n_eff_held_equal anchor, pinned-gated count==1)
bad = ['622_501..624_500', '624_501..624_700 1 hop 落位', '注册 W275 B 带', 'refuser band 626_701..626_900',
       'W276p_', '05:2x', '05:3x', '05:5x', 'K=602,920', '第二十五次连续 A-hop', '连续二十五波',
       'bmc_rows=94', '行 265 注册在册', 'r1108 W275', 'fc01636095', '018782314d', 'MSG-20261019-055x']
present = [b for b in bad if b in t]
print("NEGATIVE-CHECK:", "CLEAN" if not present else ("LEAK: %r" % present))
assert t.count("1,029,335") == 1, "n_eff anchor count drift"
assert t.count("1,031,535") == 2, "ledger anchor count drift"
sys.exit(1 if present else 0)
