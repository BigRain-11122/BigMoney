t = open(r"results\_w229bmc_20261013_probe.py", encoding="utf-8").read()
probes = ['_r959bmc_w228_fivekey_receipt', 'PERPETUAL_N1_W228_PREREG', 'PERPETUAL_N1_W229_PREREG',
          'W229 freeze receipt = 58th owned', 'W228 freeze receipt = 58th owned',
          '("W228 finalize LANDED', 'zero in-flight declared seats")',
          'W229 burn window', 'W230 burn window', 'STAIRCASE GEOMETRY',
          'candidate = 59th per the same continuity', '(57 live rows + W228 candidate at r959 splice)',
          '-> 218th wave, bm-c 59th owned', 'leg0 failed: W228 row drift (bm-c r959 splice face)',
          '(expect 218/58 post-W228-splice per the r959 splice receipt ordinal faces)',
          'A-hops-prior-B staircase EIGHTY-NINTH', 'STAIRCASE GEOMETRY EIGHTY-NINTH']
for p in probes:
    print(repr(p), '->', t.count(p))
# show docstring boundaries
i = t.find('"""'); j = t.find('"""', i + 3) + 3
print('docstring span:', i, j, '| body-only counts:')
body = t[j:]
for p in ['EIGHTY-NINTH ', 'NINETIETH ', 'r959', 'r957', 'r958', '4e30ddf69', 'e6c8441aa', '842f817ad', '03bca8089', '95e210be1', '6744db794', '923_189']:
    print(' body', repr(p), '->', body.count(p))
