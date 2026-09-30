import re
live = open('scripts/trial_labor_w12.py', encoding='utf-8').read()
lines = live.splitlines()

def show(marker, before=3, after=18, label=''):
    idx = [i for i, l in enumerate(lines) if marker in l]
    print('### %s marker=%r hits=%d' % (label, marker, len(idx)))
    for i in idx[:2]:
        for j in range(max(0, i-before), min(len(lines), i+after)):
            print('%5d: %s' % (j+1, lines[j]))
        print('   ...')

show('rsqr_segmented_survival', before=6, after=14, label='finalize payload')
show('rsqr_face_judgment', before=6, after=14, label='judge final payload')
show('gvvvsktsamsr_seg', before=2, after=2, label='gvvvsktsamsr_seg occurrences')
