# -*- coding: utf-8 -*-
"""r664 bm-a: append T-165 progress line for v0.3 census slice (programmatic JSON edit)."""
import json

P = 'fleet/tasks/T-2026-10-04-165-P1.json'
raw = open(P, 'rb').read()
d = json.loads(raw.decode('utf-8', errors='replace'))

add = (" | r664 follow-up: R3 third cut v0.3 ALGORITHMIC IGNITION CENSUS delivered "
       "(scripts/theme_ignition_census.py selftest 7/7 run 9.4s; "
       "results/theme_ring/theme_events_v03_algorithmic.json+csv: 1,723 panel scan / 1,012 eligible / "
       "1,919 rule-defined episodes across 823 ETFs, evidence_cutoff 2026-09-30 -- O-2103 sec.2 >=30-event "
       "target met 60x; honest disclosures: 2024-09-30 single day 436 episodes (23%), 924 window 693 (36%) = "
       "market-wide beta domination (cluster stratification mandatory for any judgment consumption); "
       "CEO anchor match 2/16 (+-30td, BROKER +1d / MIL +7d) = burst-confirmation rule is a LAGGING "
       "confirmer not a narrative-start detector; famous14 median ign->peak +53.4% vs rest +36.8% = E25 "
       "survivor-premium quantified at episode level; E28 dual-law card + TREASURE_REGISTRY row + library "
       "sec.8 landed; descriptive census, zero registration claims, any judgment use requires NEW frozen prereg)")

if 'r664 follow-up' not in d.get('note', ''):
    d['note'] = d.get('note', '') + add
    with open(P, 'w', encoding='utf-8', newline='\n') as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    # self-check per state.json write law
    back = json.loads(open(P, 'rb').read().decode('utf-8', errors='replace'))
    assert 'r664 follow-up' in back['note'], 'note append lost'
    assert back['status'] == 'done' and back['claimed_by'] == 'bm-a'
    print('T-165 note appended + json.loads self-check PASS')
else:
    print('already present, skip')
