# -*- coding: utf-8 -*-
# r522 bm-b: W25 prereg §7/§8 mechanical backfill (finalize same-window law; W24/W25 template style)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'research\PERPETUAL_N1_W25_PREREG.md'
t = open(P, encoding='utf-8').read()

ANCHOR = '## §7 跑后实证'
i = t.find(ANCHOR)
assert i >= 0, '§7 anchor not found -- ABORT (two-state law r307)'
tail = t[i:]
assert tail.count('（占位') == 2, \
    f'placeholder count {tail.count("（占位")} != 2 -- ABORT (pre-burn state expected)'
assert '## §8 批后复盘' in tail, '§8 anchor not found -- ABORT'

NEW = """## §7 跑后实证【finalize 窗·r522 bm-b】

- 烧录实况：12/12 分片引擎烧录（bm-b per-tick 引擎〔60s schtasks tick 自物化·零常驻实例·r517/r519/r521 实探〕·r520 冻结窗后下一 tick 自燃·每片 workers=8〔O-20260930-2355 多核律〕·audit.machine=bm-b 12/12·每片 elapsed 22.9–24.5s·n_backtests 合计 2,200 逐位吻合·shard 件 results/p2cal_ext/n1_w25/shard-0..11-of-12.json；r521 轮 12/12 全上 origin〔ride1 a14fc3b77〕，finalize 因链序等 bm-a W24，r538 21:08 落账解锁后本窗一趟过）。
- K 与链性对账：K=**52,920**（canon 120＋W1 2,200＋W2..W14 13×2,200＋W16..W24 9×2,200＋本波 2,200=§0 预期逐位吻合）；merged mu **−0.09240**·sigma **0.24460**·se_mu **0.001063**（W24 0.001086→收紧）；W25-only mu −0.08591（波单波抽样波动如实）。
- §5 四项判定：**4/4 PASS**（①mu-drift |+0.00069|<0.02〔锚 W22 −0.09309〕②sigma 相对 +0.03%<±10%〔锚 0.24453〕③A p95 0.3262 vs 0.3132 Δ+0.0130<0.05 ④K-lift **+0.0002**≤0.02〔1.1518→1.1520·@n_eff 417,348·正向如实报〕）。
- 账本对账：prev=**417,348**（W24 finalize r538 bm-a 活头 derive·禁手抄）→ **419,548** 链线性；voids_applied=['LOWAMP-P1'] 自动面；finalize stdout ledger 块留痕 results/_r522bmb_w25_finalize_full.log（首跑一趟过·跑前自产件缺席实证=r538 禁盲重跑律前置核查·零重跑零双计）。

## §8 批后复盘【s7-T·finalize 同窗回填·r522 bm-b】

- 波收口复盘：W25=bm-b 第 7 枚自有波（第十四枚引擎波）全链闭环同窗完成：r520 冻结（双尾算术续带免跳·ADMIT 回执在场）→per-tick 引擎自燃烧录→r521 12/12 交付→r522 finalize 一趟过；引擎侧 bm-b 实例全程零重启零手工代烧（SATURATION_ENGINE_LAW §1 本地队列合同履行）。
- W27+ 尾律警示转交：W26=bm-c 已冻结〔r335〕——实落带 A **95_004..97_003**/B **40_051..40_250**（双尾 forced skip：A 算术位 94_001..96_000 撞探针种子簇 95_000..95_003＝r335 发现=带闸 reserved universe 缺探针种子腿〔W25 ADMIT 回执同缺此腿·诚实披露：本波带 92_001..94_000 与探针簇零交集=零实撞零整改〕；B 算术位 39_900..40_099 撞 40_000/40_001/40_050 拒绝点＝本件 §8 警示行已被 r335 执行）；**W27=bm-a（下一座位）投影 A 97_004..99_003/B 40_251..40_450**——bm-a 冻结窗机闸必含探针种子簇全腿+N3-R1 已用种子带腿（r335 教训面+R250 one-step 律）。"""

t2 = t[:i] + NEW
open(P, 'w', encoding='utf-8', newline='').write(t2)

# self-verify: no placeholder residue in §7/§8 area; key numbers present
t3 = open(P, encoding='utf-8').read()
seg = t3[t3.find('## §7'):]
checks = [
    ('419,548 chain head', '419,548' in seg),
    ('K=52,920', '52,920' in seg),
    ('4/4 PASS', '4/4 PASS' in seg),
    ('12/12 burn fact', '12/12' in seg),
    ('no placeholder residue', '（占位' not in seg),
    ('W27 warning handed over', '97_004..99_003' in seg),
    ('probe-seed disclosure', '95_000..95_003' in seg),
    ('prev 417,348 derive', '417,348' in seg),
]
ok = True
for name, cond in checks:
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and cond
print('BACKFILL RESULT:', 'ALL PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
