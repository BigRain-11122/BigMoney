# r503 bm-c: state roundtrip failure diagnosis (r678 law -> diagnose before surgery)
import json
sp = r'K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json'
raw_bytes = open(sp, 'rb').read()
raw = raw_bytes.decode('utf-8')
crlf = raw.count('\r\n')
lf_only = raw.count('\n') - crlf
print('bytes=%d crlf=%d lf_only=%d bom=%s' % (len(raw_bytes), crlf, lf_only, raw_bytes[:3] == b'\xef\xbb\xbf'))
obj = json.loads(raw)
redump = json.dumps(obj, ensure_ascii=False, indent=1)
print('raw_len=%d redump_len=%d' % (len(raw), len(redump)))
# eol-normalized compare
redump_crlf = redump.replace('\n', '\r\n')
print('match_lf=%s match_crlf=%s' % (raw == redump, raw == redump_crlf))
if raw != redump and raw != redump_crlf:
    # first divergence
    n = min(len(raw), len(redump_crlf))
    i = 0
    while i < n and raw[i] == (redump_crlf if crlf > lf_only else redump)[i]:
        i += 1
    print('first divergence at byte %d' % i)
    print('raw   :%r' % raw[max(0,i-40):i+40])
    print('redump:%r' % ((redump_crlf if crlf > lf_only else redump)[max(0,i-40):i+40]))
# duplicate key check
def dup_keys(pairs):
    seen = {}
    for k, v in pairs:
        if k in seen:
            print('DUP KEY:', k, '->', repr(v)[:60])
        seen[k] = v
    return seen
json.loads(raw, object_pairs_hook=dup_keys)
