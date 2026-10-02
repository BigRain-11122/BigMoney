import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PATH = 'research/PERPETUAL_N1_W82_PREREG.md'
raw = open(PATH, 'rb').read()
txt = raw.decode('utf-8')
nl = '\r\n' if '\r\n' in txt else '\n'

ph7 = '## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl + '- （占位·finalize 后机械回填）'
ph8 = '## §8 批后复盘【必填·s7-T】' + nl + nl + '- （占位·finalize 后机械回填）'
assert ph7 in txt, 'S7 placeholder not found'
assert ph8 in txt, 'S8 placeholder not found'

s7 = ('## §7 跑后实证【跑前必须为空——占位纪律：写数字即造假】' + nl + nl
      + '- **finalize 实烧=one-pass r575 bm-b**（r538 一过例·2026-10-02 12:42·12 分片 shards_consumed 12/12·audit.machine=bm-b 12/12 验属·r310 完备性门 origin 12/12 ls-tree 过〔b71794b8b 推送后复核〕）：N=2,200（A 2,000＋B 200）。' + nl
      + '- **S5 四门全过（§5 预测 4/4·锚=W79 实测）**：① W82-only mu **−0.093220** 与 merged mu **−0.092385**（K=178,320）漂移 |Δ|=**0.000835**<0.02（对锚 W79 merged −0.092397 漂 0.000012）✓；② sigma 相对变化 **+0.14%**<±10%（W82-only **0.247270** vs 锚 0.246921=W79-only 实测）✓；③ A 族 full_sharpe_p95 **0.3269** vs 锚 0.3000 |Δ|=**0.0269**<0.05 ✓；④ K-lift **+0.0002**≤0.02 @n_eff_held 542,748〔1.1658→**1.1660**·W77 −0.0001→W78 +0.0000→W79 +0.0000→W80 +0.0001→W81 +0.0001→W82 +0.0002 如实报正负〕✓。' + nl
      + '- **账本落账**：prev=**542,748**（W81 bm-a r574 活链头 derive·origin 时序面 r518 律）＋2,200=**544,948 净链头**·K=**178,320**·ledger dict 唯一 schema·voids_applied=[LOWAMP-P1, LOWAMP-P2]·evidence_cutoff=2026-09-22。' + nl
      + '- mu_delta_w82_vs_w81ext=**+0.0008**（单波跨度如实·W81-only mu −0.094103 实测）；se_mu=**0.000580** @K=178,320（收窄链延续：W79 0.000591→W80 0.000587→W81 0.000583→W82 0.000580）。' + nl)

s8 = ('## §8 批后复盘【必填·s7-T】' + nl + nl
      + '- **全生命周期三窗闭环**：冻结 r574 bm-b（席位 MSG-20261002-1245-bmb·published=reserved r518-①·先推 origin=r565 早可见性律；同窗双让路 W80→bm-c/W81→bm-a 按 r511 commit 时序律零成本撤席）→烧录 12/12（tick 引擎冻结 commit 12:18:50 后自燃起烧·r535 律·12 分片 12:29 前全落盘·r574 会话死于 S7 前夜〔state 停 573·r529 猝死诊断律〕·r575 恢复轮按 r471 收养律核验收编）→finalize r575 one-pass（W81 bm-a r574 落账 542,748 解锁后一过·FAIL-CLOSED r307）。' + nl
      + '- **链序面**：W80 bm-c r364 落账（540,548）→W81 bm-a r574 落账（542,748）→本波 W82 落账（544,948）→**W83（bm-c r365 冻·烧录已交付）finalize 链序解锁**。' + nl
      + '- **带位面**：A-ext seed **207_004..209_003**＋B-ext exit seed **54_201..54_400**（gate ADMIT 回执=results/_r574bmb_w82_band_gate.py·双侧算术顺延零跳位·单读法零分叉〔F-20261002-03 不触发〕）。' + nl
      + '- **共享文件愈合注记（r519 族第 9 犯·bm-c r365 同窗治愈）**：bm-a r574 commit e3215a98e（add -A 整树面 phantom-D）把本波冻结包共享文件内容块（n1 WAVE_CONFIGS[82]+selftest materializer leg+summary 段+canon W82 行+pf N1_BANDS[82]）整面回退蒸发——bm-a hotfix 5ff066442 只恢复 17 独立件漏共享文件内插入段；bm-c r365 按 r540 律从持有 commit 45e05a67c 字节恢复（attribution=bm-b·restorer=bm-c r365）·**零科学损失：本 finalize 从未在坏树上跑过**（愈合后机验=numstat 本地相对 origin 零独有行·W82 行逐字在册）。' + nl
      + '- 无 void·无重跑（r538 一过例）·无判据触碰（回填限 §7/§8）·selftest 回填后两态全绿（r307·缺省波调用 r522 律）。' + nl)

txt = txt.replace(ph7, s7.rstrip('\r\n'))
txt = txt.replace(ph8, s8.rstrip('\r\n'))
open(PATH, 'wb').write(txt.encode('utf-8'))
print('BACKFILL WRITTEN, nl=', repr(nl))
chk = open(PATH, 'rb').read().decode('utf-8')
assert '（占位·finalize 后机械回填）' not in chk, 'placeholder still present'
print('PLACEHOLDERS CLEARED')
