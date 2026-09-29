import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open('results/_r239bmc_s6_chain.py', encoding='utf-8').read()
src = src.replace('_r239bmc_s6_chain', '_r240bmc_s6_chain')
src = src.replace('round.: .r239', 'round": "r240').replace('"round": "r239"', '"round": "r240"')
src = src.replace('# r239 bm-c S6 maintenance chain runner',
                  '# r240 bm-c S6 chain runner (37 legs, r239 mirror; no new bar since 09-29 20:36 klc2 landing -> no REGIME_GUARD enforce)')
open('results/_r240bmc_s6_chain.py', 'w', encoding='utf-8').write(src)
print('r240 chain runner written')
