# -*- coding: utf-8 -*-
# r592 bm-b: town.html alloc-building v5-canon restoration gate
# r538 (bm-a) re-anchored alloc under 组合与资金部 citing a "v6 ten-dept regroup r277"
# that does not exist in org_chart history (git log -S 十部门 = 0 hits; 新立第八部门
# intact since dc8991115). This gate asserts the restored v5-independent mapping and
# cross-checks the org_chart canon source lines.
import re, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

t = open('town.html', encoding='utf-8').read()
o = open('firm/org_chart.md', encoding='utf-8').read()
fails = []

def chk(name, cond):
    print(('PASS ' if cond else 'FAIL ') + name)
    if not cond:
        fails.append(name)

# 1. wrong r538 terms purged
chk("residual-资产配置研究组 == 0", t.count('资产配置研究组') == 0)
chk('residual-挂靠组合与资金部 == 0', t.count('挂靠组合与资金部') == 0)
chk('residual-r538-basis-note == 0', t.count('org_chart v2 部门表对齐 r538') == 0)

# 2. restored v5 faces present
chk("label:'资产组合研究部' present", "label:'资产组合研究部'" in t)
chk("dept:'资产组合研究部 Asset Allocation Research' present", "dept:'资产组合研究部 Asset Allocation Research'" in t)
chk('plaque text 资产组合研究部 present', "text('资产组合研究部'" in t)
chk('footer v5 mention present', '资产组合研究部上盘（org_chart v5 八部门对齐' in t)
chk('mandate v5 independence note', 'org_chart v5 独立成行' in t)

# 3. org_chart canon source lines intact (independence + visualization mapping)
chk('org_chart: 新立第八部门 declaration intact', '新立第八部门：资产组合研究部' in o)
chk('org_chart: v5 visualization mapping intact', '资产组合研究部楼↔资产组合研究部（v5）' in o)
chk('org_chart: 分野 (配置 vs 择时) intact', '与组合与资金部分野=配置 vs 择时' in o)

# 4. structural integrity
chk("id:'alloc' unique", t.count("id:'alloc'") == 1)
chk('drawAlloc defined once', len(re.findall(r'function drawAlloc\s*\(', t)) == 1)
depts = re.findall(r"dept:'([^']+)'", t)
chk('building count == 11', len(depts) == 11)
canon = ['研究部', '策略部', '风控部', '交易部', '组合与资金部', '数据部',
         '资产组合研究部', 'ETF 操作链条研究组', '舰队部', '总经办', '工程部']
unknown = [d for d in depts if not any(c in d for c in canon)]
chk('all 11 building depts map into 11-dept canon (v2 10 + v5 8th)', len(unknown) == 0)
if unknown:
    print('  unknown depts:', unknown)
alloc_dept = [d for d in depts if '资产组合研究部' in d]
chk('alloc dept = 资产组合研究部 (not 组合与资金部)', len(alloc_dept) == 1 and '组合与资金部' not in alloc_dept[0])
pf_and_alloc_same = sum(1 for d in depts if '组合与资金部' in d)
chk('组合与资金部 maps exactly 1 building (pf only)', pf_and_alloc_same == 1)

print()
print('RESULT:', 'ALL PASS' if not fails else 'FAILS: %d' % len(fails))
sys.exit(0 if not fails else 1)
