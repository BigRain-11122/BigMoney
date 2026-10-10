import io, re
t = io.open('scripts/allocation_policy_scan.py', encoding='utf-8', errors='replace').read()
for kw in ('COST_PER_SIDE', 'def _cost_check', '_etf_cost_leg_mask'):
    for mm in list(re.finditer(re.escape(kw), t))[:5]:
        i = mm.start()
        print('===', kw, '@', i)
        print(t[max(0, i - 220):i + 420])
        print('---')
        break
