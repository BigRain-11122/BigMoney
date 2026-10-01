import io
txt = open('scripts/perpetual_faces_n1.py', encoding='utf-8').read()
lines = txt.splitlines()
out = io.open('results/_r561bma_n1_probe.txt', 'w', encoding='utf-8')
# (a) 55 WAVE_CONFIGS entry with context
for i, l in enumerate(lines):
    if '55: {"batch"' in l:
        out.write('=== 55 CONFIGS entry (i=%d) ===\n' % i)
        out.write('\n'.join(lines[i - 2:i + 17]) + '\n\n')
# (b) W55 selftest leg span
start = None
for i, l in enumerate(lines):
    if 'W55 materializer face' in l:
        start = i - 2
        break
if start is not None:
    end = None
    for j in range(start + 5, len(lines)):
        if lines[j].strip().startswith('# ---') and 'materializer' not in lines[j]:
            end = j
            break
    out.write('=== W55 selftest leg (lines %d..%d) ===\n' % (start, end))
    out.write('\n'.join(lines[start:end]) + '\n\n')
# (c) T-141 anchor
for i, l in enumerate(lines):
    if '# --- T-141 s2 lane face' in l:
        out.write('=== T-141 anchor at line %d ===\n' % i)
        out.write('\n'.join(lines[i:i + 4]) + '\n')
out.close()
print('ok')
