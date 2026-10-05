# r729 bm-b: D-06 pre-closeout re-verify (state.next (c) -- due 10-07 12:00 group closeout).
# Mechanical re-verification of the D-06 domain-split end state, reusable at the closeout window:
#   G1: 20 pit-*.md all present and <=30KB (30720B) each (r707 family target)
#   G2: all 8 split receipts present (r439/r441 bm-c + r700/r703/r705/r706/r707x2 bm-b)
#   G3: monthly memory archives present (202609.md / 202610.md -- r444 paradigm targets)
#   INFO: root CODELY.md size + >50KB watermark flag (D-20260925-01(4) trigger fact; the
#         flow-sink leg belongs to the 10-07 D-06 closeout window per state.next (c), no
#         mid-round byte surgery by design)
# Output: results/_r729bmb_d06_reverify.json (re-run at 10-07 closeout for final receipt)
import glob, json, os, re, sys, time

LIMIT = 30720  # 30KB hard target per r707
RECEIPTS = [
    'results/_r700bmb_d06_batch1_receipt.json',
    'results/_r703bmb_pit_engine_split_receipt.json',
    'results/_r705bmb_pit_pool_split_receipt.json',
    'results/_r706bmb_pit_protocol_split_receipt.json',
    'results/_r707bmb_pit_netpath_split_receipt.json',
    'results/_r707bmb_pit_surgery_split_receipt.json',
    'results/_r439bmc_pit_git_surgery_split.json',
    'results/_r441bmc_pit_git_b2_split.json',
]
ARCHIVES = ['research/memory-archive/202609.md', 'research/memory-archive/202610.md']

out = {'probe': 'D-06 pre-closeout re-verify', 'generated': time.strftime('%Y-%m-%d %H:%M:%S'),
       'machine': 'bm-b', 'gates': {}, 'pit_files': {}, 'info': {}}

# G1: pit domain files
pit_files = sorted(glob.glob('research/pit-*.md'))
out['gates']['g1_20_files'] = {'pass': len(pit_files) == 20, 'count': len(pit_files)}
all_under = True
ENTRY_RE = re.compile(r'^\s*-?\s*\[\d{4}-\d{2}-\d{2}')
for p in pit_files:
    b = os.path.getsize(p)
    with open(p, encoding='utf-8') as f:
        entries = sum(1 for line in f if ENTRY_RE.match(line))
    ok = b <= LIMIT
    all_under = all_under and ok
    out['pit_files'][os.path.basename(p)] = {'bytes': b, 'le_30kb': ok, 'entry_lines': entries}
out['gates']['g1_all_le_30kb'] = {'pass': all_under, 'max_bytes': max(
    out['pit_files'][k]['bytes'] for k in out['pit_files']) if pit_files else None}

# G2: receipts
missing = [r for r in RECEIPTS if not os.path.exists(r)]
out['gates']['g2_receipts_8'] = {'pass': not missing, 'present': len(RECEIPTS) - len(missing), 'missing': missing}

# G3: archives
missing_a = [a for a in ARCHIVES if not os.path.exists(a)]
out['gates']['g3_archives'] = {'pass': not missing_a, 'missing': missing_a}

# INFO: root CODELY.md watermark fact
cs = os.path.getsize('CODELY.md')
out['info']['codely_md_bytes'] = cs
out['info']['codely_md_over_50kb_watermark'] = cs > 51200
out['info']['note'] = ('flow-sink + potential re-anchor = 10-07 D-06 closeout window leg per state.next (c); '
                       'no mid-round byte surgery (r504 law: machines do not archive active laws for byte count)')

verdict = all(g['pass'] for g in out['gates'].values())
out['verdict'] = 'PASS' if verdict else 'FAIL'

with open('results/_r729bmb_d06_reverify.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
    f.write('\n')
print('D-06 REVERIFY:', out['verdict'])
print('  G1 20-files:', out['gates']['g1_20_files'], 'all<=30KB:', out['gates']['g1_all_le_30kb'])
print('  G2 receipts:', out['gates']['g2_receipts_8'])
print('  G3 archives:', out['gates']['g3_archives'])
print('  INFO codely_md_bytes:', cs, '(>50KB flag:', out['info']['codely_md_over_50kb_watermark'], ')')
sys.exit(0 if verdict else 1)
