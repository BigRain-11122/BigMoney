# -*- coding: utf-8 -*-
# r538 bm-a: W24 prereg §7/§8 mechanical backfill (finalize same-window law; W22/W23 template style)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'research\PERPETUAL_N1_W24_PREREG.md'
t = open(P, encoding='utf-8').read()

OLD = """## §7 跑后实证【finalize 窗回填】（占位·finalize 同窗回填）

- 烧录实况：（占位）
- K 与链性对账：（占位）
- §5 四项判定：（占位）
- 账本对账：（占位）

## §8 批后复盘【s7-T·finalize 同窗回填】（占位）

- 波收口复盘：（占位）
- W25+ 尾律警示转交：（占位）"""

NEW = """## §7 跑后实证【finalize 窗·r538 bm-a】

- 烧录实况：12/12 分片引擎烧录（bm-a tick 架构零重启自燃〔r535 实证〕·r535 冻结窗 20:14 shard-0 首片起·每片 workers=8〔ProcessPoolExecutor·O-20260930-2355〕·audit.machine=bm-a 12/12·每片 elapsed 13.2–14.8s·n_backtests 合计 2,200 逐位吻合·shard 件 results/p2cal_ext/n1_w24/shard-0..11-of-12.json；r536 轮 20:36 12/12 全上 origin，finalize 因链序等 bm-c W23，r335 21:01 落账解锁后本窗一趟过）。
- K 与链性对账：K=**50,720**（canon 120＋W1 2,200＋W2..W14 13×2,200＋W16..W23 8×2,200＋本波 2,200=§0 预期逐位吻合）；merged mu **−0.09268**·sigma **0.24460**·se_mu **0.001086**（W23 0.001110→收紧）；W24-only mu −0.08349（波单波抽样波动如实）。
- §5 四项判定：**4/4 PASS**（①mu-drift |+0.00042|<0.02〔锚 W23 −0.09309〕②sigma 相对 +0.045%<±10%〔锚 0.24449〕③A p95 0.3329 vs 0.3054 Δ+0.0275<0.05 ④K-lift **+0.0010**≤0.02〔1.1505→1.1515·@n_eff 415,148·正向如实报〕）。
- 账本对账：prev=**415,148**（W23 finalize r335 bm-c 活头 derive·禁手抄）→ **417,348** 链线性；voids_applied=['LOWAMP-P1'] 自动面；finalize stdout ledger 块留痕 results/_r538bma_w24_finalize_full.log（重跑修正版=首跑复原件·audit.finalize_only=bm-a）。

## §8 批后复盘【s7-T·finalize 同窗回填】

- 波收口复盘：W24=bm-a 第 4 枚自有波（第十三枚引擎波）全链闭环同窗完成：r535 冻结→tick 自燃烧录（零常驻实例·bm-a 架构实证）→r536 12/12 交付→r538 finalize 一趟过。finalize 重跑坑实弹：重跑把自产 W24 件计入 prev（ledger prev derive 扫 results 文件集·非幂等）→415,148 误变 417,348 双计；修正=删未 commit 自产件重跑复原正头（科学 payload 字节恒等=确定性律自证）——首 finalize 后禁盲重跑（坑律另录 S4）。
- W25+ 尾律警示转交：W26=bm-c seat **B 带算术位 39_900..40_099 撞 N2/N4 探针点 40_000/40_001/40_050 必须跳位**（r520 bm-b W25 冻结窗警示行·r307 N1-W5 撞值跳位先例同法）；W27=bm-a（bm-a 下一座位）候 W26 落表；W25 finalize=bm-b 座位收口在途。"""

assert OLD in t, '§7/§8 placeholder block not found verbatim -- ABORT (two-state law r307)'
t2 = t.replace(OLD, NEW, 1)
open(P, 'w', encoding='utf-8', newline='').write(t2)

# self-verify: no placeholder residue in §7/§8 area; key numbers present
t3 = open(P, encoding='utf-8').read()
i = t3.find('§7 跑后实证')
seg = t3[i:i+2200]
checks = [
    ('417,348 chain head', '417,348' in seg),
    ('K=50,720', '50,720' in seg),
    ('4/4 PASS', '4/4 PASS' in seg),
    ('12/12 burn fact', '12/12' in seg),
    ('no 占位 residue in §7/§8', '（占位）' not in seg),
    ('W26 warning handed over', '39_900..40_099' in seg),
]
ok = True
for name, cond in checks:
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and cond
print('BACKFILL RESULT:', 'ALL PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
