# -*- coding: utf-8 -*-
"""ST-010: pitch-tier test-synthesis station driver (drama voice lane, bm-b).

Scope (r1020/r1019 next-pointer first action; ST-009 receipt next-station row):
- voice_07 shared-base family (XIONG / XIONGWEI / FATHER): 1 line each through
  the GPT-SoVITS zero-shot chain (per-character admitted manifest ref clip ->
  clone -> SAME fixed target text), then post-synthesis DSP pitch-tier shift
  + RMS re-match (ST-009 honest-limit item), then deterministic re-measurement
  of F0 separation (same autocorr metric family as ST-008 音色一致检).
- Two-stage tier method (ST-010 finding: zero-shot same-text synthesis
  homogenizes F0 register toward the text prosody, so ref-clip-derived offsets
  do not transfer):
  stage 1 = ST-009 frozen-face offsets (machine-read from its status face)
            applied to the synthesized outputs -> measured (debt transfer
            evidence);
  stage 2 = deterministic re-tier ON the synthesized raw F0s (reuse of the
            ST-009 tier_search: same direction constraints / min-total /
            tie-break law) -> applied -> re-measured -> gate.
- Text-controlled design: all three characters speak the SAME target line, so
  post-DSP F0 differences are voice-driven, not content-driven.
- Gate: every within-family pair F0 rel diff >= 0.15 on the delivered tier
  outputs (out of the same-voice band).

Commands: run / status / selftest
Status face: results/drama_env/pitch_tier_test_synth.json (in-repo)
Products:   media/drama-tools/voice_smoke/st010/<CID>/{ref.wav,out/output.wav,
            tier.wav, tier_frozen.wav} (media area, gitignored) + receipt
Laws: U060 no-window; CPU lane; cloud forbidden; idempotent ensure-done;
reuse-not-rewrite (measurement = voice_bank_entries.clip_metrics; tier search
= voice_differentiation_eval.tier_search).
"""
import datetime
import io
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
GRP = r'C:\Fluxgroup\FluxGroup'
REPO = os.path.join(GRP, 'media', 'drama-tools', 'GPT-SoVITS')
VPY = os.path.join(REPO, 'runtime', 'Scripts', 'python.exe')
GPT_MODEL = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models',
                         's1bert25hz-2kh-longer-epoch=68e-step=50232.ckpt')
SOVITS_MODEL = os.path.join(REPO, 'GPT_SoVITS', 'pretrained_models', 's2G488k.pth')
INFER_CLI = os.path.join('GPT_SoVITS', 'inference_cli.py')  # relative to REPO cwd
VD_STATUS_SRC = os.path.join(ROOT, 'results', 'drama_env', 'voice_differentiation_eval.json')
VB_MANIFEST = os.path.join(ROOT, 'content', 'drama', 'voice_bank', 'manifest.json')
ST010_DIR = os.path.join(GRP, 'media', 'drama-tools', 'voice_smoke', 'st010')
DSP_HELPER = os.path.join(ROOT, 'content', 'drama', 'runner_assets', 'st010_dsp_helper.py')
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'pitch_tier_test_synth.json')
OUTBOX = os.path.join(ROOT, 'content', 'drama', 'outbox')
RECEIPT = os.path.join(OUTBOX, 'ST-010-PITCH-TIER-TEST-SYNTH-RECEIPT.md')
FAMILY = ['XIONG', 'XIONGWEI', 'FATHER']
TARGET_TEXT = '成交量不会说谎，人心才会。'  # ST-007 chain-proven fixed line
SEP_TARGET = 0.15
INFER_TIMEOUT = 180  # per-line; measured ~20s
NO_WINDOW = 0x08000000

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import voice_bank_entries as vbe  # noqa: E402  (reuse: clip_metrics measurement)
import voice_differentiation_eval as vde  # noqa: E402  (reuse: tier_search law)


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


def wr_status(patch):
    st = rd_json(STATUS, {})
    st.update(patch)
    st['updated_at'] = now_iso()
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    tmp = STATUS + '.tmp'
    with io.open(tmp, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)
    os.replace(tmp, STATUS)
    return st


def rel_diff(a, b):
    hi = max(abs(a), abs(b))
    return 0.0 if hi == 0 else abs(a - b) / hi


def frozen_offsets():
    """Machine-read the ST-009 frozen pitch-tier face (r587 live-read family)."""
    vd = rd_json(VD_STATUS_SRC, {})
    tier = (vd.get('pitch_tier') or {}).get('voice_07.wav') or {}
    offs = tier.get('offsets') or {}
    if not all(c in offs for c in FAMILY):
        raise RuntimeError('ST-009 pitch_tier face missing family offsets: %s' % sorted(offs))
    return {c: int(offs[c]) for c in FAMILY}, tier.get('projected_f0') or {}


def ref_clips():
    vb = rd_json(VB_MANIFEST, {})
    out = {}
    for entry in vb.get('characters', []):
        cid = entry.get('id')
        if cid in FAMILY and entry.get('entry_state', '').startswith('admitted'):
            clips = entry.get('ref_clips') or []
            if clips:
                out[cid] = clips[0]
    missing = [c for c in FAMILY if c not in out]
    if missing:
        raise RuntimeError('admitted ref clips missing: %s' % missing)
    return out


def build_args(ref_wav, ref_txt, tgt_txt, out_dir):
    return [VPY, INFER_CLI,
            '--gpt_model', GPT_MODEL,
            '--sovits_model', SOVITS_MODEL,
            '--ref_audio', ref_wav,
            '--ref_text', ref_txt,
            '--ref_language', '中文',
            '--target_text', tgt_txt,
            '--target_language', '中文',
            '--output_path', out_dir]


def relay_run(cmd, cwd, timeout):
    """r680/r1045: spawn child with live line relay (keepalive + evidence)."""
    env = dict(os.environ)
    env['PYTHONPATH'] = REPO
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    p = subprocess.Popen(cmd, cwd=cwd, env=env, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    lines = []
    deadline = time.time() + timeout
    for raw in p.stdout:
        tline = raw.decode('utf-8', 'replace').rstrip()
        say('  | ' + tline[:160])
        lines.append(tline)
        if time.time() > deadline:
            p.kill()
            p.wait(timeout=30)
            return 124, lines
    rc = p.wait(timeout=max(30, int(deadline - time.time())))
    return rc, lines


def verify_wav(path):
    """ST-007 family deterministic probe via venv soundfile."""
    code = ('import soundfile as sf, numpy as np, json, sys;'
            'd,sr=sf.read(sys.argv[1]);'
            'print(json.dumps({"dur": round(len(d)/sr, 2), "sr": sr,'
            '"rms": float(np.sqrt(np.mean(d.astype("float64")**2))),'
            '"bytes": int(__import__("os").path.getsize(sys.argv[1]))}))')
    r = subprocess.run([VPY, '-c', code, path], capture_output=True,
                       timeout=120, creationflags=NO_WINDOW)
    out = r.stdout.decode('utf-8', 'replace').strip()
    if r.returncode != 0 or not out.startswith('{'):
        return False, {}
    f = json.loads(out.splitlines()[-1])
    ok = f['dur'] >= 1.0 and f['rms'] > 1e-3 and f['bytes'] > 20000
    return ok, f


def _pad_ref_silence(wav_path, target_s):
    """Pad tail silence so the ref clears the engine 3-10s gate (FATHER single
    admitted clip is 2.31s -- ST-008 frozen fact: no alternative clean
    material). Stdlib wave mono/16-bit path; returns the pad disclosure."""
    import wave as _w
    with _w.open(wav_path, 'rb') as w:
        params = w.getparams()
        n = w.getnframes()
        raw = w.readframes(n)
    dur = n / float(params.framerate)
    if dur >= target_s:
        return None
    add_frames = int(round((target_s - dur) * params.framerate))
    with _w.open(wav_path, 'wb') as w:
        w.setparams(params)
        w.writeframes(raw)
        w.writeframes(b'\x00' * (add_frames * params.nchannels * params.sampwidth))
    return 'padded %.2fs -> %.2fs (tail silence, engine 3-10s ref gate)' % (dur, target_s)


def synth_one(cid, clip):
    """Synthesize (raw-cache reuse when a verified output exists) + measure."""
    d = os.path.join(ST010_DIR, cid)
    out_dir = os.path.join(d, 'out')
    os.makedirs(out_dir, exist_ok=True)
    ref_wav = os.path.join(d, 'ref.wav')
    if not os.path.exists(ref_wav):
        shutil.copy2(clip['path'], ref_wav)
    pad_note = _pad_ref_silence(ref_wav, 3.05)
    if pad_note:
        say('%s: ref %s' % (cid, pad_note))
    raw_wav = os.path.join(out_dir, 'output.wav')
    if os.path.exists(raw_wav):
        ok0, facts0 = verify_wav(raw_wav)
        if ok0:
            say('%s: raw-cache-hit (verified %.2fs rms=%.4f)' % (
                cid, facts0['dur'], facts0['rms']))
            return d, raw_wav, facts0, 0.0, pad_note
        os.remove(raw_wav)
    ref_txt = os.path.join(d, 'ref_text.txt')
    tgt_txt = os.path.join(d, 'target_text.txt')
    with io.open(ref_txt, 'w', encoding='utf-8') as f:
        f.write(clip['text'])
    with io.open(tgt_txt, 'w', encoding='utf-8') as f:
        f.write(TARGET_TEXT)
    t0 = time.time()
    rc, _ = relay_run(build_args(ref_wav, ref_txt, tgt_txt, out_dir), REPO, INFER_TIMEOUT)
    wall = round(time.time() - t0, 1)
    if rc != 0:
        raise RuntimeError('%s inference rc=%s' % (cid, rc))
    ok, facts = verify_wav(raw_wav)
    if not ok:
        raise RuntimeError('%s raw wav verify FAIL %s' % (cid, facts))
    return d, raw_wav, facts, wall, pad_note


def dsp_one(d, raw_wav, n_steps, out_name='tier.wav'):
    out_wav = os.path.join(d, out_name)
    r = subprocess.run([VPY, DSP_HELPER, raw_wav, out_wav, str(n_steps)],
                       capture_output=True, timeout=180, creationflags=NO_WINDOW)
    out = (r.stdout or b'').decode('utf-8', 'replace').strip()
    if r.returncode != 0:
        raise RuntimeError('dsp helper FAIL: %s' %
                           ((r.stderr or b'').decode('utf-8', 'replace')[-200:]))
    return out_wav, json.loads(out.splitlines()[-1])


def pair_matrix(f0s):
    pairs = []
    for i, a in enumerate(FAMILY):
        for b in FAMILY[i + 1:]:
            pairs.append({'a': a, 'b': b,
                          'f0_rel': round(rel_diff(f0s[a], f0s[b]), 4)})
    return pairs


def do_run():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    # idempotency gate: done + delivered tier wavs present -> early exit
    st = rd_json(STATUS, {})
    if st.get('state') == 'done' and st.get('gate') == 'PASS' and all(
            os.path.exists(os.path.join(ST010_DIR, c, 'tier.wav')) for c in FAMILY):
        say('pitch-tier test-synth already done (idempotent early exit)')
        return 0
    if not (os.path.exists(VPY) and os.path.exists(GPT_MODEL)
            and os.path.exists(SOVITS_MODEL)):
        say('env artifacts missing (vpy/gpt/sovits)')
        wr_status({'state': 'blocked-env', 'ts': now_iso()})
        return 2
    foffs, proj = frozen_offsets()
    say('frozen ST-009 offsets (machine-read): %s projected=%s' % (foffs, proj))
    clips = ref_clips()
    chars = {}
    for cid in FAMILY:
        clip = clips[cid]
        d, raw_wav, raw_facts, wall, pad_note = synth_one(cid, clip)
        raw_m = vbe.clip_metrics(raw_wav)
        if raw_m.get('f0_hz') is None:
            raise RuntimeError('%s raw analysis-reject (%s)' % (cid, raw_m))
        chars[cid] = {
            'ref_clip': {'name': clip['name'], 'text': clip['text'],
                         'source_ref': clip.get('source_ref'),
                         'f0_hz_ref': clip.get('f0_hz')},
            'ref_padded': pad_note,
            'raw': {'wav': raw_wav, 'f0_hz': raw_m['f0_hz'],
                    'centroid_hz': raw_m['centroid_hz'], 'rms_dbfs': raw_m['rms_dbfs'],
                    'dur_s': raw_m['dur_s'], 'infer_wall_s': wall},
        }
        say('%s: ref f0=%s -> raw synth f0=%s' % (
            cid, clip.get('f0_hz'), raw_m['f0_hz']))
    raw_f0 = {c: chars[c]['raw']['f0_hz'] for c in FAMILY}
    pairs_before = pair_matrix(raw_f0)
    # --- stage 1: frozen-face offsets on synth outputs (debt-transfer evidence)
    frozen_pairs, frozen_tiers = [], {}
    for cid in FAMILY:
        tw, dsp = dsp_one(os.path.join(ST010_DIR, cid),
                          chars[cid]['raw']['wav'], foffs[cid],
                          'tier_frozen.wav')
        m = vbe.clip_metrics(tw)
        if m.get('f0_hz') is None:
            raise RuntimeError('%s frozen-tier analysis-reject' % cid)
        frozen_tiers[cid] = m['f0_hz']
        chars[cid]['tier_frozen'] = {'wav': tw, 'f0_hz': m['f0_hz'],
                                     'rms_dbfs': m['rms_dbfs'], 'dsp': dsp}
    frozen_pairs = pair_matrix(frozen_tiers)
    frozen_gate_ok = all(p['f0_rel'] >= SEP_TARGET for p in frozen_pairs)
    say('stage1 frozen-face gate=%s pairs=%s' % (
        'PASS' if frozen_gate_ok else 'FAIL', frozen_pairs))
    # --- stage 2/3: deterministic re-tier ON synth raw F0s (ST-009 tier_search
    # law) + bounded verify-adjust loop (batch-method prototype: nominal st !=
    # measured st on real speech, so separation must be re-MEASURED and the
    # most-deficient pair's shift extended by 1 st within direction+range law;
    # <=3 iterations, deterministic, full trace recorded).
    stats_face = {c: {'f0': raw_f0[c]} for c in FAMILY}
    tier = vde.tier_search(sorted(FAMILY), stats_face)
    if tier is None:
        raise RuntimeError('re-tier search infeasible on synth F0s %s' % raw_f0)
    cur = {c: int(tier['offsets'][c]) for c in FAMILY}
    say('stage2 re-tier on synth F0s: %s projected=%s total=%sst' % (
        cur, tier['projected_f0'], tier['total_st']))
    attempts = []
    for it in range(3):
        meas, wavs = {}, {}
        for cid in FAMILY:
            tw, dsp = dsp_one(os.path.join(ST010_DIR, cid),
                              chars[cid]['raw']['wav'], cur[cid], 'tier.wav')
            m = vbe.clip_metrics(tw)
            if m.get('f0_hz') is None:
                raise RuntimeError('%s tier analysis-reject (iter %d)' % (cid, it))
            meas[cid] = m
            wavs[cid] = (tw, dsp)
        pairs_it = pair_matrix({c: meas[c]['f0_hz'] for c in FAMILY})
        ok_it = all(p['f0_rel'] >= SEP_TARGET for p in pairs_it)
        attempts.append({'iter': it, 'offsets': dict(cur),
                         'measured_f0': {c: meas[c]['f0_hz'] for c in FAMILY},
                         'pairs': pairs_it, 'ok': ok_it})
        say('verify iter %d: offsets=%s pairs=%s ok=%s' % (
            it, cur, [p['f0_rel'] for p in pairs_it], ok_it))
        if ok_it:
            break
        short = [p for p in pairs_it if p['f0_rel'] < SEP_TARGET]
        worst = max(short, key=lambda p: SEP_TARGET - p['f0_rel'])
        fa, fb = meas[worst['a']]['f0_hz'], meas[worst['b']]['f0_hz']
        lo, hi = (worst['a'], worst['b']) if fa < fb else (worst['b'], worst['a'])
        cand = []
        if vde.DIRECTION.get(lo, 0) <= 0 and cur[lo] > -vde.ST_RANGE:
            cand.append((abs(cur[lo]) + 1, lo, cur[lo] - 1))
        if vde.DIRECTION.get(hi, 0) >= 0 and cur[hi] < vde.ST_RANGE:
            cand.append((abs(cur[hi]) + 1, hi, cur[hi] + 1))
        cand = [c for c in cand if (
            (vde.DIRECTION.get(c[1], 0) < 0 and c[2] <= 0)
            or (vde.DIRECTION.get(c[1], 0) > 0 and c[2] >= 0)
            or vde.DIRECTION.get(c[1], 0) == 0)]
        if not cand:
            say('adjust infeasible (direction/range law) -- honest stop')
            break
        cand.sort()
        _, who, newoff = cand[0]
        say('adjust: %s %+d -> %+d st (deficient pair %s-%s)' % (
            who, cur[who], newoff, worst['a'], worst['b']))
        cur[who] = newoff
    final = attempts[-1]
    roffs = final['offsets']
    retier_tiers = final['measured_f0']
    for cid in FAMILY:
        tw, dsp = wavs[cid]
        m = vbe.clip_metrics(tw)
        chars[cid]['offset_st'] = roffs[cid]
        chars[cid]['tier'] = {'wav': tw, 'f0_hz': m['f0_hz'],
                              'centroid_hz': m['centroid_hz'],
                              'rms_dbfs': m['rms_dbfs'], 'dur_s': m['dur_s'],
                              'dsp': dsp}
        say('%s: raw %s -> tier %+d st f0=%s (rms %.1f->%.1f dBFS)' % (
            cid, raw_f0[cid], roffs[cid], m['f0_hz'],
            chars[cid]['raw']['rms_dbfs'], m['rms_dbfs']))
    pairs_after = final['pairs']
    gate_ok = final['ok']
    verdict = 'PASS' if gate_ok else 'FAIL'
    max_abs = max(abs(o) for o in roffs.values())
    out = {
        'schema': 'pitch-tier-test-synth-v2', 'state': 'done', 'ts': now_iso(),
        'target_text': TARGET_TEXT,
        'frozen_tier': {'offsets': foffs, 'st009_projected_f0': proj,
                        'pairs': frozen_pairs,
                        'gate': 'PASS' if frozen_gate_ok else 'FAIL'},
        'retier': {'offsets': roffs,
                   'search_offsets': {c: int(tier['offsets'][c]) for c in FAMILY},
                   'projected_f0': tier['projected_f0'],
                   'projected_pairs': tier['projected_pairs'],
                   'attempts': attempts,
                   'total_st': sum(abs(o) for o in roffs.values()),
                   'max_abs_st': max_abs},
        'chars': chars, 'pairs_before_raw': pairs_before,
        'pairs_after_tier': pairs_after, 'gate': verdict,
        'sep_target': SEP_TARGET,
        'honest_limits': [
            'KEY FINDING: zero-shot same-text synthesis homogenizes F0 register '
            'toward text prosody (raw synth XIONG/XIONGWEI/FATHER all ~172-178Hz '
            'despite ref F0 165.8/162.8/151.0) -- ref-clip-derived tier offsets '
            'do NOT transfer to synthesized outputs; tier must be derived per '
            'synthesis chain (this station = stage-2 re-tier), and the batch '
            'station must re-verify separation per line (per-line F0 drift)',
            'nominal semitone != measured semitone on real speech (DSP-shifted '
            'F0 median deviates from the geometric projection: FATHER -4st '
            'nominal -> ~-3.5st measured) -- separation gates must verify on '
            'MEASURED outputs (the station verify-adjust loop), not on '
            'projections; this loop is the batch-station method prototype',
            'librosa pitch_shift = phase-vocoder + resample: formants move with '
            'F0 (not strictly formant-preserving; corrects the ST-009 wording); '
            'the +/-3 st safe zone applies to DSP distortion risk',
            'F0/centroid proxy only (autocorr metric family); embedding-level '
            'timbre identity = future station',
            'single-line sample per character (1 sentence); multi-line robustness '
            '= batch-production station',
            'ear-check (human listening spot-check) NOT run at this station -- '
            'queued for the QC gate; this station = deterministic acoustic gate',
            'XIONG offset +0 st = raw baseline passthrough (RMS re-match identity)',
            'FATHER single admitted clip 2.31s padded to 3.05s with tail silence '
            'to clear the engine 3-10s ref gate (no clean alternative material '
            'per ST-008; re-supply station pending)',
        ],
        'receipt': os.path.relpath(RECEIPT, ROOT).replace('\\', '/'),
    }
    if max_abs > 3:
        out['honest_limits'].append(
            're-tier max |offset| = %d st exceeds the +/-3 st DSP safe zone '
            '(min-total solution under direction constraints; ear-check weight '
            'rises; root fix remains distinct-source re-supply -- ST-011/ST-009 '
            'sec.3)' % max_abs)
    write_receipt(out)
    wr_status(out)  # state=done lands only after receipt exists
    print(json.dumps({'state': 'done', 'gate': verdict,
                      'retier_offsets': roffs,
                      'pairs_after': pairs_after,
                      'receipt': out['receipt']}, ensure_ascii=False))
    return 0 if gate_ok else 1


def write_receipt(out):
    os.makedirs(OUTBOX, exist_ok=True)
    md = []
    a = md.append
    a('# ST-010 分档试合成回执（pitch-tier test-synthesis · voice_07 家族）')
    a('')
    a('> 站点=CONTENT-LOOP v0.1 ST-010（r1020 指针件 1 首动作·r1019 债·声库车道 P1 ≤10-22）；')
    a('> 承接=ST-009 分档方案；正身=results/drama_env/pitch_tier_test_synth.json；本件=回执面。')
    a('> 时点=%s。车道=cpu；云端零调用；文本受控设计=三角色同句『%s』。' % (
        out['ts'], out['target_text']))
    a('')
    a('## 核心发现（本站主产出）')
    a('')
    a('**零样本同句合成会把三角色 F0 全部拉平**（文本驱动韵律盖过参考音音高）：')
    a('')
    a('| 角色 | 参考音 F0 | 合成原样 F0 | 拉平方向 |')
    a('|---|---|---|---|')
    for cid in FAMILY:
        ch = out['chars'][cid]
        ref = ch['ref_clip']['f0_hz_ref']
        raw = ch['raw']['f0_hz']
        a('| %s | %s Hz | %s Hz | %s |' % (
            cid, ref, raw,
            '上漂' if (raw or 0) > (ref or 0) else '下漂'))
    a('')
    a('合成原样对 F0 相对差=%.1f%%/%.1f%%/%.1f%%——**共享底嗓债在合成面上比参考音面更深**'
      '（同嗓带），且 ST-009 按参考音 F0 冻结的分档（%s）在合成面上投影不足'
      '（门判=%s）。' % (
          out['pairs_before_raw'][0]['f0_rel'] * 100,
          out['pairs_before_raw'][1]['f0_rel'] * 100,
          out['pairs_before_raw'][2]['f0_rel'] * 100,
          json.dumps(out['frozen_tier']['offsets']),
          out['frozen_tier']['gate']))
    a('')
    a('## 二段法：合成面重分档 + 校验-调整环（ST-009 tier_search 同律复用）')
    a('')
    a('stage2 在合成原样 F0 上重跑确定性分档搜索（方向约束 XIONG≤0/XIONGWEI≥0/FATHER≤0·最小总移位）；')
    a('因名义半音≠实测半音（DSP 后 F0 中位偏离几何投影），搜索结果过**校验-调整环**：')
    a('实测复测→未达标对按方向律+搜索域扩 1 半音→复测（≤3 迭代·确定性·全程留痕）。')
    a('')
    a('| 角色 | 合成原样 F0 | 搜索移位 | 调整环终档 | 投影 F0 | 实测分档后 F0 | RMS 复配（dBFS） |')
    a('|---|---|---|---|---|---|---|')
    for cid in FAMILY:
        ch = out['chars'][cid]
        a('| %s | %s Hz | %+d st | %+d st | %s Hz | %s Hz | %.1f → %.1f |' % (
            cid, ch['raw']['f0_hz'],
            out['retier']['search_offsets'][cid], ch['offset_st'],
            out['retier']['projected_f0'][cid], ch['tier']['f0_hz'],
            ch['raw']['rms_dbfs'], ch['tier']['rms_dbfs']))
    a('')
    a('校验-调整环轨迹：')
    for att in out['retier']['attempts']:
        a('- 迭代 %d：offsets=%s → 实测对 %s → %s' % (
            att['iter'], json.dumps(att['offsets']),
            '/'.join('%.1f%%' % (p['f0_rel'] * 100) for p in att['pairs']),
            '全对达标' if att['ok'] else '未达标→续调'))
    a('')
    a('## 分离矩阵（同嗓带判据：F0 相对差 ≤15% = 同嗓带）')
    a('')
    a('| 角色对 | 合成原样（债面） | stage1 冻结分档 | stage2 重分档 | 判读 |')
    a('|---|---|---|---|---|')
    for pb, pf, pa in zip(out['pairs_before_raw'],
                          out['frozen_tier']['pairs'],
                          out['pairs_after_tier']):
        a('| %s–%s | %.1f%% | %.1f%% | %.1f%% | %s |' % (
            pb['a'], pb['b'], pb['f0_rel'] * 100, pf['f0_rel'] * 100,
            pa['f0_rel'] * 100,
            '达标（出同嗓带）' if pa['f0_rel'] >= out['sep_target'] else '未达标'))
    a('')
    a('**门判=%s**：stage2 重分档后组内所有对 F0 相对差 ≥15%% 判据 %s'
      '（总移位 %d st·最大 |移位| %d st）。' % (
          out['gate'], '全对达标' if out['gate'] == 'PASS' else '存在未达标对（如实）',
          out['retier']['total_st'], out['retier']['max_abs_st']))
    a('')
    pads = [c for c in FAMILY if (out['chars'][c].get('ref_padded'))]
    if pads:
        a('参考音垫注：FATHER 唯一入行片 2.31s < 引擎 3-10s 参考门（ST-008 冻结事实=无干净替代素材），'
          '确定性尾静音垫至 3.05s 过门（参考文本不变·输出测量不受垫影响·如实披露）。')
        a('')
    a('## 诚实边界')
    a('')
    for lim in out['honest_limits']:
        a('- %s' % lim)
    a('')
    a('## 产物面（gitignored media 区·CEO 交付律）')
    a('')
    for cid in FAMILY:
        ch = out['chars'][cid]
        a('- %s：合成原样=`%s`；冻结面分档=`%s`；交付分档=`%s`' % (
            cid, ch['raw']['wav'], ch['tier_frozen']['wav'], ch['tier']['wav']))
    a('')
    a('## 下一步（CONTENT-LOOP 后续站位）')
    a('')
    a('- 批产站接线：分档必须在合成面上逐行验证（每行 F0 漂移不同=固定移位不保分离·逐行复测+自适应）。')
    a('- ST-011 BOY/MANCANG 寻源站（童声/市井底嗓·许可面先审；天然异底=根解路线）。')
    a('- 人耳抽检面（QC 门三查之一）+ 嵌入级音色同一性检=后续站。')
    a('')
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md) + '\n')


def do_status():
    st = rd_json(STATUS, {})
    print(json.dumps({'state': st.get('state'), 'gate': st.get('gate'),
                      'frozen_gate': (st.get('frozen_tier') or {}).get('gate'),
                      'retier_offsets': (st.get('retier') or {}).get('offsets'),
                      'pairs_after': st.get('pairs_after_tier'),
                      'receipt': st.get('receipt')}, ensure_ascii=False))
    return 0


def selftest():
    asserts = []
    # 1) frozen face machine-read + direction law
    try:
        offs, proj = frozen_offsets()
        asserts.append(('frozen-face-readable', sorted(offs) == sorted(FAMILY)))
        asserts.append(('frozen-xiong-0', offs.get('XIONG') == 0))
        asserts.append(('frozen-father-down', offs.get('FATHER', 0) <= 0))
    except Exception as e:
        asserts.append(('frozen-face-readable', False))
        asserts.append(('frozen-err', str(e)[:80]))
    # 2) admitted ref clips present
    try:
        clips = ref_clips()
        asserts.append(('refs-present', sorted(clips) == sorted(FAMILY)))
        asserts.append(('ref-files-exist', all(
            os.path.exists(clips[c]['path']) for c in FAMILY)))
    except Exception as e:
        asserts.append(('refs-present', False))
        asserts.append(('refs-err', str(e)[:80]))
    # 3) env artifacts + argv contract
    asserts.append(('models-present', os.path.exists(VPY) and os.path.exists(GPT_MODEL)
                    and os.path.exists(SOVITS_MODEL)))
    args = build_args('R', 'T', 'G', 'OUT')
    asserts.append(('args-shape', args[0] == VPY and args[1] == INFER_CLI
                    and args[11] == '中文' and args[15] == '中文'
                    and args[17] == 'OUT' and len(args) == 18))
    # 4) rel_diff semantics + pair coverage
    asserts.append(('rel-diff-max-denom', abs(rel_diff(100, 125) - 0.2) < 1e-12))
    m = pair_matrix({c: 100.0 + i for i, c in enumerate(FAMILY)})
    asserts.append(('pair-count-3', len(m) == 3))
    # 5) tier_search reuse: same-voice synth family with directions -> feasible
    syn = {'XIONG': {'f0': 173.5}, 'XIONGWEI': {'f0': 172.0}, 'FATHER': {'f0': 177.8}}
    t1 = vde.tier_search(sorted(FAMILY), syn)
    asserts.append(('retier-feasible', t1 is not None))
    if t1:
        ok_pairs = all(p['f0_rel'] >= 0.15 for p in t1['projected_pairs'])
        asserts.append(('retier-valid', ok_pairs))
        for cid in FAMILY:
            o = t1['offsets'][cid]
            d = vde.DIRECTION.get(cid, 0)
            asserts.append(('retier-dir-%s' % cid,
                            (o <= 0 if d < 0 else o >= 0) if d else True))
        t2 = vde.tier_search(sorted(FAMILY), syn)
        asserts.append(('retier-deterministic', t1 == t2))
    # 6) measurement reuse import live (autocorr family)
    import numpy as np
    t = np.arange(0, 1.0, 1.0 / 22050)
    sine = 0.3 * np.sin(2 * np.pi * 200.0 * t)
    import wave as _w
    tmp = os.path.join(ST010_DIR, '_selftest_probe.wav')
    os.makedirs(ST010_DIR, exist_ok=True)
    with _w.open(tmp, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes((sine * 32767).astype('<i2').tobytes())
    m_probe = vbe.clip_metrics(tmp)
    asserts.append(('measure-reuse-f0', m_probe.get('f0_hz') is not None
                    and abs(m_probe['f0_hz'] - 200.0) <= 10.0))
    os.remove(tmp)
    # 7) venv librosa probe (effects namespace on 0.10.x)
    r = subprocess.run([VPY, '-c',
                        'import librosa; f=getattr(librosa,"pitch_shift",None) '
                        'or librosa.effects.pitch_shift; assert callable(f)'],
                       capture_output=True, timeout=60, creationflags=NO_WINDOW)
    asserts.append(('venv-pitch-shift-face', r.returncode == 0))
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
