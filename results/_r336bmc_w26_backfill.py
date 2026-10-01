# -*- coding: utf-8 -*-
# r336 bm-c: W26 prereg section-7/8 mechanical backfill (finalize same-window; r538 W24 template style)
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

P = r'research\PERPETUAL_N1_W26_PREREG.md'
t = open(P, encoding='utf-8').read()

OLD = """## §7 跑后实证【finalize 窗回填】

-（占位锚：finalize 落地后本节回填烧录实况/K 与 §5 四项判定/链性对账/账本对账——r307 两态守卫律：烧后回填为合法消费锚文，selftest 腿两态判据兼容。）

## §8 批后复盘【s7-T·finalize 同窗回填】

-（占位锚：finalize 同窗回填波收口复盘与 W27+ 尾律警示转交〔W27=bm-a 槽位·轮值律〕。）"""

NEW = """## §7 跑后实证【finalize 窗·r336 bm-c】

- 烧录实况：12/12 分片引擎烧录（r335 同轮窗·bm-c 常驻实例·每片 workers=8〔O-20260930-2355 多核律〕·audit.machine=bm-c 12/12）；交付链=7 片（2/5/7/8/9/10/11）r335 外科推送落 origin＋5 片（0/1/3/4/6）引擎 ledger append 步 commit（首推被拒滞留本地·r336 重锚后 append 步重新 commit 6a30acf8d 推送成功）→origin 12/12（r310 ls-tree 完备性门过）→finalize r336 一趟过（pre-W26 mu −0.0924 K=52,920 与 W25 finalize 实测逐位吻合=链性双证）。
- K 与链性对账：K=**55,120**（canon 120＋W1..W25 累计 52,920〔W24/W25 finalize 落账自动并入=§0 条款生效面〕＋本波 2,200）；**§0 累计数 50,720=起草窗滑算如实披露**——起草窗 W24/W25 finalize 未落账、§0 求和把两波排除（与 §0 自身「W24/W25 落账自动并入·derive 禁手抄」条款自相矛盾）；链序 derive 真值=55,120，与 W27 prereg（r539 bm-a）锚「cumulative K=55,120」双源同谳。merged mu **−0.09192**·sigma **0.24472**·se_mu **0.001042**（W25 0.001063→收紧）；W26-only mu −0.0805（波单波抽样波动如实）。
- §5 四项判定：**4/4 PASS**（①mu-drift **+0.00117**<0.02〔锚 W23 −0.09309〕②sigma 相对 **+0.09%**<±10%〔锚 0.24449〕③A p95 **0.3273** vs 0.3054 Δ**+0.0219**<0.05 ④K-lift **+0.0011**≤0.02〔1.1523→1.1534·@n_eff 419,548·正向如实报〕）。
- 账本对账：prev=**419,548**（W25 finalize r522 bm-b 活头 derive·禁手抄）→ **421,748** 链线性；voids_applied=['LOWAMP-P1'] 自动面；audit.finalize_only=bm-c；ledger 块在产物件 science_gates.ledger（r509 持久化律：guard 前入 family summary 面）。

## §8 批后复盘【s7-T·finalize 同窗回填】

- 波收口复盘：W26=bm-c 第 5 枚自有波（第十五枚引擎波）跨轮闭环：r335 冻结（双强制跳位＋探针种子簇发现 r335 律）→r335 同轮 12/12 引擎烧录→r336 重锚整合＋孤儿 5 片引擎 append 自推送补齐 origin 12/12→finalize 一趟过。跨机链序实况=W24（bm-a r538）→W25（bm-b r522）→W26（bm-c r336）三机三窗连续收口·r519 origin-face 链序律全程生效；本机 5 片滞留面=引擎 push 拒绝后 append 步在重锚净基上自愈（r522 孤儿对账律的 bm-c 自然收敛首例·零人工重推）。
- W28+ 尾律警示转交：W27=bm-a 槽位已由 r539 冻结（A 97_004..99_003/B 40_251..40_450 双算术净空 ADMIT 回执在场·tick 自燃在途〔冻结窗实况 5/12〕）；**W28=bm-b 轮值槽**（轮值律续行·28=25+3 mod 同表）算术位投影=A 99_004..101_003/B 40_451..40_650——**99k+ 段 reserved universe 未勘探**=冻结窗机闸穷尽扫描 derive（r335 探针簇腿强制携带律·禁按本投影 prose 直接落带）；W27 finalize（bm-a 座）排本波后·prev=421,748 derive 禁手抄。"""

assert OLD in t, 'W26 section-7/8 placeholder block not found verbatim -- ABORT (two-state law r307)'
t2 = t.replace(OLD, NEW, 1)
open(P, 'w', encoding='utf-8', newline='').write(t2)

# self-verify: backfilled segment carries the real numbers; no placeholder residue
t3 = open(P, encoding='utf-8').read()
i = t3.find('§7 跑后实证')
seg = t3[i:i+2600]
checks = [
    ('chain head 421,748', '421,748' in seg),
    ('K=55,120', '55,120' in seg),
    ('drafting slip disclosed', '50,720=起草窗滑算' in seg),
    ('4/4 PASS', '4/4 PASS' in seg),
    ('12/12 burn fact', '12/12' in seg),
    ('A p95 0.3273', '0.3273' in seg),
    ('se_mu 0.001042', '0.001042' in seg),
    ('no placeholder residue', '占位锚' not in seg),
    ('W28 seat handed over', 'W28=bm-b' in seg),
    ('W27 prev derive warning', '421,748 derive' in seg),
]
ok = True
for name, cond in checks:
    print(('PASS ' if cond else 'FAIL ') + name)
    ok = ok and cond
print('BACKFILL RESULT:', 'ALL PASS' if ok else 'FAIL')
sys.exit(0 if ok else 1)
