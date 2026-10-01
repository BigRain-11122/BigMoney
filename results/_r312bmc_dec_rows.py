import subprocess, io, sys
raw = subprocess.check_output(['git','-C','K:/Fluxgroup/FluxGroup','show','origin/main:docs/decisions.md'])
text = raw.decode('utf-8')
lines = text.splitlines()
out = []
capture = False
for l in lines:
    keep = ('2026-10-01' in l and ('09:' in l or '10:' in l or '11:' in l or '12:' in l)) or ('09-30' in l and ('2' in l))
    if keep:
        capture = True
    if capture:
        out.append(l)
open('K:/Fluxgroup/FluxGroup/quant/bigmoney/results/_r312bmc_dec_rows.txt','w',encoding='utf-8').write('\n'.join(out[-400:]))
print('ROWS_FILE_WRITTEN lines=' + str(len(out[-400:])))
print('TOTAL_DEC_LINES=' + str(len(lines)))
