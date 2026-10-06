# r790 bm-a W163 finalize pre-flight: r708 double-probe (live-process file check)
# Probe 1: mtime stability window (45s, all 12 shards byte-static)
# Probe 2: live python process command-line scan (no n1/p2cal/shard writer alive)
# Probe 3 (bonus): saturation engine active_burns already confirmed [] at 18:59 status
import glob, os, subprocess, time, json, hashlib

SHARDS = sorted(glob.glob(r'results/p2cal_ext/n1_w163/shard-*.json'))
assert len(SHARDS) == 12, f'expected 12 shards, found {len(SHARDS)}'

def snap():
    out = {}
    for f in SHARDS:
        st = os.stat(f)
        out[f] = (st.st_mtime_ns, st.st_size, hashlib.sha256(open(f, 'rb').read()).hexdigest())
    return out

s1 = snap()
time.sleep(45)
s2 = snap()
probe1 = (s1 == s2)

# Probe 2: any live python process whose command line references the n1 runner / shard path?
r = subprocess.run(['powershell', '-NoProfile', '-Command',
                    "Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | "
                    "Select-Object -ExpandProperty CommandLine"],
                   capture_output=True, text=True)
writers = [l for l in r.stdout.splitlines()
           if l and ('perpetual_faces_n1' in l or 'n1_w163' in l or 'p2cal_ext' in l)]
probe2 = (len(writers) == 0)

receipt = {
    'round': 'r790', 'wave': 163, 'law': 'r708 double-probe',
    'probe1_mtime_stability_45s': probe1,
    'probe2_no_live_writer_process': probe2,
    'shard_count': len(SHARDS),
    'shard_sizes': {os.path.basename(f): s2[f][1] for f in SHARDS},
    'verdict': 'GREEN' if (probe1 and probe2) else 'RED',
}
open(r'results/_r790bma_w163_preflight.json', 'w', encoding='utf-8').write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print(json.dumps(receipt, indent=1)[:800])
