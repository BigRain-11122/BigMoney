# -*- coding: utf-8 -*-
import os, io
o = open(os.path.join(os.environ['TEMP'], 'codely_ours.md'), encoding='utf-8').read()
t = open(os.path.join(os.environ['TEMP'], 'codely_theirs.md'), encoding='utf-8').read()
ao = open(os.path.join(os.environ['TEMP'], 'arch_ours.md'), encoding='utf-8').read()
out = io.open(r'results\_r264bmc_codely_diff.txt', 'w', encoding='utf-8')
for tag, s in [('OURS-CODELY(origin bm-b r455 re-arch)', o), ('THEIRS-CODELY(mine r264)', t)]:
    out.write('===== %s =====\n' % tag)
    for l in s.splitlines():
        if l.strip().startswith('- ') or '热冷整编' in l:
            out.write(l[:160] + '\n')
    out.write('\n')
out.write('===== OURS-ARCHIVE r455 section (tail 30 lines) =====\n')
idx = ao.rfind('热冷整编 2026-09-30 r455')
if idx >= 0:
    for l in ao[idx:ao.find('\n## ', idx + 10) if ao.find('\n## ', idx + 10) > 0 else len(ao)].splitlines()[:30]:
        out.write(l[:150] + '\n')
else:
    out.write('no r455 section marker found; searching bm-b marker\n')
    for l in ao.splitlines():
        if 'r455' in l:
            out.write(l[:150] + '\n')
out.close()
print('diff written to results/_r264bmc_codely_diff.txt')
