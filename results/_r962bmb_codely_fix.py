# r962 fix: normalize appended CODELY.md entry line ending to file convention,
# then complete the state.json note fix (leg 2 of _r962bmb_codely_append.py).
# Leg 1 wrote the entry via text-mode 'a' -> trailing \n translated to \r\n
# (+1B). Byte-level inspection + byte-level tail fix only.
import json

BM = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
LOG = BM + r'\results\_r962bmb_closeout.log'

def W(m):
    import datetime
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S') + ' ' + str(m) + '\n')

raw = open(BM + r'\CODELY.md', 'rb').read()
crlf = raw.count(b'\r\n')
lf_only = raw.count(b'\n') - crlf
W('CODELY.md line-ending census: crlf=%d lf_only=%d size=%d tail=%r'
  % (crlf, lf_only, len(raw), raw[-60:]))
mine = '[2026-10-15 '.encode('utf-8')
# my entry is the last one; check tail bytes
tail = raw[-200:]
if tail.endswith(b'\r\n'):
    if lf_only >= crlf:
        # LF-convention file: strip my stray \r (last byte pair)
        fixed = raw[:-2] + b'\n'
        open(BM + r'\CODELY.md', 'wb').write(fixed)
        W('entry tail normalized CRLF->LF (file LF-convention, lf_only=%d crlf=%d)' % (lf_only, crlf))
    else:
        W('entry tail CRLF kept (file CRLF-convention, crlf=%d lf_only=%d)' % (crlf, lf_only))
else:
    W('entry tail already normalized/unchanged: %r' % (tail[-20:],))

st = json.load(open(BM + r'\state.json', encoding='utf-8'))
old = 'r962 monitor round: no new pit law; standing laws'
new = ('r962 monitor round: one new pit law (round_reports.md mixed-encoding byte-edit law, '
       'appended to CODELY.md); standing laws')
if old in st['note']:
    st['note'] = st['note'].replace(old, new)
    json.dump(st, open(BM + r'\state.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    W('state.json note claim fixed (one new pit law)')
else:
    W('state.json note anchor absent (already fixed?) - no-op')
W('r962 codely append fix leg done')
