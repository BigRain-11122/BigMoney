# -*- coding: utf-8 -*-
# r538 bm-a: structural assertions for town.html alloc-building alignment (post-edit gate)
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open('town.html', encoding='utf-8').read()
fails = []

def chk(name, cond):
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)

# 1. residual old dept name zero across file
chk('residual-资产组合研究部 == 0', t.count('资产组合研究部') == 0)
# 2. new names present at the 4 expected faces
chk("label:'资产配置研究组' present", "label:'资产配置研究组'" in t)
chk("dept:'组合与资金部 Portfolio & Capital' present", "dept:'组合与资金部 Portfolio & Capital'" in t)
chk('plaque text 资产配置研究组 present', "text('资产配置研究组'" in t)
chk('footer mention present', '资产配置研究组上盘（挂靠组合与资金部 O-2311' in t)
# 3. mandate carries org_chart v2 alignment note + O-2311 anchor
chk('mandate org_chart v2 note', 'org_chart v2 部门表对齐 r538' in t)
# 4. alloc block integrity: id unique + dept/mandate/info triple
chk("id:'alloc' unique", t.count("id:'alloc'") == 1)
chk('drawAlloc defined once', len(re.findall(r'function drawAlloc\s*\(', t)) == 1)
# 5. every dept: now maps to org_chart v2 canonical 10 (11 buildings, alloc now under 组合与资金部)
depts = re.findall(r"dept:'([^']+)'", t)
canon = ['研究部', '策略部', '风控部', '交易部', '组合与资金部', '数据部', 'ETF 操作链条研究组', '舰队部', '总经办', '工程部']
unknown = [d for d in depts if not any(c in d for c in canon)]
chk('all 11 building depts map into org_chart v2 canonical set', len(unknown) == 0)
if unknown:
    print('  unknown depts:', unknown)
chk('building count == 11', len(depts) == 11)

print()
print('RESULT:', 'ALL PASS' if not fails else 'FAILS: %d' % len(fails))
sys.exit(0 if not fails else 1)
