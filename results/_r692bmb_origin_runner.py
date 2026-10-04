# r692 bm-b probe4: origin runner version check (wait_min cap + RAM gate flush) via subprocess raw bytes
import subprocess, re, json

r = subprocess.run(['git', 'show', 'origin/main:scripts/perpetual_faces_n2.py'], capture_output=True)
assert r.returncode == 0, r.stderr[:200]
src = r.stdout.decode('utf-8')
out = {'origin_wait_min': [], 'has_ram_gate_flush': 'RAM-GATE' in src, 'len': len(src)}
for m in re.finditer(r'wait_min\s*=\s*(\d+)', src):
    out['origin_wait_min'].append(m.group(1))
# local version comparison
loc = open('scripts/perpetual_faces_n2.py', encoding='utf-8').read()
out['local_wait_min'] = re.findall(r'wait_min\s*=\s*(\d+)', loc)
out['local_len'] = len(loc)
out['identical'] = (src == loc)
with open('results/_r692bmb_origin_runner.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False))
