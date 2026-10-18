# r1054 probe2: W267/W268 seat chain + inbox msgs full
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'

def gshow(path, ref='origin/main'):
    p = subprocess.run(['git','-C',REPO,'show',ref+':'+path],capture_output=True)
    return p.stdout if p.returncode==0 else b''

out = {}
p = subprocess.run(['git','-C',REPO,'ls-tree','-r','--name-only','origin/main'],capture_output=True)
tree = p.stdout.decode('utf-8','replace').splitlines()
out['w266_faces'] = [t for t in tree if 'w266' in t.lower()][-15:]
out['w267_faces'] = [t for t in tree if 'w267' in t.lower()][-15:]
out['w266_finalize'] = any('n1_w266_results' in t for t in tree)

# find W267 prereg file path (research/prereg family)
w267_prereg = [t for t in tree if 'w267' in t.lower() and ('prereg' in t.lower() or 'PREREG' in t)]
out['w267_prereg_paths'] = w267_prereg

# read W267 prereg sec.5 item5 + sec.7/8 (owner naming) from the first prereg file
for path in w267_prereg[:1]:
    txt = gshow(path).decode('utf-8','replace')
    lines = txt.splitlines()
    keep = []
    grab = False
    for i,l in enumerate(lines):
        low = l.lower()
        if low.startswith('## 5') or low.startswith('### 5') or low.startswith('## 7') or low.startswith('### 7') or low.startswith('## 8') or low.startswith('### 8'):
            grab = True
        elif low.startswith('## ') and grab:
            grab = False
        if grab:
            keep.append(l)
    out['w267_prereg_secs'] = keep[:60]

# W266 finalize results head (owner naming face)
for path in [t for t in tree if 'n1_w266_results' in t][:1]:
    txt = gshow(path).decode('utf-8','replace')
    out['w266_results_head'] = txt[:900]

# seat MSGs mentioning W267/W268 in inbox+processed
seat = [t for t in tree if t.startswith('fleet/inbox/') and ('w267' in t.lower() or 'w268' in t.lower() or 'seat' in t.lower())]
out['seat_msgs'] = seat
for path in seat[-2:]:
    txt = gshow(path).decode('utf-8','replace')
    out['seat_msg_'+path.split('/')[-1][:40]] = txt[:1200]

# three inbox msgs for bm-a
for f in ('MSG-20261018-0845-bmb-audition-redrop-mixsample.md',
          'MSG-20261018-1035-bmb-rootfix.md',
          'MSG-20261018-1137-bmb-canon-installed.md'):
    b = gshow('fleet/inbox/'+f)
    txt = b.decode('utf-8','replace') if b else 'ABSENT'
    out[f[:50]] = txt[:900]

# heartbeat + watermark_red local state
try:
    j = json.load(open(r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results\watermark_red.json',encoding='utf-8'))
    out['watermark_red'] = {k:j.get(k) for k in ('red','reason','ts')}
except Exception as e:
    out['watermark_red'] = {'err': repr(e)[:150]}

print(json.dumps(out, ensure_ascii=False, indent=1)[:7000])
