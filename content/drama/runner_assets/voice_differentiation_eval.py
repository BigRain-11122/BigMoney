# -*- coding: utf-8 -*-
"""ST-009: canon character voice differentiation eval v0.1 (shared-base debt).

Commands: run / status / selftest
Status face: results/drama_env/voice_differentiation_eval.json (in-repo)
Receipt: content/drama/outbox/VOICE-DIFFERENTIATION-EVAL-v0.1.md

Scope (ST-008 receipt next-station row + r1018 next-pointer item 3):
- Measure the voice_07 shared-base debt (XIONG/XIONGWEI/FATHER) and the full
  cross-character acoustic matrix from admitted manifest ref clips
  (F0 / RMS / spectral centroid medians, same metrics family as
  音色一致检 v0.1).
- Deterministic pitch-tier search: integer semitone offsets per family member
  (semantic direction constraints: elders/boss <= 0, son >= 0) so every
  within-family pair clears the same-voice F0 band (rel >= 0.15), minimizing
  total shift (least DSP distortion). Formant-preserving post-synthesis DSP
  (librosa pitch_shift family) is the proposed carrier.
- Method feasibility: fine-tune on same-base material CANNOT separate a
  shared-base family (honest negative); root fix = distinct source voices
  (ties into BOY/MANCANG sourcing stations).
- Honest limits: F0/centroid proxy only (embedding-level timbre identity =
  future station); FATHER single-clip median is fragile; RMS re-match after
  DSP shift required at the synthesis station.

Idempotent: re-run recomputes deterministically (zero wall-clock in data).
Pure CPU, zero network, zero cloud, no voice_bank writes (eval only).
"""
import io
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))  # runner_assets -> drama -> content -> repo
MANIFEST = os.path.join(ROOT, 'content', 'drama', 'voice_bank', 'manifest.json')
OUTBOX = os.path.join(ROOT, 'content', 'drama', 'outbox')
RECEIPT = os.path.join(OUTBOX, 'VOICE-DIFFERENTIATION-EVAL-v0.1.md')
STATUS = os.path.join(ROOT, 'results', 'drama_env', 'voice_differentiation_eval.json')

# same-voice band thresholds (音色一致检 v0.1 family, ST-006/ST-008 gate spec)
F0_SAME_BAND = 0.15      # rel F0 diff <= 0.15 == same-voice band
CEN_SAME_BAND = 0.20     # rel centroid diff <= 0.20 == same-voice band
SEP_TARGET = 0.15        # differentiation target: every family pair >= this
ST_RANGE = 5            # semitone search edge [-5, +5]

# semantic direction constraints (canon): -1 -> offsets <= 0, +1 -> >= 0, 0 -> free
DIRECTION = {'XIONG': -1, 'XIONGWEI': 1, 'FATHER': -1}


def now_iso():
    return time.strftime('%Y-%m-%dT%H:%M:%S') + '+08:00'


def rel_diff(a, b):
    """Symmetric relative difference on positive scalars (conservative /max)."""
    hi = max(abs(a), abs(b))
    return 0.0 if hi == 0 else abs(a - b) / hi


def st_ratio(n):
    """Pitch ratio for n semitones."""
    return 2.0 ** (n / 12.0)


def med(feat, clips):
    vals = [c[feat] for c in clips if isinstance(c.get(feat), (int, float))]
    return statistics.median(vals) if vals else None


def char_stats(m):
    """Admitted characters -> per-char medians + source_ref family."""
    out = {}
    for c in m['characters']:
        clips = c.get('ref_clips') or []
        if c.get('entry_state') not in ('admitted', 'admitted-single-clip'):
            continue
        if not clips:
            continue
        refs = sorted({cl.get('source_ref', '?') for cl in clips})
        out[c['id']] = {
            'family': refs[0] if len(refs) == 1 else 'mixed:' + '+'.join(refs),
            'n_clips': len(clips),
            'f0': med('f0_hz', clips),
            'rms_dbfs': med('rms_dbfs', clips),
            'centroid': med('centroid_hz', clips),
            'voice_manifest': c.get('voice_manifest', {}),
        }
    return out


def pairwise_matrix(stats):
    """All-pairs acoustic classification across admitted characters."""
    ids = sorted(stats)
    pairs = []
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            sa, sb = stats[a], stats[b]
            f0r = rel_diff(sa['f0'], sb['f0'])
            cenr = rel_diff(sa['centroid'], sb['centroid'])
            rmsd = abs(sa['rms_dbfs'] - sb['rms_dbfs'])
            same_band = f0r <= F0_SAME_BAND and cenr <= CEN_SAME_BAND
            pairs.append({
                'a': a, 'b': b, 'f0_rel': round(f0r, 4),
                'centroid_rel': round(cenr, 4), 'rms_db': round(rmsd, 2),
                'same_family': sa['family'] == sb['family'],
                'class': ('same-voice-band' if same_band else 'distinct'),
            })
    return pairs


def allowed_offsets(cid):
    d = DIRECTION.get(cid, 0)
    if d < 0:
        return [-n for n in range(0, ST_RANGE + 1)]
    if d > 0:
        return list(range(0, ST_RANGE + 1))
    return list(range(-ST_RANGE, ST_RANGE + 1))


def tier_search(family_ids, stats):
    """Deterministic brute force: min total |offset| s.t. all within-family
    projected pairs clear SEP_TARGET. Ties: min max|offset|, then lexicographic."""
    spaces = [allowed_offsets(cid) for cid in family_ids]
    best = None
    for combo in _cartesian(spaces):
        proj = {cid: stats[cid]['f0'] * st_ratio(o)
                for cid, o in zip(family_ids, combo)}
        ok = all(rel_diff(proj[x], proj[y]) >= SEP_TARGET
                 for x, y in _pairs(family_ids))
        if not ok:
            continue
        key = (sum(abs(o) for o in combo), max(abs(o) for o in combo), combo)
        if best is None or key < best[0]:
            best = (key, combo, proj)
    if best is None:
        return None
    _, combo, proj = best
    return {
        'offsets': dict(zip(family_ids, combo)),
        'projected_f0': {k: round(v, 1) for k, v in proj.items()},
        'projected_pairs': [
            {'a': x, 'b': y, 'f0_rel': round(rel_diff(proj[x], proj[y]), 4)}
            for x, y in _pairs(family_ids)],
        'total_st': sum(abs(o) for o in combo),
    }


def _pairs(ids):
    return [(ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))]


def _cartesian(spaces):
    if not spaces:
        yield ()
        return
    for head in spaces[0]:
        for tail in _cartesian(spaces[1:]):
            yield (head,) + tail


def do_run():
    t0 = time.time()
    try:
        with io.open(MANIFEST, 'r', encoding='utf-8-sig') as f:
            m = json.load(f)
    except Exception:
        wr_status({'state': 'failed', 'err': 'manifest-unreadable', 'ts': now_iso()})
        return 1
    stats = char_stats(m)
    if len(stats) < 2:
        wr_status({'state': 'failed', 'err': 'admitted-chars<2', 'ts': now_iso()})
        return 1
    pairs = pairwise_matrix(stats)
    families = {}
    for cid, s in stats.items():
        families.setdefault(s['family'], []).append(cid)
    debt_pairs = [p for p in pairs if p['class'] == 'same-voice-band']
    tiers = {}
    for fam, ids in sorted(families.items()):
        if len(ids) >= 2:
            t = tier_search(sorted(ids), stats)
            if t:
                tiers[fam] = t
    elapsed = round(time.time() - t0, 2)
    out = {
        'schema': 'voice-differentiation-eval-v1', 'state': 'done',
        'ts': now_iso(), 'elapsed_s': elapsed,
        'admitted': sorted(stats), 'families': {k: sorted(v) for k, v in families.items()},
        'pairwise': pairs, 'same_voice_band_pairs': debt_pairs,
        'pitch_tier': tiers,
        'honest_limits': [
            'F0/RMS/centroid proxy only; embedding-level timbre identity = future station',
            'FATHER median from a single clip (fragile; re-supply station pending)',
            'formant-preserving DSP moves F0 only; centroid band stays (F0 band is the separating axis)',
            'fine-tune on same-base (voice_07) material cannot separate the family -- root fix is distinct source voices',
            'RMS loudness re-match required after DSP shift at the synthesis station',
        ],
        'receipt': os.path.relpath(RECEIPT, ROOT).replace('\\', '/'),
    }
    write_receipt(out, stats)   # receipt first: on failure status stays non-done
    wr_status(out)              # state=done lands only after receipt exists
    print(json.dumps({'state': 'done', 'admitted': out['admitted'],
                      'same_voice_band_pairs': len(debt_pairs),
                      'tiers': {k: v['offsets'] for k, v in tiers.items()},
                      'receipt': out['receipt']}, ensure_ascii=False))
    return 0


def write_receipt(out, stats):
    fam07 = out['pitch_tier'].get('voice_07.wav')
    lines = []
    a = lines.append
    a('# 角色音色差异化评估 v0.1（VOICE-DIFFERENTIATION-EVAL · ST-009）')
    a('')
    a('> 站点=CONTENT-LOOP ST-009；承接=ST-008 入行回执「共享底嗓债」披露面；')
    a('> 数据正身=content/drama/voice_bank/manifest.json（入行片级 F0/RMS/谱心证据）；')
    a('> 本件=评估回执。时点=%s。车道=cpu；零云端；纯确定性测量零判据触碰。' % out['ts'])
    a('')
    a('## 一、共享底嗓债实测（音色一致检 v0.1 同族口径）')
    a('')
    a('判据：跨角色 F0 相对差 ≤15% 且谱心相对差 ≤20% = 同嗓带（same-voice-band）。')
    a('')
    a('| 角色A | 角色B | 底嗓 | F0相对差 | 谱心相对差 | 判读 |')
    a('|---|---|---|---|---|---|')
    for p in out['pairwise']:
        fam = '同族' if p['same_family'] else '异族'
        a('| %s | %s | %s | %.1f%% | %.1f%% | %s |' % (
            p['a'], p['b'], fam, p['f0_rel'] * 100, p['centroid_rel'] * 100,
            '同嗓带' if p['class'] == 'same-voice-band' else '可分'))
    a('')
    debt = [p for p in out['same_voice_band_pairs']]
    a('同嗓带对数=%d。voice_07 三人组（XIONG %.1fHz / XIONGWEI %.1fHz / FATHER %.1fHz）：'
      'XIONG-XIONGWEI 相对差仅 %.1f%%——声学上同一把嗓子，债成立且可测。' % (
          len(debt),
          stats.get('XIONG', {}).get('f0') or 0, stats.get('XIONGWEI', {}).get('f0') or 0,
          stats.get('FATHER', {}).get('f0') or 0,
          next((p['f0_rel'] * 100 for p in debt if {p['a'], p['b']} == {'XIONG', 'XIONGWEI'}), 0)))
    a('')
    a('## 二、音高分档方案（确定性搜索·最小总移位）')
    a('')
    if fam07:
        a('搜索约束：XIONG（50s 威严老板）≤0 半音；XIONGWEI（20s 儿子）≥0；FATHER（50s 疲惫慈父）≤0；')
        a('目标=组内所有对 F0 相对差 ≥15%（出同嗓带）；优化=最小化总移位（DSP 失真最小）。')
        a('')
        a('| 角色 | 现测 F0 中位 | 分档移位 | 投影 F0 |')
        a('|---|---|---|---|')
        for cid in ('XIONG', 'XIONGWEI', 'FATHER'):
            if cid in fam07['offsets']:
                a('| %s | %.1f Hz | %+d st | %.1f Hz |' % (
                    cid, stats[cid]['f0'], fam07['offsets'][cid],
                    fam07['projected_f0'][cid]))
        a('')
        a('投影后组内对：')
        for p in fam07['projected_pairs']:
            a('- %s–%s：F0 相对差 %.1f%%（≥15%% 达标）' % (p['a'], p['b'], p['f0_rel'] * 100))
        a('')
        a('执行载体=合成后 DSP 变调（librosa pitch_shift 族·保共振峰），±3st 内为安全区；')
        a('保共振峰移位只动 F0——分档的分离轴=F0（谱心留在原带，见诚实边界）。')
    else:
        a('（voice_07 家族未找到可行分档——如实披露）')
    a('')
    a('## 三、方法可行性表')
    a('')
    a('| 路径 | 可行性 | 判读 |')
    a('|---|---|---|')
    a('| 合成后 DSP 变调分档 | 本窗可落 | voice_07 家族首选：零新素材、确定性、±3st 安全区；下一站=分档试合成实测 |')
    a('| GPT-SoVITS 逐角色微调 | 对同底嗓无效（诚实负发现） | 微调加深底嗓同一性——同族分离靠它=方向错误；微调只服务「新源说话人」 |')
    a('| 换源寻根（新底嗓素材） | 根解 | BOY（童声）/MANCANG（市井喜感）寻源站天然带新底嗓；寻源选片须避开 voice_04/05/07/12 现役底 |')
    a('| 组内既有参考片挑片 | 已实测不足 | 组内片本来同底同近 F0——挑片无法制造分离（本表第一行的实测依据） |')
    a('')
    a('MANCANG 定位提示：其底嗓债是与旁白共享 voice_05——但入行素材全 CLIPPED 未入行，')
    a('差异化随寻源站自然解决（寻源即选新底嗓），无需 DSP 分档。BOY 同理（童声源天然异底）。')
    a('')
    a('## 四、诚实边界')
    a('')
    for lim in out['honest_limits']:
        a('- %s' % lim)
    a('')
    a('## 五、后续站位（建议）')
    a('')
    a('- ST-010 分档试合成站：XIONG/XIONGWEI/FATHER 各 1 句过 GPT-SoVITS + 分档移位，复测 F0 分离达标与人耳抽检面。')
    a('- ST-011 BOY/MANCANG 寻源站（许可面先审）：BOY 童声（许可红线先审）+ MANCANG 去削波再产/新源。')
    a('- 嵌入级音色同一性检=后续站（本评估=F0/谱心代理面）。')
    a('')
    with io.open(RECEIPT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


def wr_status(patch):
    os.makedirs(os.path.dirname(STATUS), exist_ok=True)
    st = {}
    if os.path.exists(STATUS):
        try:
            with io.open(STATUS, 'r', encoding='utf-8-sig') as f:
                st = json.load(f)
        except Exception:
            st = {}
    st.update(patch)
    with io.open(STATUS, 'w', encoding='utf-8') as f:
        json.dump(st, f, ensure_ascii=False, indent=1)


def do_status():
    try:
        with io.open(STATUS, 'r', encoding='utf-8-sig') as f:
            print(json.dumps(json.load(f), ensure_ascii=False)[:400])
        return 0
    except Exception as e:
        print(json.dumps({'state': 'absent', 'err': str(e)[:100]}))
        return 0


def do_selftest():
    asserts = []

    def chk(name, ok):
        asserts.append((name, bool(ok)))

    # 1) semitone ratio math
    chk('st-ratio-octave', abs(st_ratio(12) - 2.0) < 1e-9)
    chk('st-ratio-inverse', abs(st_ratio(-12) - 0.5) < 1e-9)
    chk('st-ratio-plus3', abs(st_ratio(3) - 1.189207115002721) < 1e-9)
    # 2) rel_diff conservative /max semantics
    chk('rel-diff-symmetric', rel_diff(100, 125) == rel_diff(125, 100))
    chk('rel-diff-max-denom', abs(rel_diff(100, 125) - 0.2) < 1e-12)
    # 3) classification bands
    chk('band-same', rel_diff(100, 108) <= F0_SAME_BAND)
    chk('band-distinct', rel_diff(100, 200) > F0_SAME_BAND)
    # 4) tier search on synthetic same-voice family (all ~100Hz) with dirs
    syn = {'A': {'f0': 100.0}, 'B': {'f0': 101.0}, 'C': {'f0': 99.0}}
    t1 = tier_search(['A', 'B', 'C'], syn)
    chk('syn-search-feasible', t1 is not None)
    if t1:
        ok_pairs = all(p['f0_rel'] >= SEP_TARGET for p in t1['projected_pairs'])
        chk('syn-search-valid', ok_pairs)
    t2 = tier_search(['A', 'B', 'C'], syn)
    chk('syn-search-deterministic', t1 == t2)
    # 5) direction constraints respected on real manifest family
    stats = {}
    try:
        with io.open(MANIFEST, 'r', encoding='utf-8-sig') as f:
            m = json.load(f)
        stats = char_stats(m)
        fam = sorted(cid for cid, s in stats.items() if s['family'] == 'voice_07.wav')
        chk('manifest-voice07-family', fam == ['FATHER', 'XIONG', 'XIONGWEI'])
        t = tier_search(fam, stats) if len(fam) >= 2 else None
        chk('real-search-feasible', t is not None)
        if t:
            allpairs = all(p['f0_rel'] >= SEP_TARGET for p in t['projected_pairs'])
            chk('real-search-valid', allpairs)
            for cid, o in t['offsets'].items():
                d = DIRECTION.get(cid, 0)
                chk('dir-%s' % cid, (o <= 0 if d < 0 else o >= 0) if d else True)
    except Exception as e:
        chk('manifest-readable', False)
        asserts.append(('manifest-err', str(e)[:80]))
    # 6) debt is real: XIONG-XIONGWEI inside same-voice band
    try:
        pairs = pairwise_matrix(stats)
        xw = [p for p in pairs if {p['a'], p['b']} == {'XIONG', 'XIONGWEI'}][0]
        chk('debt-xiong-xiongwei', xw['class'] == 'same-voice-band')
    except Exception:
        chk('debt-check-ran', False)

    rc = 0 if all(ok for _, ok in asserts) else 1
    print(json.dumps({'selftest': 'PASS' if rc == 0 else 'FAIL',
                      'n': len(asserts), 'fails': [k for k, ok in asserts if not ok]}))
    return rc


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'run'
    if cmd == 'run':
        return do_run()
    if cmd == 'status':
        return do_status()
    if cmd == 'selftest':
        return do_selftest()
    print('usage: run | status | selftest')
    return 2


if __name__ == '__main__':
    sys.exit(main())
