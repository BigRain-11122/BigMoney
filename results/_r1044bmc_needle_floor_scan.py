import io
T0 = io.open(r'results\_w250bmc_w249_frozen_face.txt', encoding='utf-8', newline='').read()
needles = [
    # band values + prior tails
    '565_500', '563_501', '563_500', '545_100', '544_901', '544_900',
    'A base=563501 span=2000 checked=2000 verdict=FREE',
    'B base=544901 span=200 checked=200 verdict=FREE',
    # ledger/K heads
    '545,720 投影', '543,520', 'K=543,520 合并池', '543,520+2,200',
    '969,935', '967,735', '969,935+2,200',
    # sec5 measured keys
    '−0.09279163', '−0.09134', '0.2450393', '实差 0.0015 在带内', '（**0.3154** 实测锚）',
    'W2..W248 共二百四十六面实测', 'W5..W248 先例', 'W136..W248 先例链披露',
    # wave rolls
    'W249', 'W248', 'n1_w249', 'n1_w248', '_w249bmc_20261015', '_w249bmc', '_w248bmc',
    '--wave 249', '波号 249', '连续第十二个 seed-gap face',
    # ordinals
    '第 247 枚', '第 239 波', 'bm-c 第六十九枚自有波', '第 69 枚',
    'bmc rows 68+候选=第 69 枚 EXACT',
    'probe leg0 bmc_rows=68 attempt-continuity face（r1037 窗算法·bm-c own seat+bmc live rows 68 实读）',
    'engine_owner==bm-c 68 行注册', 'engine_owner 行 238 注册在册',
    '全二百四十六行注册', 'freeze 窗 live derive 246 行单态 owner rows 238',
    '共二百四十六面实测', 'perpetual_faces.py 零 247 行',
    'probe leg0 机证 246 行', '席位窗 probe leg0 实测 246 行',
    'R250：W249 带从未指派',
    # seat/provenance
    'MSG-20261015-225x-bmc-w249-seat', '8949e0aef',
    '（bm-c r1037 席·queue-head FREEZE-UNBLOCKED 发布）', '（bm-c r1037 席位', '（r1037 席位窗实跑',
    'waits-upstream ARMED',
    # finalize/freeze window faces
    'bm-c r1036 窗 22:1x', '·22:1x finalize one-pass】', 'r1035/W248 先例 freeze-prep 同式',
    'bm-c 循环班 r1037 freeze 窗 2026-10-16 02:1x',
    'saturation_engine.py status live-read r1037',
    # RAM faces
    '本窗 free RAM ~1.9GB',
    '本窗 free RAM ~1.9GB（bm-c 底盘常驻·24G 物理内存机·MV V4 装配+星晴 T1 海审=bm-a 席在飞〔P0 交接 poke 22:54 已收·bm-c GPU 空窗〕+CPU 车道独立如实注记）',
    '·W248 冻结窗 RAM 未记录（r1036 死窗 estate 收口·省锚如实注记）',
    '·W247 冻结窗 60.8G bm-a 实锚',
    'W243/W246/W248 低 RAM 实烧先例',
    # K-lift / se_mu chain
    '键 W248 实测 K-lift **−0.0001**', 'line_merged@K543,520 **1.1937**',
    'line_pre_w248 1.1938', 'n_eff_held_equal 967,735',
    '→W247 **0.000333**→W248 **0.000332**】',
    'bm-c r1036 W248 §7 范式', 'bm-c r1036 W248 §8 范式',
    # universe / blocks
    '席位窗宇宙（post-W248-REGISTERED 终态注册·freeze-UNBLOCKED）',
    '席位窗宇宙（post-W248-REGISTERED 终态注册）',
    '本候选=bm-a 自有席自有波',
    # downstream-stale (untouched by VMAP)
    'W250+ 投影', 'W250 freezer 承接面）】。', 'verify at W250 prereg',
    '·probe W250+ 投影 A 565_501..567_500 / B 545_101..545_300 **双面 CLEAN hops=0 预披露',
    '5. **W250+ 投影（probe 机证 leg4',
    '（**B 面=CLEAN·hops=0 算术续带承袭形态**', '已如实披露非分叉）',
    '（法典 §4 W249 行 B=544_901..545_100', '兑现收敛·ADMIT 回执在场）',
    'selftest W249 face', '零假设零风险。',
    '+W246=bm-a r1016 prereg derive',
    'W239 冻结窗 1.0G bm-c 实锚）',
    # proj gates
    'W249+ 投影',
    '已落账键·22:1x',
    'W249 splice 先于席位窗已落地', 'W248 splice 先于席位窗已落地',
    '（W206/W211/W212/W213/W214/W215/W216/W217/W218/W219/W220/W221/W222/W223/W224/W225/W226/W227/W228/W229/W230/W231/W232/W233/W234/W235/W236/W237/W238/W239/W240/W241/W242/W243/W246/W248 低 RAM 实烧先例',
    'W248 块的自有 W237..W247 legs（11 行）',
    '提取后新增 W237..W248 leg（12 行）构成 W249 块 parity 107 行',
    '（W138..W206+W211+W212+W213+W214+W215+W216+W217+W218+W219+W220+W221+W222+W223+W224+W225+W226+W227+W228+W229+W230+W231+W232+W233+W234+W235+W236+W237+W238+W239+W240+W241+W242+W243+W244+W245+W246+W247+W248）',
    'gate0.5 自查', 'pre-W249', '表尾 W248 行', 'queue-head FREEZE-UNBLOCKED lane',
    'queue-head FREEZE-UNBLOCKED 承接',
]
lines = []
for n in needles:
    lines.append('%d\t%r' % (T0.count(n), n))
io.open(r'results\_r1044bmc_needle_floor_scan.txt', 'w', encoding='utf-8').write('\n'.join(lines))
print('done', len(needles), 'bytes', len(T0.encode('utf-8')))
