import io
import json
import os

doc = json.load(io.open('results/state_tilt/UNPINNEDCHOICE-2026-11-01.json', encoding='utf-8'))
print(doc['verdict'])
print(json.dumps(doc['summary'], indent=1))
for row in doc['rows']:
    if not row['pinned']:
        print('---')
        print(row['class'], row['source'], row['line'], 'decider=%r' % (row['decider'],))
        print('  note:', row['pin_note'])
        print('  outcome=%r alternate=%r swap=%s' % (row['outcome_today'], row['alternate_today'],
                                                     row['swap_changes_today']))
        for b in row['branches']:
            print('   ', b['side'], '|', b['expr'][:60], '|', b['vintage'])
print('=== pinned rows ===')
for row in doc['rows']:
    if row['pinned']:
        print(row['class'], row['source'], row['line'], row['decider'], '|', row['pinned_by'][:1])