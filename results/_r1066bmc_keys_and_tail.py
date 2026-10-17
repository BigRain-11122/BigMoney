# r1066 bm-c: machine-dump W260 finalize/sixgate/fivekeys scalar keys + live RAM + group ORD tail rows
# (authoring aid for the W261 prereg derive; zero repo mutation beyond results/ scratch)
import json, io, ctypes

out = []

def walk(o, pre=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if isinstance(v, (int, float, str, bool)) and len(str(v)) < 200:
                out.append('%s%s = %r' % (pre, k, v))
            elif isinstance(v, dict) and len(pre) < 40:
                walk(v, pre + str(k) + '.')
            elif isinstance(v, list) and len(str(v)) < 400:
                out.append('%s%s = %r' % (pre, k, v))

for p in [r'results\perpetual_faces\n1_w260_results.json',
          r'results\_r1065bmc_w260_fivekeys.json',
          r'results\_r1065bmc_w260_sixgate.json']:
    out.append('==== FILE %s ====' % p)
    try:
        d = json.load(io.open(p, encoding='utf-8'))
        walk(d)
    except Exception as e:
        out.append('ERR %s: %s' % (p, e))

class MEM(ctypes.Structure):
    _fields_ = [('dwLength', ctypes.c_ulong), ('dwMemoryLoad', ctypes.c_ulong),
                ('ullTotalPhys', ctypes.c_ulonglong), ('ullAvailPhys', ctypes.c_ulonglong),
                ('ullTotalPageFile', ctypes.c_ulonglong), ('ullAvailPageFile', ctypes.c_ulonglong),
                ('ullTotalVirtual', ctypes.c_ulonglong), ('ullAvailVirtual', ctypes.c_ulonglong),
                ('ullAvailExtendedVirtual', ctypes.c_ulonglong)]
m = MEM(); m.dwLength = ctypes.sizeof(MEM)
ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m))
out.append('RAM free GB = %.1f (load %d%%)' % (m.ullAvailPhys / 1e9, m.dwMemoryLoad))

io.open(r'results\_r1066bmc_w260_keys_dump.txt', 'w', encoding='utf-8').write('\n'.join(out))

# group-tree ORD tail: last 15 rows, clean newline join
import subprocess
t = subprocess.run(['git', '-C', r'K:\Fluxgroup\FluxGroup', 'show', 'origin/main:docs/orders.md'],
                   capture_output=True).stdout.decode('utf-8', 'replace')
rows = t.splitlines()
io.open(r'results\_r1066bmc_ord_tail2.txt', 'w', encoding='utf-8').write('\n'.join(rows[-15:]) + '\n')
print('dump lines=%d ord_tail_rows=%d ram_free_gb=%.1f' % (len(out), len(rows[-15:]), m.ullAvailPhys / 1e9))
