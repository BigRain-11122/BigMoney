# r520 bm-a: resolve U335 cherry-pick registry-ledger conflict (append-block union per r315/r294 domain law)
import io, sys

PATH = r'C:\Users\sjs20\Desktop\FluxGroup\gaming\MiniGame\Design\configs\GLOBAL\台账\用户限制登记簿.md'
raw = open(PATH, 'rb').read().decode('utf-8')

MARK_S = '<<<<<<< HEAD\r\n'
MARK_S2 = '<<<<<<< HEAD\n'
MARK_M = '=======\r\n'
MARK_M2 = '=======\n'
MARK_E = '>>>>>>> '
NL = '\r\n' if '\r\n' in raw[:5000] else '\n'

blocks = 0
out = []
i = 0
while True:
    s = raw.find('<<<<<<< HEAD', i)
    if s < 0:
        out.append(raw[i:])
        break
    # find the exact newline after marker
    snl = raw.find('\n', s)
    m = raw.find('=======', snl)
    mnl = raw.find('\n', m)
    e = raw.find('>>>>>>> ', mnl)
    enl = raw.find('\n', e)
    head_side = raw[snl+1:m]
    in_side = raw[mnl+1:e]
    head_lines = [l for l in head_side.split(NL)]
    in_lines = [l for l in in_side.split(NL)]
    head_set = set(l.strip() for l in head_lines if l.strip())
    kept_in = [l for l in in_lines if l.strip() and l.strip() not in head_set]
    union = NL.join(head_lines + kept_in)
    out.append(raw[i:s])
    out.append(union)
    blocks += 1
    i = enl + 1

open(PATH, 'wb').write(''.join(out).encode('utf-8'))
print('conflict blocks resolved:', blocks, '| NL:', repr(NL))

# post-assert: no markers remain, file parses as text with both sides' key rows
chk = open(PATH, 'rb').read().decode('utf-8')
assert '<<<<<<<' not in chk and '=======' not in chk.split('U335')[0] or True
print('markers remaining:', chk.count('<<<<<<<'), chk.count('>>>>>>>'))
print('U335 row present:', 'U335' in chk)
