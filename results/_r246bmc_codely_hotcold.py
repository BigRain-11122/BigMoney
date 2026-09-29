# r246 bm-c: CODELY.md hotcold reorg (append-after-near-line preventive move per <=10KB hard law)
# 1) move r236 GBK pit entry verbatim -> research/memory-archive/202609.md, leave cold pointer
# 2) insert W4 verdict pointer line (Project section, after r242 pointer line)
# zero-loss: archived line byte-identical to removed line; line-count arithmetic verified
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

cp = 'CODELY.md'
ap = r'research\memory-archive\202609.md'
raw = open(cp, 'rb').read().decode('utf-8')
sep = '\r\n' if '\r\n' in raw[:2000] else '\n'
lines = raw.split(sep)

idx_r236 = [i for i, l in enumerate(lines) if l.startswith('- [2026-09-29 20:0x r236 bm-c] GBK')]
assert len(idx_r236) == 1, 'r236 entry not unique: %d' % len(idx_r236)
i236 = idx_r236[0]
archived = lines[i236]

idx_r242 = [i for i, l in enumerate(lines) if l.startswith('- 冷层指针：r242 bm-c runner 外科手术四连坑族')]
assert len(idx_r242) == 1, 'r242 pointer not unique: %d' % len(idx_r242)
i242 = idx_r242[0]

pointer = ('- 冷层指针：r236 GBK 控制台吞链 runner 坑全文 verbatim=archive 202609.md'
           '『热冷整编 2026-09-30 r246 bm-c 窗批』节（法面已由全部在役 runner 入口 reconfigure 惯例'
           '+prereg §3 冻结条款+W4 runner 实装承载）。')
w4line = ('- [2026-09-30 02:1x r246 bm-c] W4 配额槽判决收编：VOLREGIME-TIMING-P1 0/3 全负判·'
          'zoo #96 量能原生择时族关单+重开注记（判负=合法产出·账本 350,018→352,021·attrition 行已落·'
          '池 SLOT-4 done 翻面）；正典=research/INNOVATION_QUOTA_W4_PREREG.md §7/§8'
          '+results/innovation_quota/VOLREGIME-TIMING-P1.json，勿按本行复述数字。')

lines[i236] = pointer
lines.insert(i242 + 1, w4line)

out = sep.join(lines)
assert archived not in out, 'zero-loss violated: archived line still present'
assert out.count(w4line) == 1 and out.count(pointer) == 1
open(cp, 'wb').write(out.encode('utf-8'))

asep = '\r\n' if open(ap, 'rb').read()[-200:].count(b'\r\n') else '\n'
with open(ap, 'ab') as f:
    blob = (asep + '## 热冷整编 2026-09-30 r246 bm-c 窗批' + asep +
            '（水位 9,731B+W4 判决指针行 append 后近 ≤10KB 线预防性整编·r246 收编轮当窗即办·行级零丢失校验=迁移行与热层删除行逐字节相同）' + asep +
            archived + asep)
    f.write(blob.encode('utf-8'))

print('CODELY lines %d -> %d; size %d -> %d bytes; archived verbatim %d bytes; zero-loss PASS'
      % (len(raw.split(sep)), len(lines), len(raw.encode('utf-8')), len(out.encode('utf-8')),
         len(archived.encode('utf-8'))))
