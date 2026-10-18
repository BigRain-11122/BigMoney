# r1054 probe3: W267 seat MSG + 3 inbox msgs + prereg owner naming (tight)
import subprocess, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
REPO = r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney'
def gshow(path):
    p = subprocess.run(['git','-C',REPO,'show','origin/main:'+path],capture_output=True)
    return p.stdout.decode('utf-8','replace') if p.returncode==0 else None
out = {}
# seat MSG W267
t = gshow('fleet/inbox/processed/MSG-20261018-1025-bmc-w267-seat.md')
out['seat_w267'] = (t or 'ABSENT')[:1500]
# 3 inbox msgs
for f in ('MSG-20261018-0845-bmb-audition-redrop-mixsample.md',
          'MSG-20261018-1035-bmb-rootfix.md',
          'MSG-20261018-1137-bmb-canon-installed.md'):
    t = gshow('fleet/inbox/'+f)
    out[f] = (t or 'ABSENT')[:1000]
# prereg: lines mentioning W268 / owner / item5 / expected bands
t = gshow('research/PERPETUAL_N1_W267_PREREG.md') or ''
lines = t.splitlines()
out['prereg_len'] = len(lines)
out['prereg_owner_lines'] = [l for l in lines if 'W268' in l or 'owner' in l.lower() or 'next' in l.lower()][:12]
out['prereg_band_lines'] = [l for l in lines if '604' in l or 'band' in l.lower() or 'item5' in l.lower() or '602' in l][:12]
print(json.dumps(out, ensure_ascii=False, indent=1)[:5500])
