# -*- coding: utf-8 -*-
"""POOL-0003 whisper 词级锚点复核批 (bm-a, r1024) — deterministic review, zero network, zero LLM.
Spec: cph4/fleet/mv-album-001-jay/anchors/ | Baseline: mv0001_full_words.json (reuse law)
Sources: anchor JSONs read from GROUP origin blobs (zero-tree-touch);
         song catalog from local audio/ dir (41 songs, big files not in git).
Output: results/_r1024bma_pool0003_anchor_review.json
"""
import subprocess, json, io, os, sys, datetime

G = r'C:\Users\sjs20\Desktop\FluxGroup'
ANCH_DIR = 'cph4/fleet/mv-album-001-jay/anchors/'
AUDIO_DIR = os.path.join(G, 'cph4', 'fleet', 'mv-album-001-jay', 'audio')
BASELINE = r'C:\Users\sjs20\Desktop\FluxGroup\.codely-cli\scratch\mv-carve-bma\mv0001_full_words.json'
OUT = r'results\_r1024bma_pool0003_anchor_review.json'

def gshow(path):
    r = subprocess.run(['git', '-C', G, 'show', 'origin/main:' + path], capture_output=True)
    if r.returncode != 0:
        return None
    return r.stdout.decode('utf-8', errors='replace')

def glist(path):
    r = subprocess.run(['git', '-C', G, 'ls-tree', '--name-only', 'origin/main', path],
                       capture_output=True)
    return [l for l in r.stdout.decode('utf-8', errors='replace').splitlines() if l.strip()]

now = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
receipt = {
    'card': 'POOL-0003', 'machine': 'bm-a', 'round': 1024,
    'review_type': 'whisper 词级锚点复核批 (pre-assembly CPU review)',
    'spec': ANCH_DIR, 'baseline': 'mv0001_full_words.json',
    'provenance_order': 'O-20261015-2312 (night production list; card seed 2026-10-12)',
    'ts': now,
    'songs': [], 'coverage': {}, 'checks': {}, 'verdict': None,
}

# 0) baseline schema fingerprint
with io.open(BASELINE, encoding='utf-8') as f:
    base = json.load(f)
bw = base.get('words', [])
receipt['checks']['baseline_schema'] = {
    'top_keys': sorted(base.keys()),
    'word_entry_keys': sorted(bw[0].keys()) if bw else [],
    'n_words': len(bw),
    'zero_duration_words_legal': any(w.get('t0') == w.get('t1') for w in bw),
}

# 1) catalog from audio dir (41 songs; exclude mv001 demo source file)
cat = []
for fn in sorted(os.listdir(AUDIO_DIR)):
    if not fn.lower().endswith(('.mp3', '.flac', '.wav')):
        continue
    name = fn
    for ext in ('.mp3', '.flac', '.wav'):
        if name.lower().endswith(ext):
            name = name[: -len(ext)]
    if name.startswith('mv001_source'):
        continue
    name = name.replace('周杰伦 - ', '').strip()
    cat.append(name)
receipt['checks']['catalog_size'] = len(cat)
receipt['checks']['catalog'] = cat

# 2) anchors inventory at origin
files = glist(ANCH_DIR)
jsons = sorted([f.split('/')[-1] for f in files if f.endswith('.json')])
txts = set(f.split('/')[-1][:-4] + '.txt' for f in files if f.endswith('.txt'))

def load_blob(fn):
    t = gshow(ANCH_DIR + fn)
    if t is None:
        return None, 'blob missing at origin'
    try:
        return json.loads(t), None
    except Exception as e:
        return None, 'json parse fail: %s' % e

def song_of(fn):
    return fn[:-5]  # strip .json

songs_report = {}
for fn in jsons:
    song = song_of(fn)
    cal = song.endswith('-calibrated')
    base_song = song[:-len('-calibrated')] if cal else song
    d, err = load_blob(fn)
    rep = {'file': fn, 'calibrated_variant': cal, 'base_song': base_song}
    if err:
        rep['verdict'] = 'FAIL'
        rep['errors'] = [err]
    elif isinstance(d, dict) and isinstance(d.get('words'), list) and d.get('words'):
        # Format A: baseline-compatible word-level (words[].w/t0/t1), zero-duration words legal
        rep['schema_family'] = 'A(word-level, baseline mv0001_full_words.json)'
        rep['top_keys'] = sorted(d.keys())
        words = d['words']
        errs = []
        n = len(words)
        mono_bad = 0; t01_bad = 0; nonnum = 0
        prev_t0 = None
        for w in words:
            t0, t1, wt = w.get('t0'), w.get('t1'), w.get('w')
            if not isinstance(t0, (int, float)) or not isinstance(t1, (int, float)) or not isinstance(wt, str):
                nonnum += 1
                continue
            if t0 > t1:
                t01_bad += 1
            if prev_t0 is not None and t0 < prev_t0:
                mono_bad += 1
            prev_t0 = t0 if prev_t0 is None else max(prev_t0, t0)
        side = fn[:-5] + '.txt'
        rep['sidecar_txt'] = side if side in txts else None
        side_chars = None
        if side in txts:
            t = gshow(ANCH_DIR + side)
            side_chars = len(t.strip()) if t else 0
        rep['n_words'] = n
        rep['n_nonnumeric'] = nonnum
        rep['n_t0_gt_t1'] = t01_bad
        rep['n_monotonic_violations'] = mono_bad
        rep['sidecar_chars'] = side_chars
        rep['duration_span'] = None
        if words and all(isinstance(w.get('t0'), (int, float)) for w in words):
            rep['duration_span'] = round(max(w.get('t1', w.get('t0', 0)) for w in words), 2)
        rep['verdict'] = 'PASS' if not errs and nonnum == 0 and t01_bad == 0 and mono_bad == 0 else ('FAIL' if errs else 'WARN')
        rep['errors'] = errs or None
        if nonnum or t01_bad or mono_bad:
            rep['verdict_note'] = 'quality counters nonzero (see fields)'
        if cal:
            bfn = base_song + '.json'
            bd, berr = load_blob(bfn)
            if bd is None:
                rep['calibrated_vs_base'] = 'base json missing (%s)' % bfn
            else:
                bw2 = [w.get('w') for w in bd.get('words', [])]
                cw = [w.get('w') for w in words]
                rep['calibrated_vs_base'] = {
                    'word_seq_identical': bw2 == cw,
                    'base_n_words': len(bw2), 'cal_n_words': len(cw),
                }
    elif isinstance(d, list) and d and all(isinstance(e, dict) and 'text' in e and
            (('start' in e and 'end' in e) or ('t0' in e and 't1' in e)) for e in d):
        # Format B/C: LINE-level segments, raw whisper (start/end/text) or calibrated (t0/t1/text/approx)
        k0, k1 = ('start', 'end') if 'start' in d[0] else ('t0', 't1')
        rep['schema_family'] = ('B(line-level raw whisper, %s/%s/text)' % (k0, k1)
                                if k0 == 'start' else
                                'C(line-level calibrated, t0/t1/text/approx — lyric_calibration.py chain)')
        rep['n_approx_true'] = sum(1 for e in d if e.get('approx') is True)
        mono_bad = 0; se_bad = 0; nonnum = 0
        prev = None
        for e in d:
            s0, s1 = e.get(k0), e.get(k1)
            if not isinstance(s0, (int, float)) or not isinstance(s1, (int, float)):
                nonnum += 1
                continue
            if s0 > s1:
                se_bad += 1
            if prev is not None and s0 < prev:
                mono_bad += 1
            prev = s0 if prev is None else max(prev, s0)
        side = fn[:-5] + '.txt'
        rep['sidecar_txt'] = side if side in txts else None
        side_chars = None
        if side in txts:
            t = gshow(ANCH_DIR + side)
            side_chars = len(t.strip()) if t else 0
        rep['n_lines'] = len(d)
        rep['n_nonnumeric'] = nonnum
        rep['n_start_gt_end'] = se_bad
        rep['n_monotonic_violations'] = mono_bad
        rep['sidecar_chars'] = side_chars
        rep['duration_span'] = round(max(e.get(k1, 0) for e in d), 2) if d else None
        # informational classification, not a data corruption FAIL:
        # line-level granularity does not meet the word-level assembly contract (card title)
        # and line texts are raw whisper transcripts (mis-hear risk) — supersede pending POOL-0018
        rep['verdict'] = 'LINE_LEVEL_NOT_WORD_LEVEL'
        rep['verdict_note'] = ('structurally clean line-level segments; word-level upgrade pending '
                               'POOL-0018 (bm-b whisperX word/start/end, lyric_calibration.py chain)')
        if nonnum or se_bad or mono_bad:
            rep['verdict_note'] += ' | quality counters nonzero (see fields)'
    else:
        rep['verdict'] = 'FAIL'
        rep['errors'] = ['unknown schema: neither baseline words[] dict nor line-level start/end/text list']
    songs_report[fn] = rep
receipt['songs'] = [songs_report[f] for f in sorted(songs_report)]

# 3) coverage vs catalog
have = set()
for fn in jsons:
    s = song_of(fn)
    have.add(s[:-len('-calibrated')] if s.endswith('-calibrated') else s)
have_base_only = set()
for fn in jsons:
    s = song_of(fn)
    if not s.endswith('-calibrated'):
        have_base_only.add(s)
missing = [s for s in cat if s not in have]
extra = sorted(have - set(cat))
receipt['coverage'] = {
    'catalog_size': len(cat),
    'anchored_songs': len(have),
    'base_json_songs': sorted(have_base_only),
    'missing_from_anchors': missing,
    'anchor_without_catalog_entry': extra,
    'pending_generation_note': 'missing songs pending POOL-0018 (bm-b whisperX, O-20261015-1741) rolling output',
}
n_pass = sum(1 for r in receipt['songs'] if r['verdict'] == 'PASS')
n_fail = sum(1 for r in receipt['songs'] if r['verdict'] == 'FAIL')
n_warn = sum(1 for r in receipt['songs'] if r['verdict'] == 'WARN')
n_line = sum(1 for r in receipt['songs'] if r['verdict'] == 'LINE_LEVEL_NOT_WORD_LEVEL')
word_level_songs = sorted({r['base_song'] for r in receipt['songs']
                           if r.get('schema_family', '').startswith('A') and not r['calibrated_variant']})
receipt['summary'] = {
    'json_files_reviewed': len(receipt['songs']),
    'pass_word_level': n_pass, 'line_level_flagged': n_line, 'warn': n_warn, 'fail': n_fail,
    'word_level_assembly_ready_songs': word_level_songs,
    'catalog_coverage_pct': round(100.0 * len(have & set(cat)) / max(1, len(cat)), 1),
}
receipt['coverage']['word_level_ready_songs'] = word_level_songs
receipt['coverage']['line_level_only_songs'] = sorted({r['base_song'] for r in receipt['songs']
    if r.get('schema_family', '').startswith('B')} - set(word_level_songs))
receipt['coverage']['pinyin_base_note'] = ('anjing/jiandanan/kaibuliaokou = 安静/简单爱/开不了口 '
                                           '(pinyin-named base files, line-level)')
receipt['verdict'] = 'PASS_WITH_PENDING' if n_fail == 0 else 'FAIL'
receipt['next_action'] = ('bm-b POOL-0018 rolling generation for %d missing songs; '
                          'bm-a re-review on next receipt window; audio 代投 first-batch check in-flight') % len(missing)

with io.open(OUT, 'w', encoding='utf-8') as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print('receipt written:', OUT)
print('json reviewed=%d pass=%d warn=%d fail=%d | catalog=%d anchored=%d missing=%d' % (
    len(receipt['songs']), n_pass, n_warn, n_fail, len(cat), len(have), len(missing)))
print('verdict:', receipt['verdict'])
