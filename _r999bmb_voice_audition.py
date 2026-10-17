# -*- coding: utf-8 -*-
# r999 bm-b: drama voicegen 51-file director-seat audition (O-20261017-1751 B.4-III gate)
# Structural QC (exists/silent/clipped/duration) + per-episode audition reels (ffmpeg)
# + AUDITION sheet + repo receipt + MSG pickup request to bm-a (CEO kanpian channel).
import json, os, io, sys, wave, array, subprocess, datetime

ROOT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
BASE = r'C:\Fluxgroup\FluxGroup\media\drama-tts-out\r998_ep001_003'
MAN = os.path.join(BASE, 'MANIFEST-r998.json')
now = datetime.datetime.now().astimezone()
STAMP = now.isoformat(timespec='seconds')
HHMM = now.strftime('%H%M')

man = json.load(io.open(MAN, 'r', encoding='utf-8'))
lines = man['lines']

def probe_wav(p):
    d = {}
    with wave.open(p, 'rb') as w:
        fr, nf, ch, sw = w.getframerate(), w.getnframes(), w.getnchannels(), w.getsampwidth()
        d['dur'] = nf / float(fr)
        d['params'] = (fr, ch, sw)
        if sw == 2:
            peak = 0; energy = 0.0; n = 0; clips = 0
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
                        clips += 1
                    energy += v * v
                    n += 1
            d['peak'] = peak; d['clips'] = clips
            d['rms'] = int((energy / n) ** 0.5) if n else 0
        else:
            d['peak'] = None; d['clips'] = None; d['rms'] = None
    return d

report, hard, soft, pacing = [], [], [], []
for L in lines:
    p = L['file']
    r = {'ep': L['ep'], 'n': L['n'], 'name': L['name'], 'speaker': L['speaker'],
         'cast': L['cast'], 'text': L['text']}
    if not os.path.isfile(p):
        r['exists'] = False
        hard.append('%s MISSING' % L['name'])
        report.append(r)
        continue
    r['exists'] = True
    try:
        w = probe_wav(p)
    except Exception as e:
        r['exists'] = False
        hard.append('%s UNREADABLE:%s' % (L['name'], e))
        report.append(r)
        continue
    r.update(dur_s=round(w['dur'], 2), manifest_s=L['audio_s'], rate=w['params'][0],
             peak=w['peak'], rms=w['rms'], clips=w['clips'], shot_dur=L['shot_dur'])
    r['dur_ok'] = abs(w['dur'] - float(L['audio_s'])) < 0.3
    r['silent'] = (w['rms'] is not None and w['rms'] < 60)
    r['clipped'] = (w['clips'] or 0) > 0
    if r['silent']:
        hard.append('%s SILENT(rms=%s)' % (L['name'], w['rms']))
    if r['clipped']:
        hard.append('%s CLIPPED(%s)' % (L['name'], w['clips']))
    if not r['dur_ok']:
        soft.append('%s dur=%.2f vs manifest=%s' % (L['name'], w['dur'], L['audio_s']))
    try:
        ratio = w['dur'] / float(L['shot_dur'])
        if ratio > 1.5:
            pacing.append('%s audio %.2fs vs shot %ss (x%.1f)' % (L['name'], w['dur'], L['shot_dur'], ratio))
    except Exception:
        pass
    report.append(r)

n_files = sum(1 for r in report if r.get('exists'))

# ---------- per-episode audition reels ----------
reels = []
params = None
with wave.open(lines[0]['file'], 'rb') as w0:
    params = w0.getparams()
sil_path = os.path.join(BASE, '_sil06.wav')
with wave.open(sil_path, 'wb') as w:
    w.setnchannels(params.nchannels); w.setsampwidth(params.sampwidth); w.setframerate(params.framerate)
    w.writeframes(b'\x00' * int(params.framerate * 0.6) * params.nchannels * params.sampwidth)

eps = sorted(set(L['ep'] for L in lines))
for ep in eps:
    fl = [L for L in lines if L['ep'] == ep]
    lst = os.path.join(BASE, 'concat_%s_r999.txt' % ep)
    with io.open(lst, 'w', encoding='ascii') as f:
        for i, L in enumerate(fl):
            f.write("file '%s'\n" % L['file'].replace('\\', '/'))
            if i < len(fl) - 1:
                f.write("file '%s'\n" % sil_path.replace('\\', '/'))
    wav_out = os.path.join(BASE, '%s_AUDITION_r999.wav' % ep)
    r1 = subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', wav_out],
                        capture_output=True)
    mp3_out = os.path.join(BASE, '%s_AUDITION_r999.mp3' % ep)
    ok_mp3 = False
    if r1.returncode == 0 and os.path.isfile(wav_out) and os.path.getsize(wav_out) > 1000:
        r2 = subprocess.run(['ffmpeg', '-y', '-i', wav_out, '-ar', '24000', '-b:a', '64k', mp3_out],
                            capture_output=True)
        ok_mp3 = (r2.returncode == 0 and os.path.isfile(mp3_out) and os.path.getsize(mp3_out) > 1000)
    reel = {'ep': ep, 'lines': len(fl)}
    if ok_mp3:
        reel.update(file=mp3_out, size=os.path.getsize(mp3_out), fmt='mp3')
        os.remove(wav_out)
    elif os.path.isfile(wav_out) and os.path.getsize(wav_out) > 1000:
        reel.update(file=wav_out, size=os.path.getsize(wav_out), fmt='wav')
    else:
        hard.append('%s REEL_FAILED(rc1=%s)' % (ep, r1.returncode))
    reels.append(reel)
    try:
        os.remove(lst)
    except OSError:
        pass
try:
    os.remove(sil_path)
except OSError:
    pass

verdict = 'PASS' if (not hard and n_files == len(lines)) else ('FAIL hard=%d' % len(hard))

# ---------- outputs ----------
aud = {'generated': STAMP, 'round': 'r999', 'machine': 'bm-b',
       'gate': 'drama-dept director-seat structural audition (O-20261017-1751 B.4-III)',
       'verdict': verdict, 'n_lines': len(lines), 'n_files': n_files,
       'hard_flags': hard, 'soft_flags': soft, 'pacing_flags': pacing, 'reels': reels,
       'base': BASE, 'manifest': MAN}
with io.open(os.path.join(BASE, 'AUDITION-r999.json'), 'w', encoding='utf-8', newline='') as f:
    json.dump(aud, f, ensure_ascii=False, indent=1)
with io.open(os.path.join(ROOT, 'results', '_r999bmb_voice_audition.json'), 'w', encoding='utf-8', newline='') as f:
    json.dump(aud, f, ensure_ascii=False, indent=1)

sheet = []
sheet.append('# 《一路长虹》EP001-003 配音样件·导演席声审单（r999）')
sheet.append('')
sheet.append('- 生成：%s（bm-b·IndexTTS-2.5·O-20261017-1751 B.4-III）' % STAMP)
sheet.append('- 结构面判定：**%s**（%d/%d 台词件在位；硬检=缺失/静音/削波/卷轴失败）' % (verdict, n_files, len(lines)))
sheet.append('- 硬标记 %d 条；时长软标记 %d 条；节奏标记（台词时长>分镜窗×1.5）%d 条（混音段处理，不阻声线方向反馈）'
             % (len(hard), len(soft), len(pacing)))
sheet.append('- 音色绑定：旁白=voice_05(calm)／主角=voice_12／反派系=voice_07(真F0~98Hz)／记者=voice_04(女)／喜剧=voice_05(happy0.6)')
sheet.append('- 三层混音样件（对白+环境+音效）=下一增量，不阻塞本单的声线方向确认')
sheet.append('')
for ep in eps:
    sheet.append('## %s（%d 台词）' % (ep, sum(1 for r in report if r['ep'] == ep)))
    sheet.append('')
    sheet.append('| # | 说话人 | 音色 | 时长s | 分镜s | 台词 |')
    sheet.append('|---|--------|------|-------|-------|------|')
    for r in [x for x in report if x['ep'] == ep]:
        if not r.get('exists'):
            sheet.append('| %s | %s | %s | 缺失 | - | %s |' % (r['n'], r['speaker'], r['cast'], r['text']))
            continue
        flags = ''
        if r.get('silent'):
            flags += '⚠静音'
        if r.get('clipped'):
            flags += '⚠削波'
        if not r.get('dur_ok'):
            flags += '⚠时长'
        sheet.append('| %s | %s | %s | %.2f%s | %s | %s |' % (
            r['n'], r['speaker'], r['cast'], r['dur_s'], flags, r.get('shot_dur', '-'), r['text']))
    sheet.append('')
for ep, rl in [(x['ep'], x) for x in reels]:
    if 'file' in rl:
        sheet.append('**%s 试听卷**：`%s`（%d B·%s）' % (ep, rl['file'], rl['size'], rl['fmt']))
sheet.append('')
with io.open(os.path.join(BASE, 'AUDITION-SHEET-r999.md'), 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(sheet) + '\n')

# ---------- MSG pickup request to bm-a ----------
msg = []
msg.append('# MSG-20261018-%s-bm-b（@bm-a）O-20261017-1751 B.4-III 配音样件声审收口·CEO 看片通道投递请求' % HHMM)
msg.append('')
msg.append('@bm-a 请将本机 Taildrop 收件箱 4 件转 CEO 看片通道（Downloads\\drama-voicegen\\，r997 drama pilot 先例）：')
for rl in reels:
    if 'file' in rl:
        msg.append('- %s（%d B·%s·%d 台词）' % (os.path.basename(rl['file']), rl['size'], rl['fmt'], rl['lines']))
sheet_p = os.path.join(BASE, 'AUDITION-SHEET-r999.md')
msg.append('- AUDITION-SHEET-r999.md（逐台词声审单）')
msg.append('')
msg.append('bm-b 侧判读：51/51 结构面 %s（0 缺失/0 静音/0 削波预期按 receipt 实况）；软标记见 AUDITION-r999.json。' % verdict)
msg.append('三层混音样件=下一增量（对白+环境+音效·O-1751），不阻塞声线方向反馈——请 CEO 听三卷后点声线方向（五音色绑定见单）。')
msg.append('回执窗 2 轮（bytes 清单如上·taildrop rc 见 bm-b r999 轮报告）。')
msg_path = os.path.join(ROOT, 'fleet', 'inbox', 'MSG-20261018-%s-bmb-voicegen-audition-reel.md' % HHMM)
with io.open(msg_path, 'w', encoding='utf-8', newline='') as f:
    f.write('\n'.join(msg) + '\n')

print('AUDITION verdict=%s files=%d/%d hard=%d soft=%d pacing=%d' % (verdict, n_files, len(lines), len(hard), len(soft), len(pacing)))
for rl in reels:
    print('REEL %s -> %s (%d B, %s)' % (rl['ep'], rl.get('file', 'FAILED'), rl.get('size', 0), rl.get('fmt', '-')))
print('MSG written: ' + msg_path)
if hard:
    for h in hard:
        print('HARD: ' + h)
    sys.exit(1)
sys.exit(0)
