# -*- coding: utf-8 -*-
# r772 bm-a: dump post-chain tail region verbatim
import io

t = io.open(r'results/_r772bma_w157_src_block.txt', encoding='utf-8', newline='').read()
print('=== region 10800..13720 ===')
print(repr(t[10800:13720]))
