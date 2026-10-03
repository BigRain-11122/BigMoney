import json
import subprocess

# 1) pool faces: verify divlowvol released
for fp in (r'results\runnable_pool.json', r'results\runnable_pool.bm-a.json',
           r'results\runnable_pool.bm-b.json', r'results\runnable_pool.bm-c.json'):
    data = open(fp, 'rb').read()
    i = data.find(b'"key": "fund-divlowvol-p1-nulls-0of1"')
    if i < 0:
        print(fp, ': no shard')
        continue
    eol = b'\r\n' if data.count(b'\r\n') * 2 > data.count(b'\n') else b'\n'
    end = data.find(b'}' + eol, i)
    block = data[i:end]
    claimed = b'"owner": "bm-a"' in block and b'18:38:09' in block
    released = b'rel-bm-a-r636' in block
    r = subprocess.run(['git', 'diff', '--numstat', '--', fp], capture_output=True,
                       text=True, encoding='utf-8', errors='replace')
    print(fp, '| claimed:', claimed, '| release-note:', released, '| numstat:', r.stdout.strip() or '(clean)')

# 2) value pool shard: confirm released state in worktree+HEAD
data = open(r'results\runnable_pool.json', 'rb').read()
i = data.find(b'"key": "fund-value-p1-nulls-0of1"')
eol = b'\r\n'
end = data.find(b'}' + eol, i)
print('shared value shard: owner-bm-a:', b'"owner": "bm-a"' in data[i:end],
      '| r636 note:', b'rel-bm-a-r636' in data[i:end])
