# r999 conflict resolution: union-merge append-only ledgers (CODELY.md CRLF / post_review.jsonl LF)
# 16 shared regen/probe faces resolved origin-side (HEAD) via git checkout --ours (shell side).
import subprocess, io

def stage_lines(spec):
    b = subprocess.check_output(['git', 'show', spec])
    return b.decode('utf-8', errors='replace').splitlines()

# --- post_review.jsonl : LF append-only evidence ledger -> line-set union
s2 = stage_lines(':2:results/post_review.jsonl')
s3 = stage_lines(':3:results/post_review.jsonl')
set2 = set(s2)
merged = s2 + [l for l in s3 if l not in set2]
with io.open('results/post_review.jsonl', 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(merged) + '\n' if merged else '')
print('post_review union s2=%d s3=%d merged=%d added=%d' % (len(s2), len(s3), len(merged), len(merged) - len(s2)))

# --- CODELY.md : CRLF ledger -> union, ours(HEAD)=base + stash-side unique lines appended
s2 = stage_lines(':2:CODELY.md')
s3 = stage_lines(':3:CODELY.md')
set2 = set(l.rstrip('\r') for l in s2)
extra = [l for l in s3 if l.rstrip('\r') not in set2]
merged = s2 + extra
with io.open('CODELY.md', 'w', encoding='utf-8', newline='') as f:
    if merged:
        f.write('\r\n'.join(merged) + '\r\n')
print('CODELY union s2=%d s3=%d extra=%d' % (len(s2), len(s3), len(extra)))
for l in extra:
    print('EXTRA-LINE: ' + l[:100])
