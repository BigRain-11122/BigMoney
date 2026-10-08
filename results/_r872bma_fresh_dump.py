# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
d = json.load(io.open(r'results\_r872bma_back183_expect_dump.json', encoding='utf-8'))
m = dict(d['BACK183'])
for tok in ['@ORDINALS@', '@SEATPUB@', '@SEATSENT@', '@S55@']:
    print('=' * 20, tok, '=' * 20)
    print(m[tok])
print('=' * 20, '@CHAIN@ tail', '=' * 20)
print(m['@CHAIN@'][-120:])
print('=' * 20, '@KLT@ tail', '=' * 20)
print(m['@KLT@'][-100:])
print('=' * 20, '@SEMT@', '=' * 20)
print(m['@SEMT@'])
print('=' * 20, '@OWNCHAIN@', '=' * 20)
print(m['@OWNCHAIN@'])
