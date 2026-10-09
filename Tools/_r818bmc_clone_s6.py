# -*- coding: utf-8 -*-
"""r818 bm-c 1-gen clone helper: s6 driver + ignite from r817 (mechanism
verbatim, round-numbered paths only)."""
import io

src = io.open('Tools/_r817bmc_s6.py', encoding='utf-8').read()
out = (src.replace('_r817bmc_s6_log', '_r818bmc_s6_log')
          .replace('r817 bm-c S6 chain', 'r818 bm-c S6 chain')
          .replace('r817 watch-faces', 'r818 watch-faces'))
io.open('Tools/_r818bmc_s6.py', 'w', encoding='utf-8', newline='\n').write(out)

src2 = io.open('Tools/_r817bmc_s6_ignite.py', encoding='utf-8').read()
out2 = (src2.replace('_r817bmc_s6_runner', '_r818bmc_s6_runner')
            .replace('"Tools", "_r817bmc_s6.py"', '"Tools", "_r818bmc_s6.py"')
            .replace('r817 bm-c', 'r818 bm-c')
            .replace('Tools/_r816bmc_s6_ignite.py', 'Tools/_r817bmc_s6_ignite.py'))
io.open('Tools/_r818bmc_s6_ignite.py', 'w', encoding='utf-8', newline='\n').write(out2)
print('cloned s6 driver+ignite ok')
