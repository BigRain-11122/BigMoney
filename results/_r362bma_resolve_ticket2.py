import io, json

p = 'fleet/tasks/T-2026-09-27-94-P1.json'
src = io.open(p, 'r', encoding='utf-8', newline='').read()
i = src.find('<<<<<<<')
m = src.find('=======', i)
j = src.find('>>>>>>>', m)
assert i >= 0 and m > i and j > m
head_side = src[i + len('<<<<<<< HEAD\n'):m]
progress = (' "progress_r362": "bm-a R362 (SIDE-BRANCH, yielded to bm-b per '
            'yield_note_bm_a): parallel-blind s1+s2 executed 22:57-23:15 before '
            'push-collision discovery -- MASS_TRIAL_W1 prereg frozen c638f8cf '
            '(R99, seed mass_trial_w1 20283000) + generation engine '
            'scripts/mass_trial_w1.py (75 families/11 modules zero-invention '
            'source-sha, Sobol 512-draw frames, R/X/S/T axes, signal-hash dedup, '
            'selftest 11/11, byte-stable) + 975-candidate stage-1 screen '
            '(post-freeze 41s, 25 workers) -> 166 survivors 17.0%, null p50 '
            '0.45/p95 0.533<0.60 thin-margin, bear-gate axis 36.7% vs 9.0% none, '
            '4/6 registered bases pass at defaults, ledger 286551->287526 '
            '(+975 stays counted, invalidated-runs-still-count law), '
            'gate_attrition row, prereg sec.7/8 backfilled. ADJUDICATION FACE = '
            'lane owner bm-b (adopt-as-sub-wave-supply vs supersede, MSG-2261 '
            'precedent); bm-a shard offer for owner-frozen s2/s3 stands per '
            'MSG-2335; owner 48h CEO clock unaffected (bm-b owns)."')
tail_marker = src[j:]
tail_len = len('>>>>>>> 28d9249f (T-94 s2 DONE: stage-1 screen 975->166 survivors (17.0%, bear-gate axis 36.7% vs 9.0%, null p95 0.533<0.60 thin margin disclosed, 4/6 registered bases pass at defaults), prereg sec.7/8 backfilled one-shot, ledger +975, gate_attrition row; next = s3 per-stage freeze then judgment funnel [via bm-a])\n')
body = head_side.rstrip()
assert body.endswith('}'), repr(body[-50:])
resolved = body[:-1].rstrip() + ',' + progress + '}' + '\n'
out = src[:i] + resolved + tail_marker[tail_len:]
io.open(p, 'w', encoding='utf-8', newline='').write(out)
d = json.load(open(p, encoding='utf-8'))
print('keys ok:', [k for k in d if 'note' in k or 'progress' in k or k == 'claim_note'])
print('owner:', d['claimed_by'][:20])
