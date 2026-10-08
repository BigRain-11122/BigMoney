# -*- coding: utf-8 -*-
import io
src = io.open('research/PERPETUAL_N1_W193_PREREG.md', encoding='utf-8', newline='').read()
i = src.find('\u00a77 \u8dd1\u540e\u5b9e\u8bc1')
out = io.open('results/_r904bma_s78_final.txt', 'w', encoding='utf-8', newline='\n')
out.write(src[i-4:])
out.close()
print('ok', i)
