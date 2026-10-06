raw = open('results/runnable_pool.json', encoding='utf-8', newline='').read()

def block_of(nid):
    i = raw.find('"' + nid + '"')
    assert i > 0
    j = raw.rfind('{', 0, i)
    depth = 0; k = j
    while k < len(raw):
        if raw[k] == '{': depth += 1
        elif raw[k] == '}':
            depth -= 1
            if depth == 0: break
        k += 1
    return raw[j:k+1]

for nid in ['FUND-QUALITY-P1-NULLS', 'FUND-DIVLOWVOL-P1-NULLS']:
    b = block_of(nid)
    print('===', nid, '(%d bytes) ===' % len(b))
    print(b[:1400])
    print()

# format probe: indent + EOL of the host file
lines = raw.split('\n')
import collections
eol_crlf = raw.count('\r\n')
eol_lf = raw.count('\n') - eol_crlf
first_key = [l for l in lines if l.strip().startswith('"id"')][0]
print('EOL: CRLF=%d LF-only=%d' % (eol_crlf, eol_lf))
print('sample key line repr:', repr(first_key[:40]))
# indent of entries array items
i = raw.find('"entries"')
print('entries region snippet repr:', repr(raw[i:i+120]))
