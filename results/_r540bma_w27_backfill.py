# -*- coding: utf-8 -*-
# r540 bm-a: W27 prereg section-7/8 mechanical backfill (finalize same-window law; r538 W24 template style)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'research\PERPETUAL_N1_W27_PREREG.md'
t = open(P, encoding='utf-8').read()

i7 = t.find('## §7 跑后实证')
assert i7 > 0, 'section-7 heading not found -- ABORT (two-state law r307)'
OLD_TAIL = t[i7:]
assert '（占位' in OLD_TAIL, 'section-7/8 placeholder marker missing -- ABORT (already backfilled? two-state law r307)'
assert OLD_TAIL.find('§8 批后复盘') > 0, 'section-8 heading missing -- ABORT'

NEW = """## §7 跑后实证【finalize 窗·r540 bm-a】

- 烧录实况：12/12 分片引擎烧录（bm-a tick 架构零重启自燃〔r535 实证〕·r539 冻结窗 21:27 shard-0 首片起→21:42 shard-11 收尾·每片 workers=8〔ProcessPoolExecutor·O-20260930-2355 多核律〕·audit.machine=bm-a 12/12·每片 elapsed 13.2–14.8s·本波 N=2,200 逐位吻合·shard 件 results/p2cal_ext/n1_w27/shard-0..11-of-12.json r539 同轮 12/12 全上 origin；finalize 排队至 bm-c W26 finalize 落账〔r336 21:51 chain gate released〕后本窗一趟过）。
- K 与链性对账：K=**57,320**（pre-W27 累计 **55,120**〔canon 120＋W1..W26 波值 55,000〕＋本波 2,200=§0 预期逐位吻合〔§0 起草窗注记 W26 finalize 未落账·「cumulative K=55,120」指本波前池·W26 落账后自动并入·derive 禁手抄律自证〕）；merged mu **−0.09168**·sigma **0.24476**·se_mu **0.001022**（W26 0.001042→收紧）；W27-only mu **−0.08574**（波单波抽样波动如实·mu_delta vs W26ext −0.0052）。
- §5 四项判定：**4/4 PASS**（①mu-drift **+0.00072**<0.02〔merged vs 冻结锚 W25 −0.09240·起草窗最新可得锚律〕②sigma 相对 **+0.11%**<±10%〔锚 W25 0.24449〕③A p95 **0.3208** vs 0.3262 Δ**−0.0054**<0.05 ④K-lift **+0.0005**≤0.02〔1.1536→1.1541·@n_eff_held 421,748·正向如实报·canon_flip NOT performed——治理提案面·K2200 同法〕）。
- 账本对账：prev=**421,748**（W26 finalize r336 bm-c 活头 derive·禁手抄）→ **423,948** 链线性；voids_applied=['LOWAMP-P1'] 自动面；audit.finalize_only=bm-a；ledger 块在产物件 science_gates.ledger（r509 持久化律：guard 前入件·无幻影面）。

## §8 批后复盘【s7-T·finalize 同窗回填】

- 波收口复盘：W27=bm-a 第 5 枚自有波（第十六枚引擎波）全链闭环：r539 冻结（A 97_004..99_003/B 40_251..40_450 双算术净空 ADMIT 回执在场）→tick 自燃 12/12（r539 同轮交付）→r540 finalize 一趟过（排队 bm-c W26 落账 21:51 门开·同窗收口·无重跑=r538 双计律守约）。**W26-restore 事故如实披露**：finalize 前置读链发现 bm-b r523 closeout（17aa3c4af·自称 disjoint overlay）外科整树面静默删 r336 产品 7 件（n1_w26_results.json+6 工具）＋W26 prereg §7 回填还原为占位（r519 族第 5 犯变体）——b526746ed 自持有 commit 96d1b5544 字节恢复＋audit.machine=bm-c 归属验＋json.loads/ledger 421,748 自证＋MSG 已发；finalize 三前置验（ls-tree 12/12·json·prev derive）全过后才跑。
- W28+ 尾律警示转交：W28=bm-b 座位 r523 已冻结（A 99_004..101_003/B 40_451..40_650 双算术净空 ADMIT——与本机 r539 带闸投影双源同值）；烧录在途（r523 冻结时 2/12·tick 续烧中）。**W29=bm-c 座位**（模 3 续行 26+3=29·W28 行 verbatim 接力）——A 侧续行 101_004.. 起算·冻结窗机闸穷尽扫描必含探针种子簇腿＋N3-R1 腿＋全公示投影带（r335/r539 同法）；W28 finalize（bm-b 座）排本波后=prev **423,948** derive 禁手抄。
"""

t2 = t[:i7] + NEW
open(P, 'w', encoding='utf-8', newline='').write(t2)

# self-verify: key numbers present, no placeholder residue, headings intact
t3 = open(P, encoding='utf-8').read()
i = t3.find('§7 跑后实证')
seg = t3[i:i+2600]
checks = [
    ('423,948 chain head', '423,948' in seg),
    ('K=57,320', '57,320' in seg),
    ('4/4 PASS', '4/4 PASS' in seg),
    ('12/12 burn fact', '12/12' in seg),
    ('no placeholder residue', '（占位' not in seg),
    ('W29=bm-c handover', 'W29=bm-c' in seg),
    ('restore incident disclosed', 'W26-restore' in seg),
    ('A p95 0.3208', '0.3208' in seg),
]
ok = True
for name, cond in checks:
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and cond
print('BACKFILL RESULT:', 'ALL PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
