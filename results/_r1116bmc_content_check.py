# -*- coding: utf-8 -*-
# r1116 bm-c: W278 prereg content spot-check (r1113 content_check.py precedent rolled one
# generation; 72-face positive panel + 18-face negative panel; run BEFORE the freeze commit;
# exit 0 = PASS). Panel derivation: the r1113 faces rolled one gen; the stamp faces verified
# against the actual md this window (10:3x/09:5x present, 09:0x absent -> dropped; the
# stale 07:4x/07:2x/08:1x consumed -> negative panel).
import io, sys

REPO = io.open(__file__, encoding="utf-8", newline="").read()  # noqa: F841 (self-read guard)
t = io.open(__file__.rsplit("\\", 1)[0].rsplit("\\", 1)[0] + "\\research\\PERPETUAL_N1_W278_PREREG.md",
           encoding="utf-8", newline="").read()
faces = ['PERPETUAL-N1-W278', 'research/PERPETUAL_N1_W278_PREREG.md', 'A-ext seed=626_901..628_900', 'B-ext exit seed=628_901..629_100',
'626_901..628_900', '628_901..629_100', '626_701..626_900', 'A 626_901..628_900/B 628_901..629_100',
'第二十七次连续 A-hop', '第二十八次连续 above-own-A', '〔第二十七次连续〕',
'628_901..630_900', '629_101..629_300', 'W279p_B_lands_inside_W279p_A_naive=true', 'verify at W279 prereg',
'1,033,735', 'K=607,320', '609,520 投影', '−0.09277044', '0.24508694', '−0.08889850', '（**0.3095** 实测锚）', '实差 0.0039 在带内',
'键 W277 实测 K-lift **+0.0000**', 'line_merged@K607,320 **1.197**', 'line_pre_w277 1.197', 'n_eff_held_equal 1,031,535',
'→W272 **0.000319**→W273 **0.000319**→W274 **0.000318**→W275 **0.000317**→W276 **0.000316**→W277 **0.000314**→W278 投影 0.000314】',
'MSG-20261019-102x-bmc-w278-seat', 'b187aa6214', 'e0bc4a0ddd', '9e53371814', '0502c722ac', '0df07c846b', '644b4f8459',
'estate chain r1113/r1114-continuation W277 全周期', 'bm-c r1114-continuation W277 §7 范式', 'bm-c r1114-continuation W277 §8 范式',
'注册 W277 B 带 626_701..626_900 落 naive A 窗内', 'refuser band 626_701..626_900〕', 'W279 freezer 承接面强制注记',
'engine_owner==bm-c 96 行注册', 'engine_owner 行 267 注册在册', '第 97 枚', '第 268 波', '池第 276 枚', '波号 278', '零 278 行',
'probe leg0 bmc_rows=96', 'bm-c 循环班 r1114-continuation 席位窗 2026-10-19 10:3x', 'r1114-continuation 席位窗实跑：origin inbox 零 W278 席位外机命中',
'results/p2cal_ext/n1_w277/ 12/12', 'seed_admit_gate rc0 双带 FREE',
'A_staircase_hop_past_W277_B=true', 'B_lands_above_own_A=true', 'W278=bm-c own-wave window per chain-order law',
'（占位·finalize one-pass 后回填', '（占位·finalize 同窗回填', '10:3x', '09:5x',
'W263 冻结窗 26G bm-a 实锚', '_w278bmc_freeze_edits.py', '_w277bmc_freeze_edits.py 模板派生',
'saturation_engine.py status live-read r1116', '（W277 注册+烧录+finalize 全落地）', '（上游 W277 席位已闭链', 'hops=1', 'hops=0']
miss = [f for f in faces if f not in t]
print("SPOT-CHECK %d/%d PASS" % (len(faces) - len(miss), len(faces)))
if miss:
    print("MISSING:", miss)
    sys.exit(1)
# negative panel: stale faces that must be consumed (1,031,535 EXEMPT: the single honest
# n_eff_held_equal anchor, pinned-gated count==1)
bad = ['624_501..626_500', '626_701..626_900 1 hop 落位', '注册 W276 B 带', 'refuser band 628_901..629_100',
       'W277p_', '07:2x', '07:4x', '08:1x', 'K=605,120', '第二十六次连续 A-hop', '连续二十六波',
       'bmc_rows=95', '行 266 注册在册', 'r1111 W276', 'e781164e41', 'fc01636095', 'MSG-20261019-080x']
present = [b for b in bad if b in t]
print("NEGATIVE-CHECK:", "CLEAN" if not present else ("LEAK: %r" % present))
assert t.count("1,031,535") == 1, "n_eff anchor count drift"
assert t.count("1,033,735") == 2, "ledger anchor count drift"
sys.exit(1 if present else 0)
