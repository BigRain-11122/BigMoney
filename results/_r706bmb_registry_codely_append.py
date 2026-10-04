# -*- coding: utf-8 -*-
# r706 bm-b: D-06 batch-3 ceremony tail -- TREASURE_REGISTRY in/out row + CODELY.md
# protocol-domain pointer row reroute. Pure-LF hosts (probed), append-only, newline='' write.
import io

REG = 'knowledge/TREASURE_REGISTRY.md'
CODELY = 'CODELY.md'

reg_row = ('- 2026-10-05 03:0x bm-b r706 D-06 batch-3 sub-split 迁移仪式（D-20261002-06 域件 ≤30KB 再平衡·r703/r705 仪式同款）：'
           'prescan 实弹 rc3 命中 research/pit-protocol.md（research/ 全族 fail-closed 面）——集团拆件令 D-20261002-06（主文域件 ≤30KB·收口窗 10-07 12:00）'
           '授权 TREASURE_PROTECTION_LAW §2 迁移仪式三件齐：①prescan rc3 留痕（本行）②出入记录本行 ③零丢失断言：'
           '53 条 50,756B→本件 28 条 28,386B（轮协议核心：令扫/恢复分类/票让路/收养/猝死取号/state 簿记/共享记忆 union/字符面/lane_io 守卫/inbox）'
           '+pit-protocol-d19.md 13 条 12,164B（D-19 决策/orders 水位消费与内容寻址+水位探针族）'
           '+pit-protocol-judge.md 12 条 13,506B（prereg 准入闸/出场轴/finalize 记账与 AA 断言/judged 声明轴/E1 对账/断言容差面）'
           '·条目字节和 46,837B 三件恒等·逐条 verbatim 迁移非手抄（变体⑥ 行内融合两条：r294 前导空格 bullet 形随宿主 E38·r460 无换行内联形随宿主 E46·原样迁移零信息损失）·'
           'receipt=results/_r706bmb_pit_protocol_split_receipt.json；在册路径 pit-protocol.md 保留非删除·新增子件随 research/ 全族在册面暂。')

codely_append = (' r706 bm-b D-06 batch-3 sub-split（2026-10-05·域件 ≤30KB 再平衡）：pit-protocol.md 50,756B/53 条'
                 '→本件 28 条 28,386B（轮协议核心：令扫/恢复分类/票让路/收养/猝死取号/state 簿记/共享记忆 union/字符面/lane_io 守卫/inbox）'
                 '+pit-protocol-d19.md 13 条 12,164B（D-19 决策/orders 水位消费与内容寻址+水位探针族）'
                 '+pit-protocol-judge.md 12 条 13,506B（prereg 准入/出场轴/finalize 记账与 AA 断言/judged 声明轴/E1 对账）'
                 '·条目字节和 46,837B 三件恒等零丢失·变体⑥ 行内融合两条随宿主 blob 原样迁移·receipt=results/_r706bmb_pit_protocol_split_receipt.json'
                 '——D-19 消费/水位探针动作前改读 pit-protocol-d19.md·prereg 闸/finalize/judged 消费动作前改读 pit-protocol-judge.md。')

# 1) registry append (file ends with newline)
raw = open(REG, 'rb').read()
assert raw.count(b'\r\n') == 0 and raw.endswith(b'\n'), 'registry host shape unexpected'
cur = raw.decode('utf-8')
assert reg_row[:60] not in cur, 'registry row already present'
io.open(REG, 'w', encoding='utf-8', newline='').write(cur + reg_row + '\n')
print('registry row appended: %dB' % len(reg_row.encode('utf-8')))

# 2) CODELY.md protocol-domain pointer row reroute (row-level append at row end)
raw = open(CODELY, 'rb').read()
assert raw.count(b'\r\n') == 0 and raw.endswith(b'\n'), 'codely host shape unexpected'
lines = raw.decode('utf-8').split('\n')
hits = [i for i, l in enumerate(lines) if '协议域拆件' in l]
assert len(hits) == 1, 'protocol-domain pointer row not unique: %r' % hits
i = hits[0]
assert lines[i].endswith('receipt _r439bmc_pit_protocol_heal.json）。'), 'row tail anchor mismatch: %r' % lines[i][-40:]
assert 'pit-protocol-d19.md' not in lines[i], 'reroute already present'
lines[i] = lines[i] + codely_append
io.open(CODELY, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('codely row %d rerouted: +%dB (new row %dB, file now %dB)' % (
    i + 1, len(codely_append.encode('utf-8')), len(lines[i].encode('utf-8')),
    len(('\n'.join(lines)).encode('utf-8'))))
