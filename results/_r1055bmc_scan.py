# -*- coding: utf-8 -*-
# r1055 bm-c: pre-clone token census of the W253 derive editor (band-space,
# wave-number space, and unknown-face inventory) -- read-only.
import io, os, re, collections

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(REPO, "results", "_w253bmc_derive_editor.py")
t = io.open(SRC, encoding="utf-8").read()

# band-space underscore tokens 5NN_NNN
band_u = collections.Counter(re.findall(r"\b5[0-9]{2}_[0-9]{3}\b", t))
# band-space compressed tokens 5NNNNN (6 contiguous digits, not preceded by digit/dot)
band_c = collections.Counter(re.findall(r"(?<![\d.])5[0-9]{5}(?![\d.])", t))
# wave-number tokens 2NN (standalone-ish)
wave = collections.Counter(re.findall(r"\b2[0-9]{2}\b", t))

print("BAND_UNDERSCORE:")
for k, v in sorted(band_u.items()):
    print(f"  {k} x{v}")
print("BAND_COMPRESSED:")
for k, v in sorted(band_c.items()):
    print(f"  {k} x{v}")
print("WAVE_TOKENS:")
for k, v in sorted(wave.items()):
    print(f"  {k} x{v}")
print("LEN", len(t))
