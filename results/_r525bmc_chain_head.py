# _r525bmc_chain_head.py -- one-shot: read unified chain head (trials_ledger.total)
import json
d = json.load(open(r'K:\Fluxgroup\FluxGroup\quant\bigmoney\results\mass_trial\w3_judge.json', encoding='utf-8'))
print('trials_total', d['trials_ledger']['total'])
