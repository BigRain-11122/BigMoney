import json

m = json.load(open(r'C:\Fluxgroup\FluxGroup\media\drama-tts-out\r998_ep001_003\MANIFEST-r998.json', encoding='utf-8'))
lines = m['lines']
out = []
for l in lines:
    out.append('%s L%02d | %s | dur=%.2fs shot=%ds | fx=%s | %s' % (
        l['ep'], l['n'], l['speaker'], l['audio_s'], l['shot_dur'],
        l.get('fx', ''), l['text'][:42]))
open(r'results\_r1003bmb_fxtable.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('written', len(out))
