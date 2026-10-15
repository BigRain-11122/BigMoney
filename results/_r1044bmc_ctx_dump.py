import io
t = io.open(r'results\_w250bmc_w249_frozen_face.txt', encoding='utf-8', newline='').read()
out = []
for needle in ['R250：W249', '第 247 枚', '键 W248 实测 K-lift', 'n_eff_held_equal 967,735',
               '→W248 **0.000332**】', 'selftest W249 face', 'bm-c 循环班 r1037 freeze 窗',
               '本窗 free RAM', '实差 0.0015', '（**0.3154**', 'W249+ 投影', 'probe W250+ 投影',
               '−0.09279163', '0.2450393', '−0.09134', 'line_pre_w248', 'line_merged@K543,520',
               '（bm-c r1037 席·queue-head', 'bm-c r1036 窗 22:1x', 'r1035/W248 先例',
               'A base==前波 A 尾+1（563_500+1）', 'B base==前波 B 尾+1（544_900+1）',
               'W243/W246/W248 低 RAM', '席位窗宇宙（post-W248-REGISTERED 终态注册·freeze-UNBLOCKED）',
               'W250 freezer 承接面', '已如实披露非分叉）', 'perpetual_faces.py 零 247 行',
               'engine_owner==bm-c 68 行注册', '全二百四十六行注册']:
    i = t.find(needle)
    out.append('==== %s @ %d' % (needle, i))
    if i >= 0:
        out.append(t[max(0, i - 200): i + 400].replace('\n', ' ¶ '))
    out.append('')
io.open(r'results\_r1044bmc_ctx2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out))
