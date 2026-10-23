import io
p = 'results/_r1181bmc_prereg_derive_w298.py'
lines = io.open(p, encoding='utf-8', newline='').read().split('\n')
# line 335 (index 334) = MUST ordinals (new face)
lines[334] = r'    "\u7b2c\u4e94\u5341\u4e00\u6b21\u8fde\u7eed A-hop", "\u7b2c\u4e94\u5341\u4e8c\u6b21\u8fde\u7eed above-own-A",'
# line 349 (index 348) = MUST_NOT ordinals (stale face)
lines[348] = r'    "\u7b2c\u4e94\u5341\u6b21\u8fde\u7eed A-hop", "\u7b2c\u4e94\u5341\u4e00\u6b21\u8fde\u7eed above-own-A",'
io.open(p, 'w', encoding='utf-8', newline='').write('\n'.join(lines))
print('patched both ordinal lines')