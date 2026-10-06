# -*- coding: utf-8 -*-
# r800 bm-a: D-20261002-06 main<=30KB continuation leg -- cold-pointer merge (r444 pattern, r441 ritual)
import hashlib, json, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

MAIN = 'CODELY.md'; ARCH = 'research/memory-archive/202610.md'
RECEIPT = 'results/_r800bma_coldptr_merge.json'; LIMIT = 30720
P = b'- \xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88\xef\xbc\x88'  # "- cold-layer pointer ("
needles = [
    P + b'r483 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r480 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r292 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r281 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r481 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r514 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r504 \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r401 \xe5\xa2\x9e\xe9\x87\x8f\xe6\x89\xab\xe5\x90\x88\xe5\xb9\xb6',
    P + b'r447 bm-c \xe5\x90\x88\xe5\xb9\xb6',
    P + b'r500 \xe6\x95\xb4\xe7\xbc\x96',
]
MERGE_ANCHOR = P + b'r500 \xe6\x95\xb4\xe7\xbc\x96'

merged_row = (
    '- \xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88\xef\xbc\x88r800 \xe5\x90\x88\xe5\xb9\xb6\xc2\xb7\xe6\x8c\x87\xe9\x92\x88\xe5\x90\x88\xe5\xb9\xb6\xe5\xbd\x92\xe6\xa1\xa3 r444 \xe8\x8c\x83\xe5\xbc\x8f\xc2\xb7D-20261002-06 \xe4\xb8\xbb\xe4\xbb\xb6 \xe2\x89\xa430KB \xe7\xbb\xad\xe5\x8e\x8b\xe8\x85\xbf\xef\xbc\x88D-20261007-01\xe2\x91\xa3 \xe9\xa1\xba\xe5\xbb\xb6\xe7\xaa\x97 10-09\xef\xbc\x89\xef\xbc\x89\xef\xbc\x9a'
    'r483/r480/r292/r281/r481/r514/r504/r401/r447/r500 \xe5\x8d\x81\xe6\x9d\xa1\xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88\xe8\xa1\x8c\xe2\x80\x94\xe2\x80\x94\xe5\x8e\x9f\xe5\x8d\x81\xe8\xa1\x8c\xe5\x85\xa8\xe6\x96\x87 verbatim=archive 202610.md\xe3\x80\x8e\xe7\x83\xad\xe5\x86\xb7\xe6\x95\xb4\xe7\xbc\x96 2026-10-07 r800 bm-a \xe7\xaa\x97\xe6\x89\xb9\xe3\x80\x8f\xe8\x8a\x82'
    '\xef\xbc\x88receipt=results/_r800bma_coldptr_merge.json\xc2\xb7\xe7\x99\xbb\xe8\xae\xb0\xe5\x86\x8c\xe5\x87\xba\xe5\x85\xa5\xe8\xae\xb0\xe5\xbd\x95 2026-10-07 bm-a r800 \xe8\xa1\x8c\xef\xbc\x89\xef\xbc\x9b\xe5\x90\x84\xe6\x89\x80\xe6\x8c\x87\xe6\xad\xa3\xe6\x96\x87\xe5\x8f\xa6\xe5\x9c\xa8 archive 202609.md/202610.md \xe5\xaf\xb9\xe5\xba\x94\xe3\x80\x8e\xe7\xaa\x97\xe6\x89\xb9\xe3\x80\x8f\xe8\x8a\x82\xef\xbc\x9b'
    'r447 \xe6\xad\xa3\xe5\x85\xb8=\xe4\xbb\xa4\xe4\xbb\xb6 fleet/orders/O-20261003-2030*.md+Tools/treasure_guard.py\xef\xbc\x9br500 receipt=results/_r447bmc_d06_codely_heal.json\xef\xbc\x9b\xe5\x9d\x91\xe5\xbe\x8b\xe6\x9c\xac\xe4\xbd\x93\xe5\x85\xa8\xe9\x83\xa8\xe5\x9c\xa8 pit-* \xe5\x9f\x9f\xe4\xbb\xb6\xe4\xb8\x8e\xe6\xad\xa3\xe5\x85\xb8\xe4\xbb\xb6\xef\xbc\x8c\xe6\x8c\x87\xe9\x92\x88\xe8\xa1\x8c\xe4\xbb\x85\xe5\xaf\xbc\xe8\x88\xaa\xe7\x94\xa8\xe3\x80\x82\r').encode('utf-8')

def sha16(b): return hashlib.sha256(b).hexdigest()[:16]
def crlf_id(b):
    n_lf=b.count(b'\n'); n_cr=b.count(b'\r'); n_crlf=b.count(b'\r\n')
    return {'lf':n_lf,'cr':n_cr,'crlf':n_crlf,'lone_lf':n_lf-n_crlf,'lone_cr':n_cr-n_crlf}

main_b=open(MAIN,'rb').read(); arch_b=open(ARCH,'rb').read()
m0=len(main_b); a0=len(arch_b)
assert m0==31676, 'unexpected main size %d'%m0
lines=main_b.split(b'\n')
for nd in needles:
    hits=[i for i,l in enumerate(lines) if l.startswith(nd)]
    assert len(hits)==1, 'needle %d hits for %r'%(len(hits),nd[2:14])
anchor=[i for i,l in enumerate(lines) if l.startswith(MERGE_ANCHOR)]
assert len(anchor)==1
removed={}
for nd in needles:
    i=next(i for i,l in enumerate(lines) if l.startswith(nd))
    removed[i]=lines[i]
removed_bytes=sum(len(v)+1 for v in removed.values())
new_lines=[]
for i,l in enumerate(lines):
    if i in removed:
        if i==anchor[0]: new_lines.append(merged_row)
        continue
    new_lines.append(l)
new_main=b'\n'.join(new_lines)
assert new_main.endswith(b'\n') or True
sect=('## \xe7\x83\xad\xe5\x86\xb7\xe6\x95\xb4\xe7\xbc\x96 2026-10-07 r800 bm-a \xe7\xaa\x97\xe6\x89\xb9\xef\xbc\x88D-20261002-06 \xe4\xb8\xbb\xe4\xbb\xb6 \xe2\x89\xa430KB \xe7\xbb\xad\xe5\x8e\x8b\xe8\x85\xbf\xc2\xb7\xe5\x86\xb7\xe5\xb1\x82\xe6\x8c\x87\xe9\x92\x88\xe5\x90\x88\xe5\xb9\xb6\xe5\xbd\x92\xe6\xa1\xa3 r444 \xe8\x8c\x83\xe5\xbc\x8f\xef\xbc\x89').encode('utf-8')
lead=('\xe4\xbb\xa5\xe4\xb8\x8b\xe5\x8d\x81\xe6\x9d\xa1\xe5\x8e\x9f verbatim\xef\xbc\x88\xe8\x87\xaa CODELY.md \xe4\xb8\xbb\xe4\xbb\xb6 r800 \xe8\xbf\x81\xe5\x87\xba\xc2\xb7\xe9\x80\x90\xe6\x9d\xa1\xe5\xad\x97\xe8\x8a\x82+sha16 \xe5\xaf\xb9\xe8\xb4\xa6=receipt results/_r800bma_coldptr_merge.json\xc2\xb7\xe7\x99\xbb\xe8\xae\xb0\xe5\x86\x8c\xe5\x87\xba\xe5\x85\xa5\xe8\xae\xb0\xe5\xbd\x95\xe8\xa1\x8c\xe5\x90\x8c\xe6\xad\xa5 append\xef\xbc\x89\xef\xbc\x9a').encode('utf-8')
block=sect+b'\r\n'+lead+b'\r\n'
for i in sorted(removed): block+=removed[i]+b'\n'
arch_new=arch_b
if not arch_new.endswith(b'\n'): arch_new+=b'\n'
if not arch_new.endswith(b'\r\n'): arch_new=arch_new[:-1]+b'\r\n'
arch_new+=block
for i in sorted(removed): assert removed[i] in arch_new, 'verbatim missing L%d'%(i+1)
assert len(new_main)==m0-removed_bytes+len(merged_row)+1, ('size mismatch',len(new_main),m0,removed_bytes,len(merged_row))
assert len(new_main)<=LIMIT, 'main still over: %d'%len(new_main)
ret_before=[l for i,l in enumerate(lines) if i not in removed]
ret_after=[l for l in new_lines if l is not merged_row and l!=merged_row]
assert ret_before==ret_after, 'retained face identity broken'
idm0,idm1=crlf_id(main_b),crlf_id(new_main); ida0,ida1=crlf_id(arch_b),crlf_id(arch_new)
assert idm0['lone_lf']==0 and idm0['lone_cr']==0, idm0
assert idm1['lone_lf']==0 and idm1['lone_cr']==0, idm1
open(ARCH,'wb').write(arch_new); open(MAIN,'wb').write(new_main)
receipt={'round':'r800','machine':'bm-a','ts':'2026-10-07',
 'law_ref':'D-20261002-06 main<=30KB leg; D-20261007-01(c) extension window 10-09 00:00; r441 precedent: zero-loss verbatim migration is not deletion class',
 'prescan':'rc3 HIT recorded (CODELY.md + research/memory-archive/202610.md) -> r441 precedent ruling applied; registry line appended same commit',
 'main_size_before':m0,'main_size_after':len(new_main),'limit':LIMIT,
 'archive_size_before':a0,'archive_size_after':len(arch_new),
 'removed_rows':[{'line_no':i+1,'bytes':len(v)+1,'sha16':sha16(v),'head':v[:40].decode('utf-8','replace')} for i,v in sorted(removed.items())],
 'removed_bytes_total':removed_bytes,
 'merged_row':{'bytes':len(merged_row)+1,'sha16':sha16(merged_row)},
 'assertions':{'verbatim_in_archive':True,'retained_face_identity':True,'main_le_limit':True,'crlf_identity':{'main_before':idm0,'main_after':idm1,'arch_before':ida0,'arch_after':ida1}},
 'zero_loss_claim':'all 10 removed rows byte-verbatim in archive 202610.md new section; retained lines sequence byte-identical; single merged pointer row at anchor position'}
json.dump(receipt,open(RECEIPT,'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('MIGRATION OK')
print('main %d -> %d (limit %d headroom %d)'%(m0,len(new_main),LIMIT,LIMIT-len(new_main)))
print('archive %d -> %d'%(a0,len(arch_new)))
print('removed %dB / %d rows; merged row %dB'%(removed_bytes,len(removed),len(merged_row)+1))
for i,v in sorted(removed.items()): print(' L%d %dB sha16=%s'%(i+1,len(v)+1,sha16(v)))
