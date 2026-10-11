# -*- coding: utf-8 -*-
import subprocess
out = subprocess.run([r"C:\Program Files\Git\cmd\git.exe", "show",
                      "origin/main:scripts/perpetual_faces_n1.py"],
                     capture_output=True).stdout.decode("utf-8")

def find(s):
    return out.find(s)

i = find('207: {"batch"')
j = find('208: {"batch"')
blk = out[i:j]
print("--- W207 cfg entry first 16 lines:")
for line in blk.splitlines()[:16]:
    print(repr(line[:120]))

print()
i2 = find('209: {"batch"')
j2 = find('PREREG = WAVE_CONFIGS[2]')
blk2 = out[i2:j2]
print("--- W209 cfg entry last 8 lines before close:")
for line in blk2.splitlines()[-8:]:
    print(repr(line[:120]))

print()
print("close anchor ctx:", repr(out[j2-40:j2+40]))

print()
print("W209 cfg a_seed_base line:")
for line in blk2.splitlines():
    if "a_seed_base" in line or "b_exit_seed_base" in line or "shard_subdir" in line or "engine_owner" in line:
        print(repr(line[:140]))

print()
print("W210 cfg presence:", find('210: {"batch"') > 0)
print("W210 prereg key presence:", find('"prereg": ("research/PERPETUAL_N1_W210_PREREG.md') > 0)
print("universal PRE line count:", out.count('"pre-run; design = frozen v1 null calibration verbatim, "'))
