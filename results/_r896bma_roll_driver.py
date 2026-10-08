src = open('results/_r895bma_s6_driver.py', encoding='utf-8').read()
n = src.replace('_r895bma_s6_chain.json', '_r896bma_s6_chain.json')
n = n.replace(
    '# r895 bm-a S6 chain driver (W191 finalize landed this window via engine '
    'materializer; 10-09 pre-market no new bar expected, panel stays at 10-08 '
    'cutoff; paper legs run idempotent) (r892 bloodline rolled one generation)',
    '# r896 bm-a S6 chain driver (CODELY minisplit + treasure_guard weld window; '
    '02:5x pre-market no new bar expected, panel stays at 10-08 cutoff; paper '
    'legs run idempotent) (r895 bloodline rolled one generation)')
n = n.replace('new_bar = post_date == "2026-10-08"',
              'new_bar = post_date == "2026-10-09"')
assert '_r896bma_s6_chain.json' in n
assert 'post_date == "2026-10-09"' in n
assert '_r895bma_s6_chain.json' not in n
open('results/_r896bma_s6_driver.py', 'w', encoding='utf-8', newline='').write(n)
print('r896 driver rolled; residual 895 refs:', n.count('r895'))
