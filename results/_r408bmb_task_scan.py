import json, glob, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
for f in sorted(glob.glob(r'fleet\tasks\*.json')):
    try:
        j = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        print('PARSE-FAIL: %s: %s' % (f, e)); continue
    st = j.get('status'); pri = j.get('priority', ''); imm = j.get('immediate')
    if st in ('open', 'claimed') or imm:
        spec = str(j.get('spec', j.get('type', '')))[:100].replace('\n', ' ')
        print('%s: %s | pri=%s | imm=%s | claimed_by=%s | %s' % (st.upper(), f, pri, imm, j.get('claimed_by'), spec))
print('scan done: %d files' % len(glob.glob(r'fleet\tasks\*.json')))
