import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
for fn in ('cmd_screen_prep', 'cmd_screen_finalize', 'cmd_judge_prep'):
    i = draft.find('def ' + fn)
    seg = draft[i:i+900]
    print('=' * 30, fn)
    print(seg[:850])
    print()
