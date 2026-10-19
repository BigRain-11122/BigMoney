# -*- coding: utf-8 -*-
"""ST-010 DSP helper (venv-executed by pitch_tier_test_synth.py).

argv: <in_wav> <out_wav> <n_steps>
- mono-ize via soundfile; librosa.pitch_shift(n_steps); RMS re-match to the
  pre-shift RMS (ST-009 honest-limit item: loudness re-match required after
  DSP shift at the synthesis station); write PCM_16 at the input sr.
- n_steps=0 = deterministic passthrough (uniform RMS-report path).
- Prints one JSON line: {pre_rms, post_rms, scale, sr, dur, n_steps}.
Honest disclosure (fixes ST-009 wording): librosa pitch_shift is a
phase-vocoder + resampling shift -- formants move with F0 (not strictly
formant-preserving); within +/-3 st this is the accepted safe zone.
"""
import json
import sys

import numpy as np
import soundfile as sf
import librosa

# librosa 0.10.x exposes pitch_shift under effects (top-level promotion landed
# later); resolve both faces, version-robust.
_pitch_shift = getattr(librosa, 'pitch_shift', None) or librosa.effects.pitch_shift


def main():
    in_wav, out_wav, n_steps = sys.argv[1], sys.argv[2], int(sys.argv[3])
    d, sr = sf.read(in_wav, dtype='float64', always_2d=True)
    y = d.mean(axis=1)
    pre_rms = float(np.sqrt(np.mean(y ** 2)))
    if n_steps == 0:
        y2 = y.copy()
        scale = 1.0
    else:
        y2 = _pitch_shift(y, sr=sr, n_steps=n_steps)
        post = float(np.sqrt(np.mean(y2 ** 2)))
        scale = (pre_rms / post) if post > 1e-12 else 1.0
        y2 = np.clip(y2 * scale, -1.0, 1.0)
    post_rms = float(np.sqrt(np.mean(y2 ** 2)))
    sf.write(out_wav, y2.astype('float32'), sr, subtype='PCM_16')
    print(json.dumps({'pre_rms': round(pre_rms, 6),
                      'post_rms': round(post_rms, 6),
                      'scale': round(scale, 4), 'sr': sr,
                      'dur_s': round(len(y2) / float(sr), 3),
                      'n_steps': n_steps}))


if __name__ == '__main__':
    main()
