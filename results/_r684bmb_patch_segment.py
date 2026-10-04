# r684 bm-b: patch segment label in fresh lowamp rows (172d -> window end
# disclosed; actual n_days carried in window field = 176). 2-row surgical
# rewrite of THIS ROUND's own uncommitted product (regenerable artifact).
import io, json

FP = r'results/contest_p1/burn_pending_lowamp.jsonl'
rows = [json.loads(l) for l in io.open(FP, encoding='utf-8') if l.strip()]
assert len(rows) == 2, rows
for r in rows:
    r['segment'] = ("backtest (lowamp deep axis, D2 lockbox truncation "
                    "2026-09-22; window end disclosed vs 181d baselines)")
with io.open(FP, 'w', encoding='utf-8', newline='\n') as f:
    for r in rows:
        f.write(json.dumps(r, ensure_ascii=False, sort_keys=True) + '\n')
print('patched', len(rows), 'rows; segments now:',
      [r['segment'][:60] for r in rows])
