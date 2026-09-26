import subprocess

for P in ('state-bm-a.json', 'fleet/machines/bm-a.json'):
    raw = subprocess.run(['git', 'show', 'HEAD:' + P], capture_output=True).stdout
    lines = raw.split(b'\n')
    indents = set()
    for ln in lines[1:8]:
        if ln.strip():
            indents.add(len(ln) - len(ln.lstrip(b' ')))
    print(P, 'BOM:', raw[:3] == b'\xef\xbb\xbf', 'CRLF:', b'\r\n' in raw,
          'esc_u:', b'\\u' in raw, 'indent:', sorted(indents)[:3],
          'trailing_nl:', raw.endswith(b'\n'), 'len:', len(raw))
