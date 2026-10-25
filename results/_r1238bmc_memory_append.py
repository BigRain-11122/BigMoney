# -*- coding: utf-8 -*-
"""r1238 bm-c: append this window's pitfall card to the repo memory (LF, utf-8, one entry)."""
import io

LINE = (
 "- [2026-10-25 10:0x r1238 bm-c] N1 收口两枚判定律（W328 断窗续轮实弹）："
 "①**席位探针依赖本波 finalize 产物**——`Tools/n1_seat_probe.py --wave N` 断言 "
 "`results/perpetual_faces/n1_w{N-1}_results.json` 在位，故收口序固定为 六门→finalize→fivekeys→席位→§7/§8 回填"
 "（席位无法先于本波 finalize 发布·seat-first 律只是要求它在下一波 freeze 之前落地）；"
 "②**B 落位三面须同读**——W326/W327/W328 连续三波 naive B 全在 own-A 之下（BELOW 面），"
 "W329 首现 INSIDE 面（A walk 落到 naive B 窗之上、整段覆盖 own-A 内）→ "
 "`B_naive_inside_own_A=true / B_naive_below_own_A=false` 与 `B_seed_hop_disclosure=[]` 必须一起读，"
 "单看一支会误判 cascade 是否发生。How to apply：接续窗先跑 finalize 再点席位；读席位回执必读 relation_asserts 三面。\n"
)

p = 'CODELY.md'
t = io.open(p, encoding='utf-8').read()
assert t.endswith('\n')
io.open(p, 'a', encoding='utf-8', newline='\n').write(LINE)
print('appended', len(LINE.encode()), 'bytes')