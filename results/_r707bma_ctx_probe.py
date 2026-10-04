import io, re
lines = io.open('logs/autofill.log', 'rb').read().decode('utf-8', errors='replace').splitlines()
out = []
# 1) when did "origin moved the pool past HEAD" start appearing today
first = None
for l in lines:
    if '2026-10-05' in l and 'origin moved the pool' in l:
        if first is None:
            first = l
        out.append('R351: ' + l[:180])
# 2) the shard-0 crash confirm context (5 lines before/after)
idx = [i for i, l in enumerate(lines) if '02:10:03 crash-fuse CONFIRM' in l]
for i in idx:
    out.append('--- CONFIRM context ---')
    for j in range(max(0, i-6), min(len(lines), i+3)):
        out.append(lines[j][:200])
# 3) how runners are launched / logs
s = io.open('Tools/autofill.py', 'rb').read().decode('utf-8', errors='replace')
for m in re.finditer(r'(stdout|stderr|Popen|log_file|\.log|DEVNULL)', s):
    a = max(0, m.start()-100)
    seg = s[a:m.start()+150].replace('\n', ' | ')
    out.append('AUTOFILL: ' + seg)
io.open('results/_r707bma_ctx.txt', 'w', encoding='utf-8').write('\n'.join(out)[:9000])
print('lines', len(out))
