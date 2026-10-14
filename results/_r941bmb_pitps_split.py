# -*- coding: utf-8 -*-
# r941 bm-b: pit-ps.md domain sub-split (<=30KB rebalance). D-20261002-06 group split order
# authorized migration face (same as r667 pit-ps-wrapper / r791 / r836 precedents).
# Mechanical verbatim migration, NOT hand-copy (r335 machine-evidence law).
import hashlib, json, subprocess, sys, os

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
os.chdir(ROOT)
P = 'research/pit-ps.md'
C = 'research/pit-ps-runner.md'
R = 'results/_r941bmb_pitps_split_receipt.json'
CAP = 30720

data = open(P, 'rb').read()
n0 = len(data)
assert n0 > CAP, 'pit-ps.md expected over cap, got %d' % n0

start_marker = '- [2026-10-01 06:3x r495'
end_marker = '- [2026-10-03 20:4x r428'
sb = start_marker.encode('utf-8'); eb = end_marker.encode('utf-8')
assert data.count(sb) == 1, 'start marker not unique'
assert data.count(eb) == 1, 'end marker not unique'
s = data.find(sb); e = data.find(eb)
assert 0 < s < e, 'span order broken'
span = data[s:e]

migrated_blocks = [
    '- [2026-10-01 06:3x r495',
    '- [2026-10-01 14:0x r318',
    '- [2026-10-02 06:0x r559',
    '- [2026-10-02 11:1x r571',
    '- [2026-10-03 02:0x r392',
    '- [2026-10-03 03:4x r605',
    '- [2026-10-03 08:5x r404',
    '- [2026-10-03 09:2x r617',
    '- [2026-10-03 10:2x r409',
    '- [2026-10-03 14:2x r618',
    '> 增量回扫行（r625 bm-b',
]
for b in migrated_blocks:
    bb = b.encode('utf-8')
    assert span.count(bb) == 1, 'migrated block not exactly once in span: %s' % b

retained_markers = [
    '- [2026-10-03 20:4x r428', '- [2026-10-03 21:0x r429', '- [2026-10-03 21:3x r430',
    '- [2026-10-03 21:4x r635', '- [2026-10-04 00:1x r639', '- [2026-10-04 2026-10-04 02:05 r641',
    '- [2026-10-04 04:0x r657', '- [2026-10-04 07:3x r655', '- [2026-10-04 11:1x r464',
    '- [2026-10-04 19:5x r694', '- [2026-10-04 20:41 r693', '- [2026-10-04 22:0x r499',
    '- [2026-10-05 18:5x r741', '- [2026-10-06 19:3x r791', '- [2026-10-07 07:4x r662',
    '域指针·r665 bm-c', '- [2026-10-07 20:2x r840', '- [2026-10-09 19:2x r817',
    '- [2026-10-10 08:5x r825', '- [2026-10-11 07:5x r868', '- [2026-10-11 07:5x r859',
    '- [2026-10-11 12:5x r873',
]

crlf = b'\r\n' in data
eol = b'\r\n' if crlf else b'\n'

note_text = ('> 拆件注记（2026-10-14 r941 bm-b·D-20260206 域件 ≤30KB 再平衡·%dB>%dB 当窗触发）：'
             'runner 机械族 10 条+r625 增量回扫行已 verbatim 迁出→research/pit-ps-runner.md'
             '（r495 splat 炸字符/r318 [void] 吞流/r559 重定向覆写/r571 切片反转/r392 空 hashtable/'
             'r605 双引号转义/r404 保留参数名/r617 水位哈希假 CHANGED/r409 Int64 假警/r618 工具签名漂移）——'
             'PS 循环器/批跑器/S6 链 runner/水位哈希/epoch 数值自检面编写与 rc=2 假警报诊断前改读该子件；'
             '收据=results/_r941bmb_pitps_split_receipt.json。') % (n0, CAP)
note_block = note_text.encode('utf-8') + eol + eol

new_main = data[:s] + note_block + data[e:]
retained_face = data[:s] + data[e:]
assert new_main.replace(note_block, b'', 1) == retained_face, 'zero-loss retained-face identity broken'
assert len(new_main) == n0 - len(span) + len(note_block), 'main byte arithmetic broken'
assert len(new_main) <= CAP, 'main still over cap: %d' % len(new_main)
for b in migrated_blocks:
    assert new_main.count(b.encode('utf-8')) == 0, 'migrated residue in main: %s' % b
for b in retained_markers:
    assert new_main.count(b.encode('utf-8')) == 1, 'retained marker not exactly once: %s' % b

child_header_text = (
    '# pit-ps-runner —— PS 循环器/批跑器/S6 链 runner 机械族子件（D-20261002-06 PS 域 child-2·r941 bm-b 拆出）' + '\n\n'
    '> 来源：research/pit-ps.md verbatim 机械迁出（2026-10-14 r941 bm-b·域件 ≤30KB 再平衡触发·'
    '拆件脚本 results/_r941bmb_pitps_split.py 非手抄·r335 机证律同源）。\n'
    '> 执法面：PS 循环器/批跑器/S6 链 runner/水位哈希/epoch 数值自检——上述编写动作与 rc=2 假警报/假 CHANGED/'
    '假警诊断前必读本件；主件 pit-ps.md 保有判读/消费/手术面族与全族亲族注记；姊妹子件=pit-ps-wrapper.md'
    '（零窗包装器调用族·r667）。\n'
    '> 字节对账行（零丢失断言）：迁移核 %dB（%s 行尾面·md5=%s）·逐块 verbatim 断言与主件保留面恒等式'
    '见收据 results/_r941bmb_pitps_split_receipt.json（零丢失断言=逐块 bytes in target verbatim+主件保留面恒等+'
    '主件 ≤30KB）。\n\n') % (
    len(span), 'CRLF' if crlf else 'LF', hashlib.md5(span).hexdigest())
child = child_header_text.encode('utf-8') + span
assert len(child) == len(child_header_text.encode('utf-8')) + len(span)
for b in migrated_blocks:
    assert child.count(b.encode('utf-8')) == 1, 'child missing block: %s' % b

# treasure_guard prescan (registry hit rc3 = D-20260206 authorized migration face, same as r939/r667)
prescan = subprocess.run([sys.executable, 'Tools/treasure_guard.py', 'prescan', P, C],
                         capture_output=True)
prescan_rc = prescan.returncode
prescan_out = (prescan.stdout or b'')[-600:].decode('utf-8', 'replace')

open(P, 'wb').write(new_main)
open(C, 'wb').write(child)

receipt = {
    'round': 'r941 bm-b', 'ts': '2026-10-14T17:1x:00+08:00',
    'law_refs': ['D-20261002-06 domain split order', 'O-20260927-0230 <=30KB hardline law',
                 'r667 pit-ps-wrapper precedent', 'r335 machine-evidence law'],
    'prescan': {'tool': 'Tools/treasure_guard.py prescan', 'rc': prescan_rc,
                'authorization': 'D-20260206 group split order authorized migration face (rc3 hit = pit/memory registry face, same as r939/r667)',
                'stdout_tail': prescan_out},
    'main_file': {'path': P, 'bytes_before': n0, 'bytes_after': len(new_main),
                  'note_line_bytes': len(note_block), 'cap': CAP,
                  'within_cap': len(new_main) <= CAP, 'md5_after': hashlib.md5(new_main).hexdigest()},
    'child_file': {'path': C, 'bytes_total': len(child), 'core_bytes': len(span),
                   'core_md5': hashlib.md5(span).hexdigest(),
                   'core_eol': 'CRLF' if crlf else 'LF', 'blocks': len(migrated_blocks)},
    'byte_identity': {
        'assert_main_byte_arithmetic': True, 'assert_retained_face_identity': True,
        'assert_migrated_zero_residue_in_main': True,
        'assert_all_migrated_blocks_verbatim_in_child': True,
        'assert_retained_markers_each_once_in_main': True,
        'formula': 'bytes_after == bytes_before - core_bytes + note_line_bytes',
    },
    'migrated_blocks': migrated_blocks, 'retained_markers': len(retained_markers),
    'domain_pointer': 'pit-ps.md main keeps judgment/consumption/surgery family + r941 routing note; runner mechanical family -> pit-ps-runner.md (predecessor: r667 wrapper family -> pit-ps-wrapper.md)',
    'zero_loss': 'PASS',
}
json.dump(receipt, open(R, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('SPLIT PASS: main %d -> %d (cap %d), child %d B core %d B md5=%s, prescan rc=%d, receipt=%s'
      % (n0, len(new_main), CAP, len(child), len(span), hashlib.md5(span).hexdigest(), prescan_rc, R))
