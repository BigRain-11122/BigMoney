"""ST-008 canon voice-bank entries driver (drama voice lane, bm-b host).

Purpose: admit 1-3 role-aligned reference clips per canon character into
content/drama/voice_bank/manifest.json, sourced from in-house r998 drama
audition artifacts (zero license risk, per-line text machine-readable from
MANIFEST-r998.json), each character passing the 音色一致检 v0.1 deterministic
proxy gate (cross-clip F0 / RMS / spectral-centroid consistency -- the
anchor-cleaning discipline voice face per the ST-006 manifest gate spec).

Selection law (deterministic): AUDITION-r999 hard/soft/pacing flags zero-hit
+ single-speaker field (no multiplicity marker) + ok=true + 1.5-10s window,
sorted by |audio_s - 3.5s| sweet-spot distance. Honest corpus facts (frozen
r999 artifact): BOY has zero r998 material in EP001-003; MANCANG has zero
CLEAN material (all 7 满仓 lines carry hard CLIPPED flags) -- both stay
awaiting-ref-clips. Shared-base-voice debt disclosed: XIONG/XIONGWEI/FATHER
all synthesized from the voice_07 base in r998 (F0 near-identical by
construction); MANCANG (when sourced) shares the voice_05 narrator base --
per-character differentiation = param/finetune station, not this one.

Commands: run / status / selftest
Status face: results/drama_env/voice_bank_entries.json (in-repo)
Products:   content/drama/voice_bank/manifest.json ref_clips admitted (in-repo)
             content/drama/outbox/VOICE-BANK-ENTRIES-v0.1.md (receipt)
Laws: U060 no-window; CPU lane (VOICE-PIPELINE-SKELETON-v1 sec.6); cloud
forbidden (429 economy); idempotent ensure-done; 人物一致性律 voice face.
"""
import datetime
import io
import json
import os
import sys
import time

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GRP = r'C:\Fluxgroup\FluxGroup'
REFSRC = os.path.join(GRP, 'media', 'drama-tts-out', 'r998_ep001_003')
MANIFEST_R998 = os.path.join(REFSRC, 'MANIFEST-r998.json')
AUDITION_R999 = os.path.join(REFSRC, 'AUDITION-r999.json')
VB_MANIFEST = os.path.join(ROOT, 'content', 'drama', 'voice_bank', 'manifest.json')
OUTBOX = os.path.join(ROOT, 'content', 'drama', 'outbox')
RECEIPT = os.path.join(OUTBOX, 'VOICE-BANK-ENTRIES-v0.1.md')
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'voice_bank_entries.json')

# canon id -> r998 voice-cast key (the 'cast' field of MANIFEST-r998 lines is
# the authoritative voice actually rendered; speaker field adds the
# single-speaker filter). None = no in-house material in EP001-003.
ROLE_MAP = {
    'CH':       {'cast': '长->protagonist',    'speaker': '长'},
    'XIONG':    {'cast': '熊->villain',        'speaker': '熊'},
    'XIONGWEI': {'cast': '熊伟->villain-son',  'speaker': '熊伟'},
    'MANCANG':  {'cast': '满仓->comic happy6', 'speaker': '满仓'},
    'RED':      {'cast': '红利->reporter female', 'speaker': '红利'},
    'FATHER':   {'cast': '父->father',         'speaker': '父'},
    'BOY':      None,
}
MAX_CLIPS = 3
SWEET_S = 3.5
DUR_MIN, DUR_MAX = 1.5, 10.0
# 音色一致检 v0.1 deterministic proxy tolerances (cross-clip, per character)
F0_REL_TOL = 0.15
RMS_SPREAD_DB = 8.0
CENTROID_REL_TOL = 0.20


def now_iso():
    return datetime.datetime.now().isoformat(timespec='seconds')


def say(msg):
    line = '%s %s' % (now_iso(), msg)
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        try:
            print(line.encode('gbk', errors='replace').decode('gbk'), flush=True)
        except Exception:
            pass


def rd_json(p, default):
    try:
        with io.open(p, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception:
        return default


def wr_json(p, obj):
    tmp = p + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, p)


def wr_status(patch):
    st = rd_json(STATUS, {'schema': 'voice-bank-entries-v1', 'state': 'init'})
    st.update(patch)
    st['updated_at'] = now_iso()
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    wr_json(STATUS, st)
    return st


def flagged_names():
    aud = rd_json(AUDITION_R999, {})
    flagged = set()
    for k in ('hard_flags', 'soft_flags', 'pacing_flags'):
        for fl in (aud.get(k) or []):
            flagged.add(str(fl).split()[0])
    return flagged


def candidates(cid, lines, flagged):
    """Deterministic candidate list for a canon character (best-first)."""
    role = ROLE_MAP.get(cid)
    if role is None:
        return []
    out = []
    for ln in lines:
        if not ln.get('ok'):
            continue
        if ln.get('cast') != role['cast']:
            continue
        if ln.get('speaker') != role['speaker']:
            continue  # multi-speaker line -> text/voice alignment not clean
        if ln['name'] in flagged:
            continue
        dur = float(ln.get('audio_s', 0))
        if not (DUR_MIN <= dur <= DUR_MAX):
            continue
        if not os.path.exists(ln.get('file', '')):
            continue
        out.append(ln)
    out.sort(key=lambda ln: (abs(float(ln['audio_s']) - SWEET_S), ln['ep'], ln['n']))
    return out[:MAX_CLIPS]


def read_wav_mono(path):
    """(sr, float64 mono) via stdlib wave; soundfile fallback for exotic fmt."""
    try:
        import wave
        with wave.open(path, 'rb') as w:
            sr = w.getframerate()
            nch = w.getnchannels()
            sw = w.getsampwidth()
            raw = w.readframes(w.getnframes())
        if sw == 2:
            x = np.frombuffer(raw, dtype='<i2').astype('float64') / 32768.0
        elif sw == 4:
            x = np.frombuffer(raw, dtype='<i4').astype('float64') / 2147483648.0
        else:
            raise ValueError('sampwidth %d unsupported' % sw)
        if nch > 1:
            x = x.reshape(-1, nch).mean(axis=1)
        return sr, x
    except Exception:
        import soundfile as sf
        d, sr = sf.read(path, dtype='float64', always_2d=True)
        return sr, d.mean(axis=1)


def f0_centroid_stats(x, sr):
    """Frame-wise F0 (normalized-autocorr peak, voiced frames only) + spectral
    centroid median. Returns (f0_median_hz|None, centroid_hz|None, n_voiced)."""
    fr, hop = 1024, 512
    if len(x) < fr * 2:
        return None, None, 0
    lag_min = max(2, int(sr / 400.0))
    lag_max = min(fr - 2, int(sr / 60.0))
    if lag_max <= lag_min:
        return None, None, 0
    win = np.hanning(fr)
    f0s, cents = [], []
    for i in range(0, len(x) - fr + 1, hop):
        seg = x[i:i + fr]
        w = seg * win
        e = float(np.sqrt(np.mean(w ** 2)))
        if e < 1e-3:  # silence frame
            continue
        ac = np.correlate(w, w, 'full')[fr - 1:]
        if ac[0] <= 0:
            continue
        ac = ac / ac[0]
        band = ac[lag_min:lag_max + 1]
        j = int(np.argmax(band)) + lag_min
        if band[j - lag_min] > 0.30:  # voiced + periodic enough
            f0s.append(sr / float(j))
            mag = np.abs(np.fft.rfft(w))
            freqs = np.fft.rfftfreq(fr, 1.0 / sr)
            tot = float(np.sum(mag))
            if tot > 1e-12:
                cents.append(float(np.sum(freqs * mag) / tot))
    if len(f0s) < 5:
        return None, None, len(f0s)
    return float(np.median(f0s)), float(np.median(cents)), len(f0s)


def clip_metrics(path):
    """Per-clip deterministic metrics; None f0 = analysis-reject."""
    sr, x = read_wav_mono(path)
    dur = len(x) / float(sr)
    rms = float(np.sqrt(np.mean(x ** 2)))
    rms_dbfs = float(20.0 * np.log10(rms + 1e-12))
    f0, cent, n_voiced = f0_centroid_stats(x, sr)
    return {'sr': sr, 'dur_s': round(dur, 3), 'rms_dbfs': round(rms_dbfs, 2),
            'f0_hz': (round(f0, 1) if f0 else None),
            'centroid_hz': (round(cent, 1) if cent else None),
            'n_voiced_frames': n_voiced}


def consistency_gate(mets):
    """音色一致检 v0.1 (deterministic proxy). >=2 clips: cross-clip F0/RMS/
    centroid consistency; 1 clip: vacuous single-clip pass (honest label)."""
    if len(mets) == 1:
        return 'pass-single-clip-vacuous', {}
    f0s = [m['f0_hz'] for m in mets if m.get('f0_hz')]
    cents = [m['centroid_hz'] for m in mets if m.get('centroid_hz')]
    rms = [m['rms_dbfs'] for m in mets]
    if not f0s or not cents or len(f0s) != len(mets):
        return 'REJECT-analysis-gap', {}
    mean_f0 = sum(f0s) / len(f0s)
    f0_dev = max(abs(f - mean_f0) for f in f0s) / mean_f0
    rms_spread = max(rms) - min(rms)
    mean_c = sum(cents) / len(cents)
    c_dev = max(abs(c - mean_c) for c in cents) / mean_c
    ok = (f0_dev <= F0_REL_TOL) and (rms_spread <= RMS_SPREAD_DB) and (c_dev <= CENTROID_REL_TOL)
    detail = {'f0_dev_max': round(f0_dev, 4), 'rms_spread_db': round(rms_spread, 2),
              'centroid_dev_max': round(c_dev, 4)}
    return ('pass' if ok else 'REJECT'), detail


def do_run():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    # idempotency gate: done + admitted>=1 -> early exit
    st = rd_json(STATUS, {})
    if st.get('state') == 'done' and int(st.get('admitted_n', 0)) >= 1:
        say('voice-bank entries already done (idempotent early exit)')
        return 0
    man998 = rd_json(MANIFEST_R998, None)
    vb = rd_json(VB_MANIFEST, None)
    if man998 is None or vb is None:
        say('source manifest or voice-bank manifest unreadable')
        wr_status({'state': 'failed', 'err': 'manifest-unreadable'})
        return 1
    lines = man998.get('lines', [])
    flagged = flagged_names()
    say('r998 corpus: %d lines, %d audition-flagged names' % (len(lines), len(flagged)))
    t0 = time.time()
    per_char, admitted, single, no_mat = {}, [], [], []
    for entry in vb.get('characters', []):
        cid = entry['id']
        cands = candidates(cid, lines, flagged)
        if not cands:
            entry['entry_state'] = 'awaiting-ref-clips'
            entry.setdefault('entry_note', 'zero clean in-house r998 material in EP001-003 '
                            '(casting gap) -- sourcing = future station')
            no_mat.append(cid)
            per_char[cid] = {'n_clips': 0, 'gate': 'no-material'}
            say('%s: no clean in-house candidates (honest gap)' % cid)
            continue
        mets, kept = [], []
        for ln in cands:
            m = clip_metrics(ln['file'])
            if m.get('f0_hz') is None or m['dur_s'] < DUR_MIN:
                say('%s: clip %s analysis-reject (%s)' % (cid, ln['name'], m))
                continue
            mets.append(m)
            kept.append((ln, m))
        gate, detail = consistency_gate(mets)
        if gate.startswith('REJECT'):
            say('%s: 音色一致检 %s %s -- entry NOT admitted' % (cid, gate, detail))
            per_char[cid] = {'n_clips': len(mets), 'gate': gate, 'detail': detail}
            continue
        entry['ref_clips'] = []
        for ln, m in kept:
            entry['ref_clips'].append({
                'name': ln['name'], 'path': ln['file'], 'text': ln['text'],
                'ep': ln['ep'], 'n': ln['n'], 'speaker': ln.get('speaker'),
                'source_ref': ln.get('ref'), 'audio_s': ln.get('audio_s'),
                'sr': m['sr'], 'dur_s': m['dur_s'], 'rms_dbfs': m['rms_dbfs'],
                'f0_hz': m['f0_hz'], 'centroid_hz': m['centroid_hz'],
                'audition_flags': 'clean (zero hard/soft/pacing hit)',
            })
        entry['entry_state'] = 'admitted' if len(kept) >= 2 else 'admitted-single-clip'
        entry['entry_note'] = '音色一致检 v0.1 %s%s' % (
            gate, (' ' + json.dumps(detail) if detail else ''))
        entry['added_ts'] = now_iso()
        per_char[cid] = {'n_clips': len(kept), 'gate': gate,
                        'f0_hz': kept[0][1]['f0_hz'],
                        'clips': [ln['name'] for ln, _ in kept]}
        admitted.append(cid)
        if len(kept) == 1:
            single.append(cid)
        say('%s: admitted %d clip(s) gate=%s %s' % (
            cid, len(kept), gate, [ln['name'] for ln, _ in kept]))
    # top-level admission block + honest-gap refresh (fresh read preserved)
    vb['admission_v0.1'] = {
        'ts': now_iso(),
        'gate': '音色一致检 v0.1 deterministic proxy: cross-clip F0 (rel<=%.2f) + RMS '
                '(spread<=%.1fdB) + spectral centroid (rel<=%.2f); single-clip = vacuous '
                'pass; embedding-level timbre identity = future station' % (
                    F0_REL_TOL, RMS_SPREAD_DB, CENTROID_REL_TOL),
        'sourcing': 'in-house r998 drama audition artifacts (self-recorded/in-house '
                    'shortlist option; zero license risk) -- external corpus license '
                    'review stays open for the BOY gap + differentiation station',
        'admitted': admitted,
        'single_clip': single,
        'no_material': no_mat,
    }
    gaps = list(vb.get('honest_gaps', []))
    for g in [
        'ref clips admitted %s from r998 in-house assets; BOY zero material in EP001-003 '
        '(no child-voice lines) -- BOY sourcing = future station (self-record/CEO clips/'
        'corpus w/ license review)' % '+'.join(admitted),
        'shared-base-voice debt: XIONG/XIONGWEI/FATHER all rendered from the voice_07 '
        'base in r998 (F0 near-identical by construction); MANCANG shares voice_05 with '
        'the narrator -- per-character differentiation = param/finetune station before '
        'full-episode casting',
        '音色一致检 v0.1 = deterministic F0/RMS/centroid proxy, not speaker-embedding '
        'timbre identity; embedding-level gate = future station',
    ]:
        if g not in gaps:
            gaps.append(g)
    vb['honest_gaps'] = gaps
    vb['updated_ts'] = now_iso()
    wr_json(VB_MANIFEST, vb)
    # status face + receipt
    elapsed = round(time.time() - t0, 1)
    st = wr_status({'state': 'done', 'ts': now_iso(), 'elapsed_s': elapsed,
                    'admitted_n': len(admitted), 'admitted': admitted,
                    'single_clip': single, 'no_material': no_mat,
                    'per_char': per_char,
                    'receipt': os.path.relpath(RECEIPT, ROOT).replace('\\', '/')})
    write_receipt(vb, per_char, admitted, single, no_mat, elapsed)
    say('ENTRIES DONE: admitted %d/7 (%s single-clip, %s no-material) in %ss -> %s' % (
        len(admitted), ','.join(single) or '-', ','.join(no_mat) or '-',
        elapsed, RECEIPT))
    return 0


def write_receipt(vb, per_char, admitted, single, no_mat, elapsed):
    os.makedirs(OUTBOX, exist_ok=True)
    md = []
    md.append('# 正典声银行条目 v0.1（canon voice-bank entries · ST-008）')
    md.append('')
    md.append('> 站点=CONTENT-LOOP v0.1 ST-008（r1017 指针件 2·声库车道 P1 ≤10-22）；')
    md.append('> 承接=ST-006 manifest v0.1（条目 schema+入行门规格）+ ST-007 链路验证 PASS；')
    md.append('> 正身=content/drama/voice_bank/manifest.json（本件=回执面）。时点=%s。' % now_iso())
    md.append('> 车道=cpu；云端零调用（429 经济）。选片+分析耗时 %ss。' % elapsed)
    md.append('')
    md.append('## 入行结论：%d/7 角色参考音入行（音色一致检 v0.1）' % len(admitted))
    md.append('')
    md.append('- 入行判据=选片律（AUDITION-r999 硬/软/节拍旗零命中+单说话人+ok+1.5-10s 窗+3.5s 甜点距排序）')
    md.append('  + 音色一致检 v0.1 确定性代理门（跨片 F0 相对差 ≤%.0f%%·RMS 极差 ≤%.0fdB·谱心相对差 ≤%.0f%%）。' % (
        F0_REL_TOL * 100, RMS_SPREAD_DB, CENTROID_REL_TOL * 100))
    md.append('- 素材=**本仓自产 r998 结构试音件**（零许可风险·逐行文本机读·真实普通话对白）——')
    md.append('  manifest 寻源短线「self-recorded/自产素材」档的落地；外部语料（AISHELL-3）许可面仍留待后续站。')
    md.append('')
    md.append('| 角色 | r998 对齐 | 入行片数 | F0 中位 (Hz) | 门 |')
    md.append('|---|---|---|---|---|')
    cast_face = {'CH': '长->protagonist', 'XIONG': '熊->villain', 'XIONGWEI': '熊伟->villain-son',
                 'MANCANG': '满仓->comic happy6', 'RED': '红利->reporter female', 'FATHER': '父->father',
                 'BOY': '-'}
    for cid in ('CH', 'XIONG', 'RED', 'MANCANG', 'XIONGWEI', 'FATHER', 'BOY'):
        pc = per_char.get(cid, {})
        md.append('| %s | %s | %s | %s | %s |' % (
            cid, cast_face[cid], pc.get('n_clips', 0),
            (str(pc.get('f0_hz', '-')) if pc.get('f0_hz') else '多片见正身'),
            pc.get('gate', 'no-material')))
    md.append('')
    md.append('## 逐角色入行明细（clip 级证据在 manifest 正身）')
    md.append('')
    for cid in admitted:
        pc = per_char[cid]
        md.append('- **%s**（%d 片·%s）：%s。' % (
            cid, pc['n_clips'], pc['gate'], '、'.join(pc['clips'])))
    no_mat_reasons = {
        'MANCANG': 'EP001-003 的 7 条满仓行全部带 AUDITION 硬旗 CLIPPED（无干净片）',
        'BOY': 'EP001-003 无儿童声行素材',
    }
    for cid in no_mat:
        md.append('- **%s**：%s——**诚实缺口不入行**，寻源=后续站（自录/CEO 提供/带许可审的外部语料）。' % (
            cid, no_mat_reasons.get(cid, 'EP001-003 无干净素材')))
    md.append('')
    md.append('## 诚实边界')
    md.append('')
    md.append('- **共享底嗓债**：XIONG/XIONGWEI/FATHER 三角色在 r998 全部由 voice_07 底噪渲染（F0 构造性')
    md.append('  近同·熊家父子=族内共享系合理）；MANCANG 与旁白共享 voice_05 底。差异化=后续参数/微调站')
    md.append('  （full-episode casting 前必须解）。')
    md.append('- 单片角色（%s）过检=「单片空真」档：行内有 1 条干净素材、无跨片可检面——补片=后续批素材扩产。' % (
        '、'.join(single) or '无'))
    md.append('- 音色一致检 v0.1=确定性代理（F0/RMS/谱心），非说话人嵌入级音色同一性检——嵌入级门=后续站。')
    md.append('- 入行参考音未经人耳听感门（听感抽检=QC 站的活）；r998 试音旗标 25 行 CLIPPED 件已按律排除。')
    md.append('')
    md.append('## 下一步（CONTENT-LOOP 后续站位）')
    md.append('')
    md.append('- BOY 参考音寻源站（儿童声·许可面先审）+ 单片角色补片（新批台词/去削波再产）。')
    md.append('- 角色差异化站：voice_07/voice_05 共享底嗓的参数分档或 GPT-SoVITS 微调面评估。')
    md.append('- 批产站：逐镜 TTS 批产 runner（resume-safe·失败行隔离）+ QC 门三查接线（入行参考音为本站产物）。')
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')


def do_status():
    st = rd_json(STATUS, {})
    print(json.dumps({'state': st.get('state'), 'admitted_n': st.get('admitted_n'),
                     'admitted': st.get('admitted'), 'no_material': st.get('no_material'),
                     'updated_at': st.get('updated_at'),
                     'receipt': st.get('receipt')}, ensure_ascii=False))
    return 0


def selftest():
    asserts = []
    man = rd_json(MANIFEST_R998, None)
    asserts.append(('r998-manifest-readable', isinstance(man, dict) and len(man.get('lines', [])) >= 50))
    flagged = flagged_names()
    # frozen r999 artifact fact: 25 hard + 8 pacing - 6 overlap = 27 union names
    asserts.append(('flagged-parse-27', len(flagged) == 27))
    lines = (man or {}).get('lines', [])
    # honest corpus facts: MANCANG all-7-lines hard-CLIPPED, BOY zero material
    need = {'CH': 3, 'XIONG': 3, 'XIONGWEI': 2, 'RED': 2, 'MANCANG': 0, 'FATHER': 1, 'BOY': 0}
    for cid, k in need.items():
        cands = candidates(cid, lines, flagged)
        asserts.append(('cands-%s-%d' % (cid, k), len(cands) == k))
    c1 = candidates('CH', lines, flagged)
    c2 = candidates('CH', lines, flagged)
    asserts.append(('selection-deterministic', [c['name'] for c in c1] == [c['name'] for c in c2]))
    sr = 22050
    t = np.arange(0, 1.0, 1.0 / sr)
    sine = 0.3 * np.sin(2 * np.pi * 200.0 * t)
    f0, cent, nv = f0_centroid_stats(sine, sr)
    asserts.append(('sine-f0-200hz', f0 is not None and abs(f0 - 200.0) <= 10.0))
    asserts.append(('vb-manifest-in-repo', VB_MANIFEST.startswith(ROOT)))
    ok_gate, _ = consistency_gate([
        {'f0_hz': 130.0, 'rms_dbfs': -22.0, 'centroid_hz': 900.0},
        {'f0_hz': 135.0, 'rms_dbfs': -24.0, 'centroid_hz': 950.0}])
    asserts.append(('gate-pass-accepts-consistent', ok_gate == 'pass'))
    bad_gate, _ = consistency_gate([
        {'f0_hz': 130.0, 'rms_dbfs': -22.0, 'centroid_hz': 900.0},
        {'f0_hz': 260.0, 'rms_dbfs': -22.0, 'centroid_hz': 900.0}])
    asserts.append(('gate-rejects-f0-octave-jump', bad_gate == 'REJECT'))
    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                      'asserts': {k: v for k, v in asserts}}, ensure_ascii=False))
    return rc


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'status'
    if cmd == 'run':
        sys.exit(do_run())
    elif cmd == 'status':
        sys.exit(do_status())
    elif cmd == 'selftest':
        sys.exit(selftest())
    else:
        print(json.dumps({'verdict': 'usage', 'cmds': ['run', 'status', 'selftest']}))
        sys.exit(2)
