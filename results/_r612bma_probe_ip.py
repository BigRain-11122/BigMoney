import io

path = 'Tools/iteration_prompt.txt'
with open(path, 'rb') as f:
    raw = f.read()
print('bytes:', len(raw))
print('BOM utf16le:', raw[:2] == b'\xff\xfe', 'BOM utf8:', raw[:3] == b'\xef\xbb\xbf')
for enc in ('utf-16', 'utf-8', 'gbk'):
    try:
        t = raw.decode(enc)
        print(enc, 'decoded len', len(t), 'reland_hit=', 'reland' in t, 'law_hit=', 'S0 集成/收口 reland 环律' in t)
    except Exception as e:
        print(enc, 'fail', e)
