"""r1001 bm-a: calibrate W243 prereg count gates against the frozen W242 template
(machine-count every gate family before writing the derive script -- zero hand-counting)."""
import json
import subprocess

r = subprocess.run(['git', 'log', '--diff-filter=A', '--format=%H', '--',
                    'research/PERPETUAL_N1_W242_PREREG.md'], capture_output=True)
tpl_sha = r.stdout.decode().strip().splitlines()[0]
tpl = subprocess.run(['git', 'show', tpl_sha + ':research/PERPETUAL_N1_W242_PREREG.md'],
                    capture_output=True).stdout.decode('utf-8')

pats = {
    '_w241bmc': 1, '_w241bmc_freeze_edits.py': 1,
    'n1_w240_results.json': None, 'n1_w241_results.json': None, 'n1_w242_results.json': None,
    'PERPETUAL-N1-W242': None, 'PERPETUAL_N1_W242': None, 'n1_w242/shard': None,
    '549_501..551_500': None, '541_204..541_403': None,
    'fourth consecutive': None, '连续第三个 seed-gap': None,
    '551_501..553_500': None, '541_501..541_700': None,
    '138a94745': None, '1814-bma': None, '第 124 枚': None,
    '954,535': None, '952,335': None, '950,135': None, '945,189': None,
    '549501': None, '541204': None,
    'owner rows 231': None, 'engine_owner 行 231': None,
    '238 行': None, '239 行': None,
    'W2..W241': None, 'W1..W241': None, 'v2..W241': None, 'W5..W241': None,
    '17:3x': None, '19:5x': None,
    '第 232 波': None, '池第 240 枚': None,
    'parity 100 行': None, '共二百三十九面': None, '二百三十九行': None,
    '530,320 投影': None, '528,120+2,200': None,
    'W242-inherit': None,
    '_w242bma': None,
    '2107-bma': None, '6207e60e9': None,  # must be 0 in template
    'engine_owner==bm-a 123': None,
    '17.6GB': None,
    '本机 bm-c 实例': None,
    '240 行': None, 'W2..W242': None, 'W1..W242': None,
}
out = {}
for p in pats:
    out[p] = tpl.count(p)
print(json.dumps({'tpl_sha': tpl_sha, 'counts': out}, ensure_ascii=False, indent=1))
# locate the 4th W2..W241 occurrence context
import re
idxs = [m.start() for m in re.finditer(re.escape('W2..W241'), tpl)]
for i in idxs:
    print('CTX:', tpl[max(0, i - 60):i + 40].replace('\n', ' | '))
