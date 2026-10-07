import subprocess, re
for p in ['results/saturation_engine/face_bm-a.json', 'results/saturation_engine/state_bm-a.json',
          'results/saturation_engine/history_bm-a.jsonl']:
    for stage, side in [(2, 'bm-c-base'), (3, 'mine')]:
        r = subprocess.run(['git', 'show', f':{stage}:{p}'], capture_output=True)
        t = r.stdout.decode('utf-8', errors='replace')
        m = re.search(r'"ts"\s*:\s*"([^"]+)"', t)
        print(p, side, m.group(1) if m else f'no-ts bytes={len(t)}')
