import json, difflib

b = open(r'state-bm-a.json', 'rb').read()
t = b.decode('utf-8', errors='replace')
d = json.loads(t)
rt2 = json.dumps(d, ensure_ascii=False, indent=1).replace('\n', '\r\n')
# try with trailing newline (original ends-nl True)
rt2n = rt2 + '\r\n'
print('rt2+nl identical:', rt2n.encode('utf-8') == b)
if rt2n.encode('utf-8') != b:
    o = t.splitlines()
    n = rt2n.splitlines()
    diff = list(difflib.unified_diff(o, n, lineterm=''))[:30]
    for line in diff:
        print(repr(line[:120]))
