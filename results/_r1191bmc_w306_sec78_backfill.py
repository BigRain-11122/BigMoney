# -*- coding: utf-8 -*-
"""r1191 bm-c: W306 prereg sec.7/sec.8 mechanical backfill (finalize same-window leg).

Only the two placeholder lines are rewritten (judging criteria untouched per the
freeze rule). English-free face: records shifted values machine-read from
results/perpetual_faces/n1_w306_results.json + the five-key receipt.
"""
import io

P = 'research/PERPETUAL_N1_W306_PREREG.md'
t = io.open(P, encoding='utf-8').read()

S7_OLD = '- （占位·finalize one-pass 后回填：账本恒等式/合并池 K/merged mu·sigma·se_mu/K-lift 对照/§5 五预键机证件/六门探针/canon flip 态/audit 段——bm-c r1189 W306 §7 范式）'
S8_OLD = '- （占位·finalize 同窗回填：§5.5 W307+ 投影承接机证/宝藏与方法论捕获问/诚实披露面——bm-c r1189 W306 §8 范式）'

S7 = '\n'.join([
 '- **账本恒等式**：prev_total 1,095,341 + batch 2,200 = total 1,097,541（exact=true·W305 finalize 链头机读）。',
 '- **合并池**：K 668,920 + 2,200 = 671,120（exact=true）·merged mu **−0.09284764**·sigma **0.24512663**·se_mu@K671,120 **0.000299**（较 W305 的 0.000300 再收窄一档）·W306-only mu **−0.08964145**·sigma **0.24199611**。',
 '- **K-lift 对照**：line_pre_w306 **1.1999** → line_merged@K671,120 **1.1999**·Δ **+0.0000**·n_eff_held_equal 1,095,341（非质变）。',
 '- **§5 五预键机证件**：results/_r1191bmc_w306_fivekeys.json——6/6 ALL PASS（key1 Δmu 0.0032062<0.02 / key1b 1.05e-05 / key2 sigma_rel −4.22e-05 / key3 a_p95 Δ +0.0081<0.05 / key4 K-lift 0.0≤0.02 / key5 se_mu 0.000299≤0.000300）。**诚实披露**：§5 key4 prose 内 n_eff_held_equal 字面量写作 1,093,141（W304 值），W305 实测为 1,095,341——断言走机读实测，prose 偏差已入回执 prereg_prose_deviations（不静默抹平）。',
 '- **六门探针**：results/_r1191bmc_w306_sixgate.json = 第 69 次连续 ALL PASS（clean-state v2=b CR 归一 worktree==landed + 冻结面重放裁定 PASS 零 unexplained delta）。',
 '- **canon flip**：NOT performed（治理提案面，K2200 同法）。',
 '- **audit 段**：evidence_cutoff 2026-09-22·families A n=2,000 p95 0.3090 p99 0.4623·12/12 分片消费。',
])

S8 = '\n'.join([
 '- **§5.5 W307+ 投影承接**：W306 注册后 naive W307 A 690_501..692_500 起点将被本波 B 带 690_501..690_700 拒（staircase-affects-A 承袭）；B naive 690_701..690_900 干净但落投影 A 窗内（own-A reservation cascade 承袭）——**W307 冻结方必须 post-W306 宇宙 live re-derive，禁转录投影，禁假设 +1 恒等**（本窗 seat 回执实测 A base==W305 B tail+1、B base==own-A tail+1 双 1-hop 形态，第五十四波如实注记）。',
 '- **宝藏/方法论捕获问**：本批无新科学面（纯 null 加深波）；方法论层面捕获两条施工判例——①冻结面裁定器（Tools/n1_freeze_face_adjudicate.py）的 --editor/--receipt/--prereg 路径必须传 POSIX 斜杠：反斜杠路径经 `git show <sha>:<path>` 会被当成字面文件名，报「exists on disk, but not in commit」的假阴性；②六门 splice 抓取串必须与真实 commit message 逐字一致（本波实际为「W306 five-face freeze splice」，抓「W306 five-face splice」=零命中→可解析 sha 断言立刻失败）。两条已入轮报告与记忆候选，无 TREASURE 级新物。',
 '- **诚实披露面**：prereg §5 key4 prose 的 n_eff 字面量陈旧（上列）；另 W306 单波 mu −0.08964145 高于合并池 −0.09284764 约 0.0032（带内，纯抽样波动，非设计变更）；A 档 p95 0.3090 较 W305 0.3009 上移 0.0081（带内）。',
])

assert t.count(S7_OLD) == 1, t.count(S7_OLD)
assert t.count(S8_OLD) == 1, t.count(S8_OLD)
t = t.replace(S7_OLD, S7).replace(S8_OLD, S8)
io.open(P, 'w', encoding='utf-8', newline='\n').write(t)
print('backfilled bytes', len(t.encode('utf-8')))
print('placeholders left', t.count('（占位'))