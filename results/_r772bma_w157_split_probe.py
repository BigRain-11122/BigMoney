# -*- coding: utf-8 -*-
# r772 bm-a: dump the post-chain assert-string regions verbatim (split-band forms)
import io

t = io.open(r'results/_r772bma_w157_src_block.txt', encoding='utf-8', newline='').read()
print('=== region 8400..10800 (assert strings with split bands) ===')
print(repr(t[8400:10800]))
