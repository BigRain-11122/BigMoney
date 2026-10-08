import json
import sys

sys.path.insert(0, 'scripts')
from regime5_validation import state_table, MAIN_START, PANEL_PATH, LABELS_PATH, DEFAULT_N_CONF  # noqa
from regime5_labeler import _load as load_panel
import regime_style_matrix as rsm

panel = load_panel(PANEL_PATH)
doc = json.load(open(LABELS_PATH, encoding='utf-8'))
labels = doc['labels']
dates = [r['date'] for r in labels]
raw = [r['state'] for r in labels]
pidx = {r[0]: i for i, r in enumerate(panel)}
closes = [r[1] for r in panel]
r_next = [None] * len(labels)
for j, d in enumerate(dates):
    p = pidx[d]
    if p + 1 < len(panel):
        r_next[j] = closes[p + 1] / closes[p] - 1.0
rb = [j for j in range(len(labels)) if r_next[j] is not None]
win_stats = [j for j in rb if dates[j] >= MAIN_START]
eff3 = rsm.confirm_window(raw, DEFAULT_N_CONF)
raw_tab = state_table(raw, r_next, win_stats)
eff_tab = state_table(eff3, r_next, win_stats)
print('main-window RAW-label face (disclosure only, NOT the frozen gate face):')
for s in ('BULL', 'BEAR', 'GRIND', 'CHOP', 'SUPPORT'):
    rr = raw_tab['states'][s]
    print('%-8s n=%5d d=%+.2f bp t=%s' % (s, rr['n'], rr['d'] * 1e4,
                                          'NA' if rr['t'] is None else '%.2f' % rr['t']))
print('raw-state counts in main window:',
      {s: raw_tab['states'][s]['n'] for s in ('BULL', 'BEAR', 'GRIND', 'CHOP', 'SUPPORT')})
# eff3 vs raw disagreement rate in window
dis = sum(1 for j in win_stats if eff3[j] != raw[j])
print('eff3-vs-raw disagreement days in window: %d / %d' % (dis, len(win_stats)))
