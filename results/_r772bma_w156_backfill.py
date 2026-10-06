# r772 bm-a: W156 prereg sec7/sec8 same-window finalize backfill (r763..r769 precedent)
# file is pure CRLF -- anchors and replacements built with \r\n to keep byte-form identical (r402 family)
import io

p = r'research/PERPETUAL_N1_W156_PREREG.md'
t = io.open(p, encoding='utf-8', newline='').read()
assert '\r\n' in t and t.count('\r\n') == t.count('\n'), 'unexpected mixed EOL'

hdr_old = '## §7 跑后实证。【finalize 收口机械回填·占位——跑前为空】\r\n- （占位：12/12 分片落地后 finalize one-pass 机械回填·回填限本节与 §8·judged 断言照 W155 例。）\r\n'
hdr_new_l = [
'## §7 跑后实证。【finalize 收口机械回填·bm-a r772·one-pass rc0·12/12 分片消费；§7/§8 回填窗注记：r772 finalize one-pass 同窗即回填（r763..r769 窗先例延续·死会话 r771 冻结窗后本恢复轮收口·r768 W154 同型接续）——回填内容=n1_w156_results.json 冻结实测键·零改判据】',
'- **合并池**：pre-W156 K=338,920（mu=−0.092851·sigma=0.244997）→ W156-only K=2,200（mu=−0.087805·sigma=0.247316）→ **merged K=341,120（mu=−0.092818·sigma=0.245012）**；账本 737,011+2,200=**739,211**（voids_applied=LOWAMP-P1/P2·file=results/perpetual_faces/n1_w156_results.json·evidence_cutoff=2026-09-22）——r771 冻结窗 leg4 投影 341,120/739,211 恒等兑现。',
'- **skill_line_v2 K-lift**（n_eff 恒等 737,011）：1.1807 → **1.1808**（Δ=**+0.0001**）；se_mu 收窄链 W154 0.000422 → W155 0.000421 → **0.000420**（0.2450/√341,120）。',
'- **A 档 full_sharpe_p95=0.3172**（2,000 runs·W155 锚=0.3123【n1_w155_results.json 机读】·差 +0.0049；§5.3 起草锚引 0.3122=W155 §7 转写位差面如实披露·两读法同过 <0.05 门·零判据影响）。',
'- **§5 四预测键全过（机证）**：①|W156-only mu − merged mu|=0.00501<0.02 ✓ ②sigma 相对变化 +0.94%<±10% ✓ ③A p95 差 +0.0049<0.05 ✓ ④K-lift +0.0001≤±0.02 ✓。',
'- **canon flip：NOT performed**（K2,200 同例法·治理提锚面 only·结果件如实注记）。',
'- 审计：12 shards 零重叠连续覆盖 A[0,2000)/B[0,200)·n_backtests 合计 2,200·machine=bm-a·audit.finalize_only=true·批内波间漂移键 mu_delta_w156_vs_w155ext=+0.004919。',
]
hdr_new = '\r\n'.join(hdr_new_l) + '\r\n'
assert t.count(hdr_old) == 1, 'SS7 anchor not found/unique: %d' % t.count(hdr_old)
t = t.replace(hdr_old, hdr_new)

s8_old = '- （占位：设计复用面+宝藏捕获问+W157+ 投影承接三行照 W155 例回填。）\r\n'
s8_new_l = [
'- 设计=v1 冻结逐字复用·纯种子带深化——零新机制零新方法；**宝藏捕获问（O-20261003-2030 §1 判决 finalize 收口步）：本批无新宝藏**（A-hops-prior-B 阶梯第十五例+own-A 保留 leg2 面已于冻结窗 r771 确认·E36 卡既有·finalize 无新增面）；方法论资产卡无 append 面。',
'- W157+ 投影承接（r771 冻结窗 leg3 已披露 + §5 键 5 同律）：A naive 360_004..362_003（post-W156 宇宙将被本波 B 带 360_004..360_203 于自家起点拒——阶梯 A-hops-prior-B 继承第十六例·r771「W156-B-refuses-W157-A staircase anticipated」预注兑现）→ W157 A 重 derive 同强制（越过 W156 B 带）；B naive 360_204..360_403（CLEAN hops=0）落重 derive 后 A 窗内=**同窗互斥 leg2 律**——**W157 冻结方必在 post-W156 注册宇宙重 derive 且 derive B 时预留本波 A 窗**（E36 卡·W141 先例链）；§5.5 起草投影数字=变前旧刻度面（r771 §3 seed-scale T-90 修复同源残留·法=冻结方 gate 机证重 derive 非转抄 r587 律·本节以 leg3 机证投影为准）；verify at W157 prereg，hop 链逐跳在 probe 回执。',
]
s8_new = '\r\n'.join(s8_new_l) + '\r\n'
assert t.count(s8_old) == 1, 'SS8 anchor not found/unique: %d' % t.count(s8_old)
t = t.replace(s8_old, s8_new)

io.open(p, 'w', encoding='utf-8', newline='').write(t)
b = open(p, 'rb').read()
print('backfill written, bytes =', len(b), 'CRLF =', b.count(b'\r\n'), 'LF-only =', b.count(b'\n') - b.count(b'\r\n'))
