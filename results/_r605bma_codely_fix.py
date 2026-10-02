import subprocess

# 1. HEAD blob bytes (mixed endings incumbent)
head = subprocess.run(['git', 'cat-file', 'blob', 'HEAD:CODELY.md'],
                      capture_output=True).stdout
assert head.endswith(b'\n') and not head.endswith(b'\r\n'), \
    f'unexpected tail: {head[-8:]!r}'

# 2. my r605 line = last line of the current (all-CRLF) worktree file
cur = open('CODELY.md', 'rb').read()
last_line = cur.rstrip(b'\r\n').split(b'\r\n')[-1]
assert last_line.startswith(b'- [2026-10-03 03:4x r605 bm-a]'), \
    'worktree last line is not the r605 entry: ' + repr(last_line[:60])

# 3. surgical append on the HEAD-verbatim base (LF ending, dominant style)
new = head + last_line + b'\n'
open('CODELY.md', 'wb').write(new)
print('worktree rewritten: HEAD bytes', len(head), '-> new', len(new),
      '(+1 line,', len(last_line), 'bytes)')

# 4. stage verbatim (CRLF-in-blob immunity = no clean-filter conversion)
subprocess.run(['git', 'restore', '--staged', 'CODELY.md'], check=True)
subprocess.run(['git', 'add', 'CODELY.md'], check=True)
r = subprocess.run(['git', 'diff', '--cached', '--numstat', '--', 'CODELY.md'],
                  capture_output=True, text=True, encoding='utf-8')
print('numstat after surgical fix:', r.stdout.strip())
staged = subprocess.run(['git', 'show', ':CODELY.md'],
                        capture_output=True).stdout
print('staged bytes:', len(staged), '| CRLF:', staged.count(b'\r\n'),
      '| LF:', staged.count(b'\n'))
assert staged == new, 'staged != worktree bytes'
print('OK: staged == HEAD blob + one appended LF line (zero ending churn)')
