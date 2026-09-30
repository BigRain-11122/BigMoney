import re
draft = open('results/_r464bma_w13_runner_draft.py', encoding='utf-8').read()
lines = draft.splitlines()
i = draft.find('def _load_exclusion_rows_w13')
seg_lines = draft[i:].splitlines()
# print loader body first 120 lines
for j, ln in enumerate(seg_lines[:120]):
    print('%5d: %s' % (j+1, ln))
