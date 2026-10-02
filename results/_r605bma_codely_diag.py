import subprocess

def blob_bytes(ref):
    return subprocess.run(['git', 'cat-file', 'blob', ref],
                          capture_output=True).stdout

def blob_size(ref):
    r = subprocess.run(['git', 'cat-file', '-s', ref], capture_output=True,
                       text=True)
    return int(r.stdout.strip())

head_ref = subprocess.run(['git', 'rev-parse', 'HEAD'],
                          capture_output=True, text=True).stdout.strip()
print('HEAD:', head_ref)
print('HEAD CODELY size:', blob_size(f'{head_ref}:CODELY.md'.replace('HEAD:', head_ref + ':') if False else 'HEAD:CODELY.md'))
staged = subprocess.run(['git', 'show', ':CODELY.md'], capture_output=True).stdout
print('staged size:', len(staged))
head = blob_bytes('HEAD:CODELY.md')
print('HEAD size (direct):', len(head))
print('HEAD CRLF:', head.count(b'\r\n'), 'LF:', head.count(b'\n'))
print('staged CRLF:', staged.count(b'\r\n'), 'LF:', staged.count(b'\n'))
hl = {l.rstrip(b'\r\n') for l in head.split(b'\n') if l.strip()}
sl = {l.rstrip(b'\r\n') for l in staged.split(b'\n') if l.strip()}
only_head = [l for l in hl if l not in sl]
only_staged = [l for l in sl if l not in hl]
print('lines only in HEAD:', len(only_head))
print('lines only in staged:', len(only_staged))
for l in only_staged[:3]:
    print('  + ', l[:100].decode('utf-8', 'replace'))
for l in only_head[:3]:
    print('  - ', l[:100].decode('utf-8', 'replace'))
