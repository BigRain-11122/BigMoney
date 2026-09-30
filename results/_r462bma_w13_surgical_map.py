# -*- coding: utf-8 -*-
# r462 bm-a: W13 surgical conversion map facts.
# Purpose: durable hand-off so the next round can write the W13 surgeon
# (W12->W13) mechanically instead of re-reading the 2,895-line W12 surgeon
# + 262KB W12 runner from scratch (dead r462 session burned 25min on that).
# Sources (all frozen, in-tree):
#   - results/_r445bmb_w12_surgeon.py      : W11->W12 conversion recipe (sub1/subn ops)
#   - scripts/trial_labor_w12.py           : frozen W12 runner = W13 SRC
#   - results/_r456bma_sumnsump_w13_probe.py + _facts.json : SUMN gate verbatim source
#   - research/TRIAL_LABOR_W13_PREREG.md    : frozen W13 spec (r461 freeze 8bc04fd63)
#   - SEED_REGISTRY: w13 gen/scrnull/unc = 20323000/20323500/20324000 (r461 ALL GREEN)
import io, re, json, hashlib, time

OUT = 'results/_r462bma_w13_surgical_map.json'

surgeon = io.open('results/_r445bmb_w12_surgeon.py', encoding='utf-8').read()
L = surgeon.splitlines()
sections = []   # ordered (# ---- N. name, line)
ops_by_sec = {}
cur = None
for i, l in enumerate(L):
    s = l.strip()
    m = re.match(r'# -{2,4}\s*(\d+)\.\s*(.+)$', s)
    if m:
        cur = {'n': int(m.group(1)), 'name': m.group(2)[:80], 'line': i + 1, 'ops': 0}
        sections.append(cur)
    elif re.search(r'\b(sub1|subn)\(', l) and cur is not None:
        cur['ops'] += 1
n_ops = sum(s['ops'] for s in sections)
n_free = len([1 for l in L if re.search(r'\b(sub1|subn)\(', l)]) - n_ops

# W13 prereq faces: banner + sec.3 grid spec extract
prereg = io.open('research/TRIAL_LABOR_W13_PREREG.md', encoding='utf-8').read()
banner_keys = {}
for pat, key in [
    (r'evidence_cutoff[^\n]*', 'cutoff_line'),
    (r'TRIAL_LABOR_W13[^\n]*', 'title_line'),
]:
    m = re.search(pat, prereg)
    if m:
        banner_keys[key] = m.group(0)[:160]
grid_m = re.search(r'(#+\s*3[^\n]*\n(.*?\n){1,40}?)', prereg)

# r456 SUMN probe facts: key frozen numbers
facts = json.load(io.open('results/_r456bma_sumnsump_w13_probe_facts.json', encoding='utf-8'))

def flat_nums(d, prefix='', depth=0, out=None):
    if out is None:
        out = {}
    if depth > 2:
        return out
    if isinstance(d, dict):
        for k, v in d.items():
            kl = str(k).lower()
            if isinstance(v, (int, float)) and re.search(r'decid|open|sumn|slope|mirror|first|anchor|win|minp', kl):
                out[prefix + str(k)] = v
            elif isinstance(v, dict):
                flat_nums(v, prefix + str(k) + '.', depth + 1, out)
    return out

nums = flat_nums(facts)

out = {
    'ts': time.strftime('%Y-%m-%dT%H:%M:%S+08:00'),
    'round': 462, 'machine': 'bm-a', 'lane': 'trial-labor W13 runner build',
    'surgeon_recipe': {
        'file': 'results/_r445bmb_w12_surgeon.py',
        'lines': len(L),
        'sha16': hashlib.sha256(surgeon.encode('utf-8')).hexdigest()[:16],
        'total_ops': len([1 for l in L if re.search(r'\b(sub1|subn)\(', l)]),
        'sections': sections,
    },
    'w13_src_runner': {
        'file': 'scripts/trial_labor_w12.py',
        'bytes': io.open('scripts/trial_labor_w12.py', encoding='utf-8').read().__len__(),
        'note': 'frozen W12 runner; W13 surgeon SRC per W11->W12 precedent',
    },
    'w13_gate_verbatim_source': {
        'probe': 'results/_r456bma_sumnsump_w13_probe.py',
        'facts': 'results/_r456bma_sumnsump_w13_probe_facts.json',
        'frozen_anchor_numbers_seen': {k: nums[k] for k in sorted(nums)[:40]},
        'note': 'SUMN gate construction VERBATIM import from probe (zero-invention law), anchor generated programmatically from facts (zero hand-copy, r445 declare-vs-disk law)',
    },
    'w13_prereg': {
        'file': 'research/TRIAL_LABOR_W13_PREREG.md',
        'freeze_commit': '8bc04fd63 (r461)',
        'banner_lines': banner_keys,
    },
    'w13_seeds': {
        'gen': 20323000, 'scrnull': 20323500, 'unc': 20324000,
        'law': 'three-step law ALL GREEN r461 (facts results/_r461bma_w13_seed_law_facts.json)',
    },
    'build_law': [
        'r446: prep/finalize/judge-prep real-data identity-face three-command first-run BEFORE declaring runner landed',
        'r458: catalog enqueue_gates must be prereg_frozen:<path> (bare string = checker unknown-gate-ref permanent block)',
        'r459: pool entry needs workers_plan + runner_args (fail-closed gates in fill_ladder)',
        'r460: crash-fuse lock: first launch must be correctly armed via pool_worker channel if control face fails',
        'runner_exists gate at Tools/fill_ladder_catalog.json must NOT fire on partial build (Slice-B review before formal naming)',
        'W12 section map for anchors: dump probes _r462bma_{catalog,wiring,dump2}_probe.py (r462 session A, kept in-tree)',
    ],
    'next_round_moves': [
        '1. write results/_r463bma_w13_surgeon.py: adapt W12 surgeon sections with SUMN layer swap (src=trial_labor_w12.py, dst=results/_r463bma_w13_runner_draft.py)',
        '2. run surgeon -> draft + surgery report; three-command identity-face runs (prep/finalize/judge-prep on real data)',
        '3. selftest leg; Slice-B review; formal land as scripts/trial_labor_w13.py',
        '4. flip catalog runner_exists; GENERATE pool enqueue (prereg_frozen gate + workers_plan + runner_args); autofill burn; SCREEN/JUDGE waves follow',
    ],
}
io.open(OUT, 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
print('MAP WRITTEN', OUT)
print('sections:', [(s['n'], s['name'][:40], s['ops']) for s in sections])
print('total ops:', out['surgeon_recipe']['total_ops'])
print('anchor numbers seen:', len(nums), sorted(nums)[:12])
