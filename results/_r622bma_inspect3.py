import io, subprocess

def origin_text(path):
    return subprocess.run(['git', 'show', 'origin/main:'+path], capture_output=True).stdout.decode('utf-8')

ob = origin_text('results/runnable_pool.json')
i = ob.find('"id": "FUND-DIVLOWVOL-P1-CELL-DIVLOWVOLYIELDVOL-X1"')
# find entry start: walk back to the line start of '{'
ls = ob.rfind('{', 0, i)
# entry end: find the matching close via next '"id"' or end-of-entries; crude: find '"workers_plan"' then extend
print('==== ORIGIN X1 shard block:')
j = ob.find('"fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1"')
print(ob[j-20:j+520])

src = io.open('results/runnable_pool.json', encoding='utf-8', newline='').read()
print('==== LOCAL X1 entry status + shard block:')
k = src.find('"id": "FUND-DIVLOWVOL-P1-CELL-DIVLOWVOLYIELDVOL-X1"')
# entry status line follows the id/ticket lines; search forward for '"status"' before "shards"
m = src.find('"shards"', k)
entry_head = src[k:m]
st = entry_head.find('"status"')
print('entry status snippet:', entry_head[st:st+40])
j2 = src.find('"fund-divlowvol-p1-cell-divlowvolyieldvol-x1-0of1"')
print(src[j2-20:j2+520])

# origin x2/value-nulls/quality-nulls owner pairs for reference
for sid, nm in (('fund-divlowvol-p1-cell-divlowvolyieldvol-x2-0of1','x2'),
                ('fund-value-p1-nulls-0of1','value-nulls'),
                ('fund-quality-p1-nulls-0of1','quality-nulls')):
    jj = ob.find('"'+sid+'"')
    seg = ob[jj:jj+560]
    print('==== ORIGIN', nm, ':')
    print(seg)
