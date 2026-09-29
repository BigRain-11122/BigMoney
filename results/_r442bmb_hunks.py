diff = open('results/_r442bmb_w9w10_delta.txt',
            encoding='utf-8', errors='replace').read().split('\n')
c = 0
for l in diff:
    if l.startswith('@@'):
        print(l[:115])
        c += 1
        if c > 70:
            break
print('total lines', len(diff), 'hunks shown', c)
