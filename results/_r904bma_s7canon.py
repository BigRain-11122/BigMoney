# -*- coding: utf-8 -*-
import io
src = io.open('research/PERPETUAL_N1_W191_PREREG.md', encoding='utf-8', newline='').read()
i7 = src.find('\u00a77')
i8 = src.find('\u00a78')
iend = src.find('\u8dd1\u524d\u51bb\u7ed3')
out = io.open('results/_r904bma_s7canon.txt', 'w', encoding='utf-8', newline='\n')
out.write(src[i7:iend if iend > 0 else len(src)])
out.close()
print('W191 sec7 span:', i7, i8, len(src))
