# -*- coding: utf-8 -*-
# r705 bm-b: D-06 batch-3 ceremony tail -- TREASURE_REGISTRY in/out row + CODELY.md pool-domain
# pointer row reroute. Pure-LF hosts (probed), append-only, newline='' write to preserve LF.
import io

REG = 'knowledge/TREASURE_REGISTRY.md'
CODELY = 'CODELY.md'

reg_row = ('- 2026-10-05 02:2x bm-b r705 D-06 batch-3 sub-split 迁移仪式（D-20261002-06 域件 ≤30KB 再平衡·r703 仪式同款）：'
           'prescan 实弹 rc3 命中 research/pit-pool.md（research/ 全族 fail-closed 面）——集团拆件令 D-20261002-06（主文域件 ≤30KB·收口窗 10-07 12:00）'
           '授权 TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言：'
           '46 条 52,337B→本件 20 条 26,502B（认领/翻面语义/可见性/接管/双烧/停泊治理面）+pit-pool-edit.md 26 条 27,728B'
           '（池文件编辑/写入路径/settle/reland 窗/翻面执行手术/烧录机械/点火闸面）·条目字节和 48,301B 两件恒等·'
           '逐条 verbatim 迁移非手抄（变体⑤ bullet-less 三条 r598/r608/r605 随宿主 blob E16/E18 原样迁移零信息损失）·'
           'receipt=results/_r705bmb_pit_pool_split_receipt.json；在册路径 pit-pool.md 保留非删除·新增子件随 research/ 全族在册面暂。')

codely_append = (' r705 bm-b D-06 batch-3 sub-split（2026-10-05·域件 ≤30KB 再平衡）：pit-pool.md 52,337B/46 条'
                 '→本件 20 条 26,502B（认领/翻面语义/可见性/接管/双烧/停泊治理面）+pit-pool-edit.md 26 条 27,728B'
                 '（池文件编辑/写入路径/settle/reland 窗/翻面执行手术/烧录机械/点火闸面）·条目字节和 48,301B 两件恒等零丢失·'
                 '变体⑤ bullet-less 三条随宿主 blob 原样迁移·receipt=results/_r705bmb_pit_pool_split_receipt.json'
                 '——池文件字节编辑/settle/补翻手术/烧录机械/落闸动作前改读 pit-pool-edit.md。')

# 1) registry append (file ends with newline)
raw = open(REG, 'rb').read()
assert raw.count(b'\r\n') == 0 and raw.endswith(b'\n'), 'registry host shape unexpected'
cur = raw.decode('utf-8')
assert reg_row[:60] not in cur, 'registry row already present'
io.open(REG, 'w', encoding='utf-8', newline='').write(cur + reg_row + '\n')
print('registry row appended: %dB' % len(reg_row.encode('utf-8')))

# 2) CODELY.md pool-domain pointer row reroute (row-level append at row end)
raw = open(CODELY, 'rb').read()
assert raw.count(b'\r\n') == 0 and raw.endswith(b'\n'), 'codely host shape unexpected'
lines = raw.decode('utf-8').split('\n')
hits = [i for i, l in enumerate(lines) if '池域拆件' in l]
assert len(hits) == 1, 'pool-domain pointer row not unique: %r' % hits
i = hits[0]
assert lines[i].endswith('已入件（件内对账行为准）。'), 'row tail anchor mismatch: %r' % lines[i][-40:]
assert 'pit-pool-edit.md' not in lines[i], 'reroute already present'
lines[i] = lines[i] + codely_append
io.open(CODELY, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('codely row %d rerouted: +%dB (new row %dB, file now %dB)' % (
    i + 1, len(codely_append.encode('utf-8')), len(lines[i].encode('utf-8')),
    len(('\n'.join(lines)).encode('utf-8'))))
