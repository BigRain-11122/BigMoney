import io
src = open(r'results\_r890bma_s6_driver.py', encoding='utf-8').read()
s2 = src.replace('_r890bma_s6_chain', '_r900bma_s6_chain')
s2 = s2.replace('r890 bm-a S6 chain driver (W189 burn in-flight engine-autonomous; 10-08 sina late-bar watch continues) (r889 bloodline rolled one generation)',
               'r900 bm-a S6 chain driver (W193 seat published; 10-09 pre-market no-new-bar window expected; panel 10-08) (r890 bloodline rolled one generation)')
s2 = s2.replace('new_bar = post_date == "2026-10-08"', 'new_bar = post_date == "2026-10-09"')
assert s2 != src and '2026-10-09' in s2 and '_r900bma_s6_chain' in s2, 'replace failed'
open(r'results\_r900bma_s6_driver.py', 'w', encoding='utf-8', newline='').write(s2)
import ast
ast.parse(s2)
print('written + AST ok')
