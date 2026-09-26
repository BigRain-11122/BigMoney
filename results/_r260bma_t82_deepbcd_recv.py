# T-82 deep-bcd receiver leg (bm-a R260): blob byte self-verify + local re-run comparison
# Channel law R255: subprocess capture of git show raw bytes, NO PS redirection.
# EOL face law R257/R258: dB/dC raw-CRLF compare raw; dD LF-only compare LF-normalized.
import json, hashlib, subprocess, os, shutil

BRANCH = 'origin/transfer/t80-deep-bcd-basis'
PREFIX = 'results/t54/'
SENDER = 'fleet/transfers/T-2026-09-26-82-deepbcd-sender.json'
STAGE = os.path.join(os.environ['TEMP'], 't82deep-recv')
ARCHIVE = 'results/_r260bma_t82_deepbcd_compare'
FILES = [
    'cells_deep_base_dB.jsonl', 'cells_deep_base_dC.jsonl', 'cells_deep_base_dD.jsonl',
    'cells_deep_x2_dB.jsonl', 'cells_deep_x2_dC.jsonl', 'cells_deep_x2_dD.jsonl',
]

with open(SENDER, encoding='utf-8-sig') as fh:
    sender = json.load(fh)
decl = {e['file']: e for e in sender['files']}

os.makedirs(STAGE, exist_ok=True)
os.makedirs(ARCHIVE, exist_ok=True)

def sha(b):
    return hashlib.sha256(b).hexdigest()

def line_multiset(b):
    # bytes -> sorted list of line-bytes (strip trailing newline variants by splitting on b'\n', drop trailing empty)
    lines = b.split(b'\n')
    if lines and lines[-1] == b'':
        lines = lines[:-1]
    return sorted(lines)

report = {'blob_verify': {}, 'local_compare': {}, 'verdicts': {}}
all_blob_match = True
all_multiset_identical = True

for name in FILES:
    # 1) blob bytes via git show (raw, subprocess capture)
    r = subprocess.run(['git', 'show', f'{BRANCH}:{PREFIX}{name}'], capture_output=True)
    if r.returncode != 0:
        raise SystemExit(f'git show failed for {name}: {r.stderr[:200]}')
    blob = r.stdout
    e = decl[name]
    blob_sha = sha(blob)
    m = (blob_sha == e['sha256']) and (len(blob) == e['bytes'])
    all_blob_match &= m
    report['blob_verify'][name] = {
        'blob_sha256': blob_sha, 'declared_sha256': e['sha256'],
        'blob_bytes': len(blob), 'declared_bytes': e['bytes'], 'match': m,
    }
    # stage channel-face payload
    with open(os.path.join(STAGE, name), 'wb') as fh:
        fh.write(blob)

    # 2) local re-run copy comparison
    lp = PREFIX + name
    with open(lp, 'rb') as fh:
        loc = fh.read()
    crlf_b = blob.count(b'\r\n'); lf_b = len(blob.split(b'\n')) - 1
    crlf_l = loc.count(b'\r\n'); lf_l = len(loc.split(b'\n')) - 1
    raw_same = sha(loc) == blob_sha
    blob_lfn = blob.replace(b'\r\n', b'\n')
    loc_lfn = loc.replace(b'\r\n', b'\n')
    lfn_same = sha(loc_lfn) == sha(blob_lfn)
    ms_blob = line_multiset(blob_lfn)
    ms_loc = line_multiset(loc_lfn)
    multiset_identical = ms_blob == ms_loc
    # byte-identity after EOL face alignment = strongest form
    face_aligned_identical = lfn_same
    all_multiset_identical &= multiset_identical
    report['local_compare'][name] = {
        'local_bytes': len(loc), 'local_lines': lf_l, 'blob_lines': lf_b,
        'local_eol': ('CRLF' if crlf_l == lf_l else ('LF-only' if crlf_l == 0 else 'MIXED')),
        'blob_eol': ('CRLF' if crlf_b == lf_b else ('LF-only' if crlf_b == 0 else 'MIXED')),
        'raw_sha_equal': raw_same, 'lf_normalized_sha_equal': lfn_same,
        'row_multiset_identical': multiset_identical,
        'line_order_permutation': (multiset_identical and not lfn_same),
    }
    if name.startswith('cells_deep'):
        v = ('BYTE_IDENTICAL_RAW' if raw_same else
             ('BYTE_IDENTICAL_LF_NORMALIZED' if lfn_same else
              ('ROW_MULTISET_IDENTICAL_LINE_PERMUTATION' if multiset_identical else 'DIVERGENT')))
    report['verdicts'][name] = v
    # 3) archive local copy before landing (R254 evidence-only paradigm)
    shutil.copyfile(lp, os.path.join(ARCHIVE, 'mine_' + name))

report['blob_verify_all_match'] = all_blob_match
report['all_row_multiset_identical'] = all_multiset_identical
report['family_cross_check'] = '4/4 deep-shard family COMPLETE' if all_blob_match and all_multiset_identical else 'INCOMPLETE/DIVERGENT'
with open(os.path.join(ARCHIVE, 'verdict.json'), 'w', encoding='utf-8') as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)
print(json.dumps({'blob_verify_all_match': all_blob_match,
                  'all_row_multiset_identical': all_multiset_identical,
                  'verdicts': report['verdicts'],
                  'local_compare': report['local_compare']}, indent=1))
