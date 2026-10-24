# -*- coding: utf-8 -*-
import io
t = io.open('results/_r1208bmc_w314_sixgate.py', encoding='utf-8').read()
keys = ['703901', '705901', '706101', '708101', 'w314', 'w313', 'W314', 'W313',
        'r1208', 'r1206', 'm312', 'k313pos', 'after313', '_set_wave(314)',
        '_set_wave(313)', '_set_wave(305)', "'315: {'", "'314: {'", '77th',
        '1112941', '686520', '1,112,941', '686,520', 'WAVE = 314', 'PREV = 313',
        'shard-7/9/10 finished 19:49:36-38', '312']
for k in keys:
    print('%-40r %d' % (k, t.count(k)))