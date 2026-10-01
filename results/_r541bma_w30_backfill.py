# -*- coding: utf-8 -*-
# r541 bm-a: W30 prereg section-7/8 mechanical backfill (finalize same-window law; r540 W27 template style)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'research\PERPETUAL_N1_W30_PREREG.md'
t = open(P, encoding='utf-8').read()

i7 = t.find('## §7 跑后实证')
assert i7 > 0, 'section-7 heading not found -- ABORT (two-state law r307)'
OLD_TAIL = t[i7:]
assert '（占位' in OLD_TAIL, 'section-7/8 placeholder marker missing -- ABORT (already backfilled? two-state law r307)'
assert OLD_TAIL.find('§8 批后复盘') > 0, 'section-8 heading missing -- ABORT'

NEW = """## §7 跑后实证【finalize 窗·r541 bm-a】

- 烧录实况：12/12 分片引擎烧录（bm-a tick 架构零重启自燃〔r535 实证·本窗再证：冻结 commit 614575701 落 origin ~22:14 后 22:15 shard-0 首片自燃〕·22:15→22:29 十二片逐分钟收尾·每片 workers=8〔ProcessPoolExecutor·O-20260930-2355 多核律〕·audit.machine=bm-a 12/12·每片 elapsed 13.7–14.3s·全波 n_backtests **2,200 逐位吻合**·shard 件 results/p2cal_ext/n1_w30/shard-0..11-of-12.json；evidence_cutoff=2026-09-22 12/12 同窗律·本窗 finalize 一趟过零排队〔W28 finalize 已先行落账 r524 bm-b=链头 426,148 门开〕）。
- K 与链性对账：K=**61,720**（pre-W30 累计 **59,520**〔W28 实测 merged n 实锚逐位〕＋本波 2,200=§0 勘误后散文 61,720 机器 derive 逐位吻合〔§0 初稿算术误书 63,920 已同窗勘误披露·finalize 消费面=机器 derive 零散文依赖·本对账即自证〕）；merged mu **−0.09150**·sigma **0.24478**·se_mu **0.000985**（W28 0.0010→收紧）；W30-only mu **−0.09037**（波单波抽样波动如实·mu_delta vs W28ext −0.0025）。
- §5 四项判定：**4/4 PASS**（①mu-drift **+0.00117**<0.02〔W30-only vs 冻结锚 W28 merged −0.09154·锚滚动律同窗执行〕②sigma 相对 **−0.04%**<±10%〔锚 W28 0.24487·merged 0.24478〕③A p95 **0.308** vs 0.3278 Δ**−0.0198**<0.05〔波单波抽样面·非断裂〕④K-lift **−0.0005**≤0.02〔1.1553→1.1548·@n_eff_held 426,148·**负向如实报**〔W22 −0.0002 同族先例：加深收窄 se_mu 不必然抬线〕·canon_flip NOT performed——治理提案面·K2200 同法〕）。
- 账本对账：prev=**426,148**（W28 finalize r524 bm-b 活头 derive·禁手抄）→ **428,348** 链线性；voids_applied=['LOWAMP-P1'] 自动面；audit.finalize_only=bm-a；ledger 块在产物件（finalize 输出含 science_gates.ledger 面）。

## §8 批后复盘【s7-T·finalize 同窗回填】

- 波收口复盘：W30=bm-a 第 6 枚自有波（第十九枚引擎波）全链同轮闭环：r541 冻结（A 103_004..105_003/B 41_001..41_200 **双跳位 ADMIT**——A=W29 公示投影保留面 r518 执行·B=p4_batch1=41_000 带内点跳位 W26-B 族谱系·回执 _r541bma_w30_band_gate.py leg0/leg0b/leg1/leg1b/leg2/leg3 六腿）→tick 自燃 12/12（冻结同窗 22:15–22:29）→finalize 一趟过（22:3x·W28 门开零排队）→本节回填同窗——**冻结→烧毕→finalize→回填全链单轮完成=最快收口先例**（对照 W27=r539 冻结+烧毕/r540 finalize 两轮）。冻结窗内 origin 前移 4 commit（W28 finalize 落账 r524 bm-b）→锚滚动律同窗执行（§5 锚 W27→W28）+pull --rebase 脏树硬拒（r277 禁 stash 面）→r512 外科提交净路零 rebase 零吞件+reset --mixed 重锚+origin 新件 34 面 checkout 和解（本机活 lane 7 件保留）——全链零科学损失。
- W29 指引（bm-c 座·未注册如实注记）：W28 行 W29+ 警示公示窗（A 101_004..103_003/B 40_651..40_850）经本波 r518 保留面腿**未被占用=仍为 W29 预留**；bm-c 注册时带闸按注册表 derive（必含 W30 行+探针种子簇腿+N3-R1 腿+全公示投影带）；finalize 链序走活头 derive（现头 428,348）与波号序无锁。
- W31+ 尾律警示转交：**W31=bm-b 座位**（模 3 续行 28+3=31·W30 行 verbatim 接力）——A 侧续行 105_004..107_003·B 侧续行 41_201..41_400 投影双净空（r541 带闸回执 W31+ 投影腿）；冻结窗机闸穷尽扫描必含探针种子簇腿＋N3-R1 腿＋全公示投影带（本表 W28 行 W29+ 警示＋W30 行 W31+ 警示双面）＋SEED_REGISTRY 全值（41_000/43_000 带内点族教训=B 侧跳位机闸首净窗 derive）。
"""

t = t[:i7] + NEW
open(P, 'w', encoding='utf-8', newline='\n').write(t)

# self-check: 8/8 (headings, no placeholder left, key values present, correction note intact)
tt = open(P, encoding='utf-8').read()
checks = [
    ('sec7 heading', '## §7 跑后实证【finalize 窗·r541 bm-a】' in tt),
    ('sec8 heading', '## §8 批后复盘【s7-T·finalize 同窗回填】' in tt),
    ('no placeholder left', '（占位' not in tt.split('## §7')[1]),
    ('K 61720', '61,720' in tt),
    ('ledger 428,348', '428,348' in tt),
    ('S5 4/4', '4/4 PASS' in tt),
    ('negative K-lift honest', '−0.0005' in tt and '负向如实报' in tt),
    ('correction note intact', '勘误披露' in tt and '63,920' in tt),
]
bad = [n for n, ok in checks if not ok]
print('backfill self-check:', '8/8 PASS' if not bad else f'FAIL {bad}')
sys.exit(1 if bad else 0)
