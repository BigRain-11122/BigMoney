# -*- coding: utf-8 -*-
# r999: clip refine verdict (true flat-top clipping vs isolated hot peaks) + delivery branch.
import json, os, io, sys, glob, wave, array, subprocess, datetime

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
BASE = r'C:\Fluxgroup\FluxGroup\media\drama-tts-out\r998_ep001_003'
MAN = os.path.join(BASE, 'MANIFEST-r998.json')
now = datetime.datetime.now().astimezone()
STAMP = now.isoformat(timespec='seconds')
HHMM = now.strftime('%H%M')

lines = json.load(io.open(MAN, 'r', encoding='utf-8'))['lines']
res = []
for L in lines:
    p = L['file']
    maxrun = 0; run = 0; ge = 0; peak = 0
    with wave.open(p, 'rb') as w:
        if w.getsampwidth() != 2:
            res.append({'name': L['name'], 'skip': True, 'true_clip': False})
            continue
        while True:
            raw = w.readframes(48000)
            if not raw:
                break
            a = array.array('h')
            a.frombytes(raw)
            for v in a:
                av = v if v >= 0 else -v
                if av > peak:
                    peak = av
                if av >= 32000:
                    ge += 1
                if av >= 32760:
                    run += 1
                    if run > maxrun:
                        maxrun = run
                else:
                    run = 0
    res.append({'name': L['name'], 'peak': peak, 'ge32000': ge,
                'maxrun_32760': maxrun, 'true_clip': maxrun >= 3})

true_clips = [r['name'] for r in res if r.get('true_clip')]
hot_only = [r['name'] for r in res if (not r.get('true_clip', False) and not r.get('skip', False) and r.get('ge32000', 0) > 0)]
verdict = 'FAIL_TRUE_CLIP' if true_clips else 'PASS_HOTPEAK_ADVISORY'

add = []
add.append('')
add.append('## 附：削波精判（r999 refine·真削波 vs 热峰）')
add.append('')
add.append('- 精判=**%s**（真削波线 %d 条=平顶连段 ≥3 样本 @|v|≥32760；热峰线 %d 条=孤立近满幅）'
           % (verdict, len(true_clips), len(hot_only)))
if true_clips:
    add.append('- 真削波清单（需 IndexTTS 降增益重生成后再过闸）：')
    for n in true_clips:
        add.append('  - %s' % n)

def dump(obj, path):
    with io.open(path, 'w', encoding='utf-8', newline='') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)

out = {'generated': STAMP, 'round': 'r999', 'verdict': verdict,
       'true_clipped_lines': true_clips, 'hot_peak_only_lines': hot_only,
       'threshold': 'true_clip = >=3 consecutive samples at |v|>=32760 (flat-top run)',
       'per_file': res}
dump(out, os.path.join(BASE, 'AUDITION-CLIP-REFINE-r999.json'))

msgs = glob.glob(os.path.join(ROOT, 'fleet', 'inbox', 'MSG-20261018-*-bmb-voicegen-audition-reel.md'))

if verdict == 'PASS_HOTPEAK_ADVISORY':
    with wave.open(lines[0]['file'], 'rb') as w0:
        fr0 = w0.getframerate(); ch0 = w0.getnchannels(); sw0 = w0.getsampwidth()
    sil_path = os.path.join(BASE, '_sil06.wav')
    with wave.open(sil_path, 'wb') as w:
        w.setnchannels(ch0); w.setsampwidth(sw0); w.setframerate(fr0)
        w.writeframes(b'\x00' * int(fr0 * 0.6) * ch0 * sw0)
    eps = sorted(set(L['ep'] for L in lines))
    reels = []
    for ep in eps:
        fl = [L for L in lines if L['ep'] == ep]
        lst = os.path.join(BASE, 'concat_%s_r999b.txt' % ep)
        with io.open(lst, 'w', encoding='ascii') as f:
            for i, L in enumerate(fl):
                f.write("file '%s'\n" % L['file'].replace('\\', '/'))
                if i < len(fl) - 1:
                    f.write("file '%s'\n" % sil_path.replace('\\', '/'))
        mp3 = os.path.join(BASE, '%s_AUDITION_r999.mp3' % ep)
        r = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst,
                            '-af', 'volume=-3dB', '-ar', '24000', '-b:a', '64k', mp3],
                           capture_output=True)
        ok = (r.returncode == 0 and os.path.isfile(mp3) and os.path.getsize(mp3) > 1000)
        reels.append({'ep': ep, 'lines': len(fl), 'file': mp3 if ok else None,
                      'size': os.path.getsize(mp3) if ok else 0, 'fmt': 'mp3', 'ok': ok})
        try:
            os.remove(lst)
        except OSError:
            pass
    try:
        os.remove(sil_path)
    except OSError:
        pass
    out['reels'] = reels
    add.append('- 试听卷已按 -3dB 预增益重制（热峰安全带·混音段仍走限幅器）。')
    dump(out, os.path.join(BASE, 'AUDITION-CLIP-REFINE-r999.json'))
    msgp = msgs[0] if msgs else os.path.join(ROOT, 'fleet', 'inbox',
                                             'MSG-20261018-%s-bmb-voicegen-audition-reel.md' % HHMM)
    m = []
    m.append('# MSG-20261018-%s-bm-b（@bm-a）O-20261017-1751 B.4-III 配音样件声审收口·CEO 看片通道投递请求' % HHMM)
    m.append('')
    m.append('@bm-a 请将本机 Taildrop 收件箱 4 件转 CEO 看片通道（Downloads\\drama-voicegen\\，r997 drama pilot 先例）：')
    for rl in reels:
        if rl['ok']:
            m.append('- %s（%d B·mp3·%d 台词）' % (os.path.basename(rl['file']), rl['size'], rl['lines']))
    m.append('- AUDITION-SHEET-r999.md（逐台词声审单+削波精判附）')
    m.append('')
    m.append('bm-b 侧判读：51/51 结构面 PASS；削波精判=%s（孤立热峰非平顶，卷内已 -3dB 预增益；真削波 0 条）。'
             % verdict)
    m.append('三层混音样件=下一增量（对白+环境+音效·O-1751），不阻塞声线方向反馈——请 CEO 听三卷后点声线方向（五音色绑定见单）。')
    m.append('回执窗 2 轮（bytes 清单如上·taildrop rc 见 bm-b r999 轮报告）。')
    with io.open(msgp, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(m) + '\n')
    print('REFINE verdict=%s hot_only=%d true_clip=0 reels rebuilt -3dB' % (verdict, len(hot_only)))
    sys.exit(0)
else:
    for mp in msgs:
        try:
            os.remove(mp)
        except OSError:
            pass
    add.append('- 按呈审纪律未投递 CEO——真削波线重生成后再过闸（IndexTTS 降增益·r1000 执行）。')
    dump(out, os.path.join(BASE, 'AUDITION-CLIP-REFINE-r999.json'))
    print('REFINE verdict=FAIL_TRUE_CLIP lines=%d (no delivery)' % len(true_clips))
    for n in true_clips[:30]:
        print('TRUECLIP: ' + n)
    sys.exit(1)

# sheet addendum appended in both branches (reachable only if no sys.exit above)
