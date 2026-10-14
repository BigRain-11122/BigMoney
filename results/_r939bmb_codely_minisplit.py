# r939 bm-b CODELY main-file mini-split migration (D-20260206 authorized face, prescan rc3 memory/pit class)
# Ritual: r731/r833/r889. Zero-loss assertion: migrated bytes verbatim in target files + main retained-face identity.
import hashlib, json, sys

MAIN = 'CODELY.md'
T_REBASE2 = 'research/pit-git-resolver-rebase2.md'
T_ENCODING = 'research/pit-encoding.md'
T_JUDGE = 'research/pit-protocol-judge.md'
RECEIPT = 'results/_r939bmb_codely_minisplit.json'

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

main = open(MAIN, 'rb').read()
main_before = len(main)
lines = main.split(b'\n')
assert lines[-1] == b'', 'expected trailing empty line'

# entries at 0-based 47/48/49 (verified by ASCII substring probes)
idx933 = idx936 = idx938 = None
for i, l in enumerate(lines):
    if b'r933 bm-b git' in l and l.startswith(b'- [2026-10-14 14:1x]'):
        idx933 = i
    if b'r936 bm-b git' in l and l.startswith(b'- [2026-10-14 15:0x]'):
        idx936 = i
    if b'r938 bm-b' in l and l.startswith(b'- [2026-10-14 16:0x]'):
        idx938 = i
assert idx933 == 47 and idx936 == 48 and idx938 == 49, (idx933, idx936, idx938)
assert idx936 == idx933 + 1 and idx938 == idx936 + 1, 'entries must be consecutive tail lines'

e933, e936, e938 = lines[47], lines[48], lines[49]
migrated = [(e933, T_REBASE2), (e936, T_REBASE2), (e938, T_ENCODING)]

# new pit entry direct-write (main full => r666/r889 direct-write precedent)
new_pit = ('- [2026-10-14 16:3x] r939 bm-b prereg 回填域新坑：**回填计数误引全量 census 结构面'
           '（informative n 抄 §4 人口描述 45/128·机读实读=judged 块内 21/35）**——W19 §7 配对差分行实弹'
           '（勘误同轮落：TRIAL_LABOR_W19_PREREG.md L93·中位差/p 原值正确零改动）；律：**prereg §7/§8 回填'
           '引用的一切计数必须从机读产物件 json.load 实读，禁从冻结结构段转抄**——r938「探针走原始字节」律在'
           '「回填引用」面的姊妹面（pit-protocol-judge 域·finalize/回填动作前改读）。').encode('utf-8')

# append to targets (verbatim, line-per-line)
rebase2 = open(T_REBASE2, 'rb').read()
rebase2_before = len(rebase2)
if not rebase2.endswith(b'\n'):
    rebase2 += b'\n'
rebase2 += e933 + b'\n' + e936 + b'\n'
open(T_REBASE2, 'wb').write(rebase2)

enc = open(T_ENCODING, 'rb').read()
enc_before = len(enc)
enc += e938 + b'\n'
open(T_ENCODING, 'wb').write(enc)

judge = open(T_JUDGE, 'rb').read()
judge_before = len(judge)
assert judge.endswith(b'\n'), 'judge file must end with newline'
judge += new_pit + b'\n'
open(T_JUDGE, 'wb').write(judge)

# pointer line replaces the three entries (budget: main_after <= 30720)
pointer = ('- 域指针·r939 bm-b mini-split：r933/r936→resolver-rebase2·r938→pit-encoding·'
           '新律→pit-protocol-judge·receipt=results/_r939bmb_codely_minisplit.json').encode('utf-8')
new_main_lines = lines[:47] + [pointer] + [b'']
new_main = b'\n'.join(new_main_lines)
assert len(new_main) <= 30720, 'main over cap: %d' % len(new_main)
open(MAIN, 'wb').write(new_main)

# zero-loss verification: migrated bytes present verbatim in targets
rebase2_now = open(T_REBASE2, 'rb').read()
enc_now = open(T_ENCODING, 'rb').read()
judge_now = open(T_JUDGE, 'rb').read()
assert e933 in rebase2_now and e936 in rebase2_now and e938 in enc_now, 'verbatim-in-target FAILED'
assert new_pit in judge_now, 'new-pit verbatim-in-target FAILED'
assert len(rebase2_now) <= 30720 and len(enc_now) <= 30720 and len(judge_now) <= 30720, 'domain over cap'
main_now = open(MAIN, 'rb').read()
assert main_now == new_main, 'main write identity FAILED'

receipt = {
    'round': 'r939', 'machine': 'bm-b', 'ts': '2026-10-14T16:3x+08:00',
    'ritual': 'r731/r833/r889 precedent; D-20260206 group split-order authorized migration face',
    'prescan': 'treasure_guard prescan rc3 (memory/pit class) -- authorized face, 4 files',
    'main_before': main_before, 'main_after': len(main_now),
    'migrated_entries': [
        {'entry': 'r933 git dual-law (rebase-continue zero-UU remedy 2nd instance + PS stash@{0} quoting)',
         'bytes': len(e933), 'sha16': sha16(e933), 'target': T_REBASE2, 'verbatim_in_target': True},
        {'entry': 'r936 S0 rebase zero-UU silent tri-merge on owner faces (owner-content audit law)',
         'bytes': len(e936), 'sha16': sha16(e936), 'target': T_REBASE2, 'verbatim_in_target': True},
        {'entry': 'r938 PS-pipe hash probe corrupts CJK blob (raw-subprocess-bytes law)',
         'bytes': len(e938), 'sha16': sha16(e938), 'target': T_ENCODING, 'verbatim_in_target': True},
    ],
    'direct_write_new_pit': {
        'entry': 'r939 prereg backfill numbers must be machine-read (census-misquote face)',
        'bytes': len(new_pit), 'sha16': sha16(new_pit), 'target': T_JUDGE,
        'law': 'r666/r889 direct-write precedent (main at cap)',
    },
    'domain_sizes': {
        T_REBASE2: {'before': rebase2_before, 'after': len(rebase2_now)},
        T_ENCODING: {'before': enc_before, 'after': len(enc_now)},
        T_JUDGE: {'before': judge_before, 'after': len(judge_now)},
    },
    'zero_loss_assertion': 'migrated bytes verbatim in targets + main retained-face identity (lines 0-46 unchanged, 3 tail entries -> 1 pointer line)',
    'standing_debt_disclosed': 'research/pit-ps.md = 32,451B > 30,720B cap (pre-existing overage, not touched this window; next maintenance window sub-split per r705/r836 precedent)',
    'main_assertion': 'main %d <= 30720 PASS' % len(main_now),
}
open(RECEIPT, 'w', encoding='utf-8').write(json.dumps(receipt, ensure_ascii=False, indent=1))
print('MINI-SPLIT OK: main %d -> %d (<=30720); rebase2 %d -> %d; encoding %d -> %d; judge %d -> %d'
      % (main_before, len(main_now), rebase2_before, len(rebase2_now), enc_before, len(enc_now), judge_before, len(judge_now)))
print('receipt:', RECEIPT)
