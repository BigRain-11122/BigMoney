# -*- coding: utf-8 -*-
"""r738 bm-a W133 registry-insert MEASUREMENT pass 2 (post-0a/0b needles that
the first measure pass could not see verbatim).  Bloodline: r737
_r737bma_w132_measure2.py verbatim + W133 facts.
"""
import io

face = io.open(r".codely-cli\scratch_w132_face_source.txt", encoding="utf-8").read()
face = face.replace("W132", "W133")
face = face.replace("W131", "W132")
face = face.replace("W130", "W131")
face = face.replace('== 307_004 == 307_003 + 1', '== 309_004 == 309_003 + 1')
face = face.replace('set(range(307_004, 309_004))', 'set(range(309_004, 311_004))')
face = face.replace('== 68_902 == 68_901 + 1', '== 69_102 == 69_101 + 1')
face = face.replace('set(range(68_902, 69_102))', 'set(range(69_102, 69_302))')
face = face.replace('arith_a132', 'arith_a133')
face = face.replace('arith_b132', 'arith_b133')

for nd in [
    'W132 finalize one-pass bm-a r737',
    '= W132 bm-a r737 one-pass',
    'r736 W132 seat MSG-1726 tail',
    'first push raced origin forward 3',
    'bm-a r736 freeze 8cd6667e8',
    'W133+ projection',
    'W134+ projection',
]:
    print(f"count({nd!r}) = {face.count(nd)}")
