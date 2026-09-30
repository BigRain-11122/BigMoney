# r490 bm-b crash_fuse.json UU resolver (bigmoney-conflict-resolve skill, rolling-ledger union recipe r188/R208)
# Mid-rebase recovery: rebase stalled on pick a10be2398 (round 490a rider) after prior session died.
# Ours  = HEAD (82f05331b + applied picks, carries bm-a n1w2 harvest sigs, 35 sigs)
# Theirs = a10be2398 (round 490a rider, carries bm-b lowamp-nulls entry, 25 sigs)
# Recipe: both-blob union zero-loss; state fields take newest (refusals = monotonic counter -> max);
#         cleared DIFF -> newest cleared_ts; same-value tie -> HEAD (r140). Format mirror: indent=1, CRLF, no trailing NL.
import subprocess, json, sys

def blob(rev):
    return subprocess.check_output(['git', 'show', rev + ':results/crash_fuse.json'])

ours_b = blob('HEAD')
theirs_b = blob('a10be2398')
ours = json.loads(ours_b.decode('utf-8'))
theirs = json.loads(theirs_b.decode('utf-8'))

assert sorted(ours) == sorted(theirs) == ['cleared', 'sigs'], sorted(set(ours) ^ set(theirs))

resolved = {}
for section in list(ours.keys()):  # mirror HEAD top-level section order (sigs first)
    h, t = ours[section], theirs[section]
    out = {}
    # preserve producer ordering: HEAD order first, then only-THEIRS keys in their original order
    for k in list(h.keys()) + [k for k in t.keys() if k not in h]:
        if k not in h:
            out[k] = t[k]
        elif k not in t:
            out[k] = h[k]
        elif h[k] == t[k]:
            out[k] = h[k]  # identical or tie -> HEAD
        else:
            if section == 'cleared':
                # newest cleared_ts wins (both carry same old_code_sha256 here)
                out[k] = t[k] if t[k]['cleared_ts'] > h[k]['cleared_ts'] else h[k]
            else:
                # sigs: refusals is a monotonic counter -> higher = later state; equal -> HEAD (r140)
                out[k] = t[k] if t[k].get('refusals', 0) > h[k].get('refusals', 0) else h[k]
    resolved[section] = out

# zero-loss assertions (skill 三.3)
assert set(resolved['sigs']) == set(ours['sigs']) | set(theirs['sigs'])
assert set(resolved['cleared']) == set(ours['cleared']) | set(theirs['cleared'])
assert len(resolved['sigs']) == len(set(ours['sigs']) | set(theirs['sigs']))
assert len(resolved['cleared']) == len(set(ours['cleared']) | set(theirs['cleared']))

non_ascii = any(b > 127 for b in ours_b) or any(b > 127 for b in theirs_b)
s = json.dumps(resolved, ensure_ascii=not non_ascii, indent=1)
s = s.replace('\n', '\r\n')
data = s.encode('utf-8')

# validate before write (skill 三.1)
json.loads(data.decode('utf-8'))

with open('results/crash_fuse.json', 'wb') as f:
    f.write(data)

print('resolved sigs:', len(resolved['sigs']), '(ours', len(ours['sigs']), '+ theirs', len(theirs['sigs']), ')')
print('resolved cleared:', len(resolved['cleared']))
print('non_ascii:', non_ascii)
print('OK')
