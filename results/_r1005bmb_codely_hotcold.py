# -*- coding: utf-8 -*-
# r1005 bm-b CODELY.md hotcold migration (D-20260924-01 / O-20260927-0230 <=10KB hard line).
# prescan rc3 = memory-class authorized migration face (TPL s2, r983/r1047 precedent).
# Byte-level single-file fresh-read-modify-write (multi-writer law). LF endings, no BOM.
import json, os, hashlib

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
CODELY = os.path.join(ROOT, 'CODELY.md')
ARCH = os.path.join(ROOT, 'research', 'memory-archive', '202610.md')
RECEIPT = os.path.join(ROOT, 'results', '_r1005bmb_codely_hotcold_receipt.json')

raw = open(CODELY, 'rb').read()
orig_len = len(raw)
orig_sha = hashlib.sha256(raw).hexdigest()
assert raw.startswith('## Codely Structured Memories'.encode('utf-8')), 'unexpected header'
lines = raw.split(b'\n')

MOVE_PREFIXES = [
    '- \u57df\u6307\u9488\u00b7git \u57df\u9996\u62c6\u4ef6\u5bfc\u822a\u884c\uff08r369',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 \u6c60\u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 \u5f15\u64ce\u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 \u534f\u8bae\u57df\u62c6\u4ef6\uff08',
    '- \u51b7\u5c42\u6307\u9488\uff08r983 \u5408\u5e76\u00b7',
    '- \u51b7\u5c42\u6307\u9488\uff1a\u6d41\u6c34\u578b\u6761\u76ee\u6309 D-20260924-01',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 \u6570\u636e\u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 PS \u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 \u7f16\u7801\u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 spawn/tooling \u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7D-20261002-06 census/tooling \u57df\u62c6\u4ef6\uff08',
    '- \u57df\u6307\u9488\u00b7r983 bm-b mini-split \u53f2\u884c\u5408\u5e76\uff08',
    '- \u51b7\u5c42\u6307\u9488\uff08r983 bm-b \u70ed\u51b7\u6574\u7f16\u00b7',
    '- \u51b7\u5c42\u6307\u9488\uff08r1047 bm-a \u70ed\u51b7\u6574\u7f16\u00b7',
]
mp = [p.encode('utf-8') for p in MOVE_PREFIXES]

ROW_P_MERGED = ('- \u57df\u6307\u9488\u00b7pit \u65cf\u8def\u7531\u5408\u5e76\u884c\uff08r369/r373/r387/r380/r414/r415/r416/r419/r585/r983 \u8c31\u7cfb\u00b7\u539f 11 \u884c\u5168\u6587\u4e0e\u5168\u90e8\u589e\u91cf\u6ce8\u8bb0 verbatim=archive 202610.md\u300e\u70ed\u51b7\u6574\u7f16 2026-10-18 r1005 bm-b \u7a97\u6279\u300f\u8282\uff09\uff1agit \u57df\u52a8\u4f5c\uff08S0 \u96c6\u6210/push \u649e\u62d2/\u8ba9\u8def\u624b\u672f/closeout/\u5916\u79d1\u63a8\u9001/staged/\u89e3\u6790\u8f93\u51fa\uff09\u524d\u5fc5\u8bfb research/pit-git.md \u5b50\u4ef6\u65cf\uff08surgery/surgery-guard/netpath/parse/staged/resolver/resolver-rebase/resolver-rebase2/racewin\uff09+pit-git-parse/staged\uff1b\u6c60\u57df\u52a8\u4f5c\u524d\u6539\u8bfb pit-pool.md/pit-pool-edit.md/pit-pool-burn.md\uff08\u7f16\u8f91/settle/\u70e7\u5f55\u673a\u68b0/\u70b9\u706b\u95f8/\u53cc\u70e7\u63a5\u7ba1\u5404\u5c31\u4f4d\uff09\uff1b\u5f15\u64ce\u57df\u2192pit-engine.md/pit-engine-freeze.md/pit-engine-finalize.md/pit-engine-freeze-editor.md\uff1b\u534f\u8bae\u57df\u2192pit-protocol.md/pit-protocol-d19.md/pit-protocol-judge.md/pit-protocol-lane.md\uff08D-19 \u6d88\u8d39/prereg \u95f8/judged/state \u7c3f\u8bb0\u5404\u5c31\u4f4d\uff09\uff1bmachine-state/Ollama/GPU/\u4efb\u52a1\u5065\u5eb7\u5ba1\u8ba1\u2192pit-machine.md\uff1b\u5de5\u5177\u8840\u7edf\u514b\u9686/needle/\u4ee3\u9645\u6b65\u8fdb\u2192pit-lineage.md+pit-lineage-legdiff.md\uff1bselftest \u63a5\u7ebf/\u591a\u5165\u53e3\u811a\u672c/census \u5224\u51b3\u95e8/\u8f6c\u6362\u9009\u4ef6\u2192pit-tooling.md\uff1b\u6570\u636e\u9762\u677f\u505c\u6cca/\u91c7\u96c6\u5668\u6d3b\u6027\u2192pit-data.md\uff1bPS \u5faa\u73af\u5668/\u6279\u8dd1\u5668/\u96f6\u7a97\u5305\u88c5\u5668/\u6c34\u4f4d\u54c8\u5e0c\u2192pit-ps.md\uff1b\u7f16\u7801/\u5b50\u8fdb\u7a0b\u6355\u83b7/CJK \u4ef6\u624b\u672f\u2192pit-encoding.md\uff1b\u5206\u79bb spawn/\u957f\u6d3b\u70b9\u706b/croc\u2192pit-spawn.md\u3002')

ROW_R_MERGED = ('- \u51b7\u5c42\u6307\u9488\u00b7\u70ed\u51b7\u6574\u7f16\u53f2\u5408\u5e76\u884c\uff08r983/r1047/r1005 \u4e09\u6279\u8fc1\u79fb\u53f2+\u6307\u9488\u5408\u5e76 r444/r779/r800/r812 \u8c31\u7cfb\u00b7\u539f\u884c\u5168\u6587 verbatim=archive 202610.md \u5bf9\u5e94\u300e\u7a97\u6279\u300f\u8282\u00b7receipt=results/_r983bmb_codely_minisplit.json/_r1047bma_codely_hotcold_receipt.json/_r1005bmb_codely_hotcold_receipt.json\uff09\uff1a\u6d3b\u6cd5\u901f\u67e5=\u51b7\u7d22\u5f15\u63d0\u4ea4\u4e00\u5f8b\u6811\u624b\u672f\uff08r950\uff09/closeout \u53cc\u6bb5\u5f0f+fetch-\u5efa\u57fa\u5ea7+\u6811\u6740\u8f6f\u5e3d\uff08r951/r953\uff09/\u6062\u590d\u9010\u6587\u4ef6\u61d2\u53d6+tmp_pack \u6253\u635e+\u540c\u6587\u4ef6\u91cd\u8bd5\uff08r955/r959/r960\uff09/\u8f6e\u62a5\u544a binary edit\uff08r962\uff09/\u6bcf\u8f6e\u6536\u53e3\u6838\u4ee4\u4ef6+\u81ea\u4ea7 MSG origin \u5728\u4f4d\u6027\uff08r968/r974\uff09/\u6811\u624b\u672f dirs \u5168\u7956\u5148\u94fe+\u5185\u5bb9\u7ea7\u9001\u8fbe\u65ad\u8a00\uff08r982\uff09/rebase --continue \u6b7b\u5faa\u73af=quit+cherry-pick \u4fdd estate\uff08r1032\u00b7r1005 \u518d\u8bc1\uff09/\u6c34\u4f4d\u63a2\u9488\u9762 UU \u6309 ts newer-wins\uff08r1028\uff09/sparse \u6e05\u4ed3\u540e\u5168\u91cf checkout \u91cd\u7269\u5316\uff08r987\uff09/\u6c34\u4f4d\u6b65\u4e00\u5f8b d19_watermark.py update --advance \u7981\u5b57\u9762\uff08r1069\uff09/Taildrop \u53d6\u4ef6\u5fc5\u626b Downloads\uff08r1044\uff09/spawn \u5b50\u8fdb\u7a0b\u4f9d\u8d56\u8f93\u51fa\u5fc5 capture_output+relay\uff08r1045\uff09/idle fast-path \u6b7b\u9501\u89e3\u9501\u4e09\u4ef6\uff08r1046\uff09\u3002')

ROW_R1005_NEW = ('- [2026-10-18 11:2x r1005 bm-b] **\u6b7b\u7a97\u9057\u4ea7 git \u53cc\u7ebf\u62d3\u6251\u5751\uff08S0 \u7ee7\u627f\u7a97\u5b9e\u5f39\uff09**\uff1a\u88ab\u51fb\u6740 rebase \u7a97\u9057\u7559=HEAD detached\uff08\u771f\u9057\u4ea7\u7ebf\uff09+main \u505c\u9648\u65e7\u7ebf\uff08\u540c\u6d88\u606f\u91cd\u653e 81ffe58dbe \u5f62\u6001\u00b7porcelain \u4e0d\u663e\u5f62\uff09\u2014\u2014\u7ee7\u627f\u7a97\u7b2c\u4e00\u52a8\u4f5c\u5fc5 `git rev-parse main` \u6838\u62d3\u6251\uff08detached\u2260on-main\uff09\uff1br1032 \u5f8b quit+cherry-pick \u91cd\u5efa\u540e update-ref \u6307\u9488\u624b\u672f\u524d\u5fc5 reflog main \u6838\u4ed6\u7a97\u65b0\u63d0\u4ea4\uff08\u672c\u4f8b=\u9648\u65e7\u91cd\u590d\u91cd\u653e\u53ef\u5b64\u513f\u96f6\u4e22\u5931\uff09\u3002\u540c\u7a97\u518d\u8bc1\uff1apush \u6302\u6b7b 5min \u96f6\u8f93\u51fa\u2260\u9001\u8fbe\u5931\u8d25\u2014\u2014ls-remote \u63a2\u771f\u9001\u8fbe\u6001\uff08\u6302\u6b7b\u7a97\u5185\u4ed6\u673a\u53ef\u5df2\u524d\u79fb origin\u00b7\u91cd\u8bd5\u524d\u5fc5 fetch \u91cd\u6838 behind \u6570\uff09\u3002How to apply\uff1apush \u6302\u6b7b\u5904\u7f6e\u5e8f=\u67e5\u96f6\u6b8b\u7559\u8fdb\u7a0b\u2192ls-remote \u63a2\u9001\u8fbe\u2192fetch \u91cd\u6838\u2192\u91cd\u653e\u91cd\u63a8\uff0c\u7981\u76f2\u91cd\u8bd5\u3002')

ARCH_HEADER = ('## \u70ed\u51b7\u6574\u7f16 2026-10-18 r1005 bm-b \u7a97\u6279\uff08CODELY.md 21,556B>10KB \u786c\u7ebf\u00b7\u57df\u6307\u9488 4 \u884c+\u51b7\u5c42\u6307\u9488 10 \u884c verbatim \u8fc1\u51fa\u00b7D-20260924-01/D-20261002-06/O-20260927-0230 \u8303\u5f0f\u00b7prescan rc3=\u8bb0\u5fc6\u7c7b\u6388\u6743\u8fc1\u79fb\u9762 TPL \u00a72\u00b7receipt=results/_r1005bmb_codely_hotcold_receipt.json\uff09')

moved = []
out = []
p_merged_done = False
r_merged_done = False
r1005_done = False
ref_header = b'### Reference'

for ln in lines:
    hit = None
    for p in mp:
        if ln.startswith(p):
            hit = p
            break
    if hit is not None:
        moved.append(ln)
        if hit == mp[0] and not p_merged_done:
            out.append(ROW_P_MERGED.encode('utf-8'))
            p_merged_done = True
        elif hit == mp[4] and not r_merged_done:
            out.append(ROW_R_MERGED.encode('utf-8'))
            r_merged_done = True
        continue
    if ln == ref_header and not r1005_done:
        out.append(ROW_R1005_NEW.encode('utf-8'))
        out.append(b'')
        r1005_done = True
    out.append(ln)

assert len(moved) == 14, 'expected 14 moved rows, got %d' % len(moved)
new_raw = b'\n'.join(out)
new_len = len(new_raw)
assert new_len <= 10240, 'new size %d > 10KB hard line' % new_len
assert p_merged_done and r_merged_done and r1005_done

arch_raw = open(ARCH, 'rb').read()
arch_len_before = len(arch_raw)
if not arch_raw.endswith(b'\n'):
    arch_raw += b'\n'
section = ARCH_HEADER.encode('utf-8') + b'\n\n' + b'\n'.join(moved) + b'\n'
arch_new = arch_raw + section
for l in moved:
    assert l in arch_new, 'verbatim containment failed for moved row head: %r' % l[:60]

open(CODELY, 'wb').write(new_raw)
open(ARCH, 'wb').write(arch_new)

receipt = {
    'round': 1005, 'machine': 'bm-b', 'ts': '2026-10-18 11:2x +08:00',
    'law': 'O-20260927-0230 <=10KB hard line; D-20260924-01 hotcold; TPL s2 migration face (prescan rc3 memory-class authorized, r983/r1047 precedent)',
    'prescan': 'rc3 registry hit CODELY.md + archive 202610.md (memory-class authorized migration face)',
    'orig_len': orig_len, 'orig_sha256': orig_sha,
    'new_len': new_len, 'new_sha256': hashlib.sha256(new_raw).hexdigest(),
    'moved_rows': len(moved), 'moved_bytes': sum(len(l) + 1 for l in moved),
    'archive_len_before': arch_len_before, 'archive_len_after': len(arch_new),
    'moved_prefixes_heads': [l[:40].decode('utf-8', 'replace') for l in moved],
    'kept_rows': 8, 'added_rows': 3,
    'assertions': 'moved==14, new_len<=10240, verbatim containment 14/14, p/r merged rows emitted, r1005 row appended',
}
with open(RECEIPT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('OK moved=%d orig=%d new=%d (<=10240) archive %d->%d receipt=%s' % (
    len(moved), orig_len, new_len, arch_len_before, len(arch_new), os.path.basename(RECEIPT)))
