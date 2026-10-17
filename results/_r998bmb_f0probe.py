# -*- coding: utf-8 -*-
# r998: F0 probe of IndexTTS example prompt voices -> male/female classification
# for drama-001 pilot zero-shot casting (PILOT-001-PLAN: zero-shot refs, formal voice lib not built).
import os, json, io
import numpy as np
import soundfile as sf

REPO = r'C:\Fluxgroup\FluxGroup\media\drama-tools\repos\index-tts'
EX = os.path.join(REPO, 'examples')
OUT = r'C:\Fluxgroup\FluxGroup\quant\bigmoney\results\_r998bmb_f0probe.json'


def median_f0(path, sr_target=16000):
    """Robust median F0 via autocorrelation on 3 voiced frames (200ms windows)."""
    try:
        wav, sr = sf.read(path)
    except Exception:
        try:
            import wave
            with wave.open(path) as w:
                sr = w.getframerate()
                wav = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float32) / 32768.0
        except Exception:
            return None, None
    if wav.ndim > 1:
        wav = wav.mean(axis=1)
    if sr != sr_target:
        import numpy as np
        n = int(len(wav) * sr_target / sr)
        wav = np.interp(np.linspace(0, len(wav) - 1, n), np.arange(len(wav)), wav)
        sr = sr_target
    # energy-based frame selection: pick top-energy 200ms frames
    fl = int(0.2 * sr)
    hop = fl // 2
    frames = []
    energies = []
    for st in range(0, max(1, len(wav) - fl), hop):
        seg = wav[st:st + fl]
        e = float(np.sqrt((seg ** 2).mean()))
        if e > 1e-4:
            frames.append(seg)
            energies.append(e)
    if not frames:
        return None, 0.0
    order = sorted(range(len(frames)), key=lambda i: -energies[i])[:6]
    f0s = []
    fmin, fmax = 70.0, 400.0
    lmin, lmax = int(sr / fmax), int(sr / fmin)
    for i in order:
        seg = frames[i]
        seg = seg - seg.mean()
        ac = np.correlate(seg, seg, 'full')[len(seg) - 1:]
        ac = ac / (ac[0] + 1e-9)
        peak, pk = 0.0, -1
        for lag in range(lmin, min(lmax, len(ac))):
            if ac[lag] > peak and ac[lag] > 0.3:
                peak, pk = ac[lag], lag
        if pk > 0:
            f0s.append(sr / pk)
    if not f0s:
        return None, float(np.mean(energies))
    return float(np.median(f0s)), float(np.mean(energies))


def main():
    rows = []
    for fn in sorted(os.listdir(EX)):
        if not fn.endswith('.wav'):
            continue
        f0, e = median_f0(os.path.join(EX, fn))
        if f0 is None:
            cls = 'unknown'
        elif f0 < 160:
            cls = 'male_low' if f0 < 120 else 'male'
        elif f0 < 200:
            cls = 'male_high_or_female_low'
        else:
            cls = 'female'
        rows.append({'file': fn, 'f0_median': f0, 'energy': e, 'class': cls})
    with io.open(OUT, 'w', encoding='utf-8') as f:
        json.dump(rows, f, ensure_ascii=True, indent=1)
    for r in rows:
        print('%-16s f0=%6.1f %-24s %s' % (r['file'], r['f0_median'] or -1, r['class'], ''))


if __name__ == '__main__':
    main()
