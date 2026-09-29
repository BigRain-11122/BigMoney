p = 'CODELY.md'
lines = open(p, encoding='utf-8').read().splitlines()

r443_entry = ('- [2026-09-29 19:4x r443 bm-a] 跨索引型 reindex 静默全 NaN+日期键混型空交集坑'
 '（T-101-V4-A11-XSELECT burn#1-3 接线族·判据零触碰·r251/r280 先例族）：'
 '①pandas RangeIndex 系列直 reindex 到 DatetimeIndex=不报错静默产全 NaN——跨面接线必先 Series(x.values, index=dates) '
 '统一日期键再 reindex；②面板字符串日期列（tpl cutoff 字符串比较面）与 DatetimeIndex 计算面混用=交集静默空不崩溃'
 '（下游 max() on empty 显形）——该接缝=跨面接线必查；'
 '③numpy 高级索引散布赋值 rows 必须显式 [:,None] 广播。三次崩溃全在产物落盘与账本 append 之前=零双记。'
 'A11 判决=输入特征横截面选择子线关闭 0/24——四子线态（择时 A2/A9/A10+选择 A11）全谱判负·残余去向=预测器/条件化面'
 '（数字面=正典三件·指针=prereg §7/8+results/t101_v4_a11_xselect.json+attrition 27/73 行+臂表 A11 行）。')

i = [j for j, l in enumerate(lines) if l.startswith('- [2026-09-29 19:4x r443 bm-a]')]
assert len(i) == 1, 'r443 line not unique: %d' % len(i)
lines[i[0]] = r443_entry

open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines) + '\n')
import os
print('CODELY.md size =', os.path.getsize(p), 'bytes (under 10240:', os.path.getsize(p) < 10240, ')')
