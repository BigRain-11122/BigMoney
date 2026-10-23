# -*- coding: utf-8 -*-
import io, re
t = io.open('results/_w300bmc_w299_frozen_face.txt', encoding='utf-8').read().replace('\r\n', '\n')
out = []


def snip(label, pat, n=1, w=700, back=250):
    hits = list(re.finditer(pat, t))
    out.append('### %s hits=%d' % (label, len(hits)))
    for m in hits[:n]:
        out.append('[%d] %s' % (m.start(), t[max(0, m.start() - back):m.start() + w]))


snip('proj_pool', r'=\*\*[\d,]+ 投影\*\*')
snip('RAM_chain', r'·W264 冻结窗')
snip('timeline', r'（r11\d\d/r11\d\d/r11\d\d W\d+ 全周期先例实时间线')
snip('free_ram', r'本窗 free RAM [\d.]+GB')
snip('msg_seat', r'MSG-20261024-\d+-bmc-w\d+-seat', 4, 350)
snip('splice_prov', r'bm-c r11\d\d 五面冻结 splice', 3, 350)
snip('round_label', r'循环班 r11\d\d', 5, 200)
snip('wave298_fin', r'W298 finalize one-pass', 3, 300)
snip('gen30', r'CLEAN-AT-BIRTH \d+\w+ gen', 3, 200)
snip('wave_no', r'波号 \d+=', 3, 250)
snip('R300', r'R\d\d\d：W\d+ 带', 3, 250)
snip('tab_tail', r'表尾 W\d+ 行', 3, 250)
snip('pool_no', r'池第 \d+ 枚', 3, 200)
snip('own_wave_no', r'第[一二三四五六七八九十百]+枚自有波', 3, 300)
snip('hop_ord', r'第[一二三四五六七八九十]+次连续 A-hop', 3, 300)
snip('above_ord', r'第[一二三四五六七八九十]+次连续 above-own-A', 3, 300)
snip('seats', r'bmc_rows=\d+', 5, 200)
snip('rows_register', r'engine_owner(?: 行|==bm-c) \d+', 5, 250)

io.open('results/_w300bmc_probe_markers2.txt', 'w', encoding='utf-8').write('\n'.join(out))
print(len(out))