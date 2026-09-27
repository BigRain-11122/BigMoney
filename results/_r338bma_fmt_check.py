import subprocess

def blob(ref, path):
    return subprocess.run(['git', 'show', ref + ':' + path], capture_output=True).stdout

for path in ['results/runnable_pool.json', 'fleet/tasks/T-2026-09-25-46-P1.json', 'results/gate_attrition.json']:
    b = blob('HEAD', path)
    cur = open(path, 'rb').read()
    print('==', path)
    print('  HEAD blob: %dB CRLF=%d LF=%d | indent-sample: %r' % (
        len(b), b.count(b'\r\n'), b.count(b'\n') - b.count(b'\r\n'), b[:120]))
    print('  worktree : %dB CRLF=%d LF=%d' % (
        len(cur), cur.count(b'\r\n'), cur.count(b'\n') - cur.count(b'\r\n')))
    # indentation of first nested line
    first_lines = b.split(b'\n')[:6]
    for l in first_lines[1:4]:
        print('   HEAD line:', repr(l[:60]))
