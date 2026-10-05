# -*- coding: utf-8 -*-
"""r740 bm-a w4: CODELY.md-only UU resolve -- r706 per-section lstrip-bullet
block-union + fusion probe (r741 bm-b bloodline step-5 verbatim, standalone
form). Zero-loss asserts both sides."""
import io, subprocess, re, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def git_out(*args):
    return subprocess.run(['git'] + list(args), capture_output=True, cwd=ROOT,
                          creationflags=0x08000000)

MERGE_TIP = git_out('rev-parse', 'MERGE_HEAD').stdout.decode('utf-8').strip()
UU_LIVE = set(git_out('diff', '--name-only', '--diff-filter=U').stdout.decode('utf-8').split())
# live set may be empty (stages collapsed by errant add); authoritative face reassigned below

# stages collapsed by an errant add (r725 treadmill face); exact blob provenance:
# ours == HEAD blob, theirs == MERGE_HEAD blob (identical bytes to the lost :2:/:3:)
o_txt = git_out('show', 'HEAD:CODELY.md').stdout.decode('utf-8')
t_txt = git_out('show', 'MERGE_HEAD:CODELY.md').stdout.decode('utf-8')
assert o_txt and t_txt, 'blob sides missing'
UU = {'CODELY.md'}  # merge still in progress; authoritative conflict face per HEAD-vs-MERGE_HEAD

def split_sections(txt):
    lines = txt.splitlines()
    pre, secs, cur_title, cur = [], [], None, []
    for l in lines:
        if l.startswith('### '):
            if cur_title is not None:
                secs.append((cur_title, cur))
            cur_title = l; cur = []
        elif cur_title is None:
            pre.append(l)
        else:
            cur.append(l)
    if cur_title is not None:
        secs.append((cur_title, cur))
    return pre, secs

def split_entries(lines):
    ents, cur = [], []
    for l in lines:
        if l.lstrip().startswith('- ['):
            if cur:
                ents.append(cur)
            cur = [l]
        elif cur:
            cur.append(l)
        else:
            cur = ['<PRE>%s' % l]
    if cur:
        ents.append(cur)
    return ents

def ekey(ent):
    return ent[0].lstrip()

pre_o, secs_o = split_sections(o_txt)
pre_t, secs_t = split_sections(t_txt)
result_secs = []
receipt = {'merge_head': MERGE_TIP, 'ours_sections': [t for t, _ in secs_o],
           'theirs_sections': [t for t, _ in secs_t], 'appended': [], 'shared_diff': []}
for title, tbody in secs_t:
    o_body = None
    for t2, b2 in secs_o:
        if t2 == title:
            o_body = b2; break
    if o_body is None:
        result_secs.append((title, tbody))
        receipt['appended'].append(('theirs-only-section', title[:60]))
        continue
    t_ents = split_entries(tbody)
    o_ents = split_entries(o_body)
    t_keys = {}
    for e in t_ents:
        k = ekey(e)
        assert k not in t_keys, 'dup key theirs %s' % k[:60]
        t_keys[k] = e
    out_ents = list(t_ents)
    for e in o_ents:
        k = ekey(e)
        if k.startswith('<PRE>'):
            continue
        if k in t_keys:
            if e != t_keys[k]:
                keep, drop = (e, t_keys[k]) if len('\n'.join(e)) >= len('\n'.join(t_keys[k])) else (t_keys[k], e)
                receipt['shared_diff'].append({'key': k[:80], 'kept': 'ours' if keep is e else 'theirs',
                                               'ours_len': len('\n'.join(e)), 'theirs_len': len('\n'.join(t_keys[k]))})
                if keep is e:
                    idx = out_ents.index(t_keys[k])
                    out_ents[idx] = e
            continue
        out_ents.append(e)
        receipt['appended'].append(('ours-entry', k[:80]))
    body_lines = []
    for e in out_ents:
        for l in e:
            body_lines.append(l[5:] if l.startswith('<PRE>') else l)
    result_secs.append((title, body_lines))
for title, body in secs_o:
    if title not in {t for t, _ in secs_t}:
        result_secs.append((title, body))
        receipt['appended'].append(('ours-only-section', title[:60]))
out_txt = '\n'.join(pre_t if pre_t else pre_o) + '\n'
for title, body in result_secs:
    out_txt += '\n' + title + '\n'
    if body:
        out_txt += '\n'.join(body) + '\n'

# zero-loss asserts (r706 fusion probe both sides)
res_keys = set()
_, res_secs_final = split_sections(out_txt)
for title, body in res_secs_final:
    for e in split_entries(body):
        k = ekey(e)
        if not k.startswith('<PRE>'):
            res_keys.add(k)
for src, nm in ((secs_o, 'ours'), (secs_t, 'theirs')):
    for title, body in src:
        for e in split_entries(body):
            k = ekey(e)
            if not k.startswith('<PRE>'):
                assert k in res_keys, 'CODELY zero-loss violated (%s): %s' % (nm, k[:60])

open(os.path.join(ROOT, 'CODELY.md'), 'wb').write(out_txt.encode('utf-8'))
raw = open(os.path.join(ROOT, 'CODELY.md'), 'rb').read()
assert not re.search(rb'(^|\n)<{7} ', raw), 'marker left'
assert not re.search(rb'(^|\n)>{7}( |$)', raw), 'marker left'
json.dump(receipt, open(os.path.join(ROOT, 'results', '_r740bma_codely_union.w4.json'), 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('CODELY block-union: appended=%d shared_diff=%d res_keys=%d' % (
    len(receipt['appended']), len(receipt['shared_diff']), len(res_keys)))
for a in receipt['appended']:
    print('  +', a[0], a[1])
