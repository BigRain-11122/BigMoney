t = open(r"results\_w229bmc_20261013_probe.py", encoding="utf-8").read()
probes = ['EIGHTY-NINTH', 'EIGHTY-NINTH ', 'NINETIETH', 'NINETIETH ', 'NINETY-FIRST', 'EIGHTY-EIGHTH',
          'range(16, 229)', 'range(16, 228)', 'N1_BANDS[228]', 'N1_BANDS[229]', '925_389', '923_189', '499_520',
          '(518_404, 520_403)', '(520_604, 520_803)', 'owner_total == 218', 'bmc_rows) == 58',
          '"ordinal": 219', '"bmc_ordinal": 59',
          '4e30ddf69', 'e6c8441aa', '842f817ad', '03bca8089', '95e210be1', '6744db794', 'c9e9e83b8',
          'W227', 'W228', '20261013', 'r959', 'r957', 'r958',
          'A-hops-prior-B NINETIETH instance ', 'EIGHTY-NINTH instance',
          '(516_404, 518_403)', '(518_604, 520_603)', '(518_404, 518_603)', '501_720', '927_589']
for p in probes:
    print(repr(p), '->', t.count(p))
print('LEN', len(t))
