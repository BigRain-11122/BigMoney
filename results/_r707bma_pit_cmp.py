import subprocess, io
b = subprocess.run(['git', 'show', 'HEAD:research/pit-engine.md'], capture_output=True).stdout
print('HEAD size', len(b), 'endswith newline:', b.endswith(b'\n'))
print('HEAD tail:', repr(b[-120:]))
cur = io.open('research/pit-engine.md', 'rb').read()
i = cur.find(b'[2026-10-04 15:5x r682')
j = cur.find(b'[2026-10-05 02:1x r707')
print('between r682 and r707:', repr(cur[i+10:i+50]))
print('boundary bytes:', repr(cur[j-40:j+10]))
print('cur endswith newline:', cur.endswith(b'\n'))
