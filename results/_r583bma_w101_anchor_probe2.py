# r583 bm-a: probe anchors part 2 (W99 config tail, W99 summary tail, dep pattern)
import subprocess

def show(p):
    return subprocess.run(['git', 'show', 'HEAD:%s' % p], capture_output=True).stdout.decode('utf-8')

n1 = show('scripts/perpetual_faces_n1.py')
i = n1.find('"shard_subdir": "n1_w99"')
print('--- W99 config tail ---')
print(repr(n1[i-80:i+200]))
j = n1.find('law sec.4 W99 row')
print('--- W99 summary tail ---')
print(repr(n1[j-100:j+250]))
# W99 leg cumulative dep pattern (bm-c r374)
k = n1.find('W99 finalize cumulative deps')
if k < 0:
    k = n1.find('cumulative dep')
print('--- W99 dep text ---')
print(repr(n1[k-60:k+400]))
# count anchor uniqueness
print('anchor counts:',
      n1.count('        _set_wave(2)\n    # --- T-141 s2 lane face (SATURATION_ENGINE_LAW sec.2 pre-claim'),
      n1.count('"shard_subdir": "n1_w99"'))
