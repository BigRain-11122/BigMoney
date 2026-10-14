src = open('results/_r998bma_s6.py', encoding='utf-8').read()
src = src.replace('_r998bma_s6_chain.log', '_r1001bma_s6_chain.log')
src = src.replace('r998 bm-a S6 chain driver (32 legs, log-to-file, exit-code capture).',
                  'r1001 bm-a S6 chain driver (successor relaunch; regenerates the 32 faces discarded at S0 estate absorption).')
assert '_r1001bma_s6_chain.log' in src and 'r1001 bm-a S6 chain driver' in src
open('results/_r1001bma_s6.py', 'w', encoding='utf-8', newline='').write(src)
print('chain script written')
