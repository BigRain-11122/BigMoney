import json, time, datetime

# state update: round_no 443 -> 444 (this round was r443)
p = 'state-bm-a.json'
d = json.load(open(p, encoding='utf-8'))
d['round_no'] = 444
d['did'] = ('r443: T-101-V4-A11-XSELECT landed (input-feature cross-sectional selection '
           'subline first test per A10 sec.8 downstream pointer): prereg FROZEN + runner '
           '+ seeds 20315000/20315500 three-step law -> burn#4 141.3s one-shot FV_PASS 0/24 '
           '(true skill line 1.2504 = batch-own random-selection null pool mu 0.1590/sigma '
           '0.2161, N_eff 344,080; best cell U4|f_c2|top2|x1 sharpe 0.4994 = 40% line '
           'position, clean negative E[FP] 1.20 nominal 0 realized; f_rsv30/f_roc20 order '
           'BELOW random = negative-information face; only positive-excess face U4|f_c2 '
           '+10.4%/x2 +8.3% = high-beta member tilt mirror d6 0.94-0.97 same trap family '
           'as r442 C1|588000; 24/24 D6-REJECT structural class-beta per sec.1 '
           'pre-declaration; maxdd concentration finding 20/24 breach -35% floor) = '
           'input-feature route four-subline state all-closed (timing A2/A9/A10 + '
           'selection A11), remaining = predictor/conditional faces; zero-correction '
           'burns #1-#3 = pre-output wiring failures (index-type reindex silent all-NaN, '
           'string/datetime key mix empty intersection, numpy scatter broadcast), '
           'judgment zero-touch; S6 37 legs rc=0 x36 + update_lhb rc=3 source-restatement '
           'quarantine r229 precedent; no new bar 3 trigger legs legit-skip')
d['verify'] = ('smoke 26/26; runner selftest 7/7; G-P1/G-ACCEPT live-read PASS; SEED '
              'three-step law (120 int zero-collision band-empty first-els distinct); '
              'ledger 344,056->344,080 +24 linear trials_ledger key landed; dualrun '
              'ZERO-DRIFT streak 24/3; CODELY 10,220B back under 10KB after in-window '
              're-arch (r442 flow verbatim to archive)')
d['next'] = ('r444: (a) predictor/conditional-face candidate draft (vol/risk '
             'conditioning, non-selection non-timing, fresh prereg + D6 first); '
             '(b) 09-29/09-30 bar landing watch -> trigger chain; (c) 10-01 '
             'month-first triple (science_audit + monthly_briefing + self_review); '
             'next 5x = bm-a r445 HANDOVER check')
now = '2026-09-29T19:5x:xx+08:00'
d['last_round_at'] = now
d['current_task'] = ('r443 closed: A11 xselect verdict batch landed (0/24, input-feature '
                     'cross-sectional selection CLOSED); next=predictor/conditional face '
                     'draft + bar watch')
d['updated'] = now
json.dump(d, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

# heartbeat update (epoch MUST be JSON int; clock_read T-separated ISO 8601)
h = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
h['last_seen'] = '2026-09-29 19:5x'
h['current_task'] = 'r443 closed: A11 xselect 0/24 verdict landed; next predictor/conditional draft'
h['verdict'] = 'healthy'
h['heartbeat_epoch_utc'] = int(time.time())
h['clock_read'] = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
json.dump(h, open('fleet/machines/bm-a.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)

# self-verify (smoke F7 face): epoch int type + clock_read T-separated
h2 = json.load(open('fleet/machines/bm-a.json', encoding='utf-8'))
assert isinstance(h2['heartbeat_epoch_utc'], int), 'epoch must be int'
assert 'T' in h2['clock_read'] and ' ' not in h2['clock_read'], 'clock_read must be T-separated'
s2 = json.load(open('state-bm-a.json', encoding='utf-8'))
assert s2['round_no'] == 444
print('state 444 + heartbeat OK; epoch=', h2['heartbeat_epoch_utc'],
      'int isinstance', isinstance(h2['heartbeat_epoch_utc'], int),
      'clock=', h2['clock_read'])
