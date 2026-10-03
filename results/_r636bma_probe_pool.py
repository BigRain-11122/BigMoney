import subprocess

data = open(r'results\runnable_pool.json', 'rb').read()
print('CRLF:', data.count(b'\r\n'), '| LF-total:', data.count(b'\n'), '| size:', len(data))
i = data.find(b'fund-value-p1-nulls-0of1')
seg = data[i:i + 900]
print('shard byte offset:', i)
print('owner-bm-a in shard:', b'"owner": "bm-a"' in seg)
print('18:16:08 in shard:', b'18:16:08' in seg)
print('rel-bm-a-r636 release note in shard:', b'rel-bm-a-r636' in seg)
r = subprocess.run(['git', 'diff', '--numstat', '--', 'results/runnable_pool.json'],
                   capture_output=True, text=True, encoding='utf-8', errors='replace')
print('git diff numstat:', repr(r.stdout.strip()), '| stderr:', r.stderr.strip()[:100])
