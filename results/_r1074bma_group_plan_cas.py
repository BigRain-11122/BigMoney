# r1074bm-a: group-plan BigMoney section CAS surgical refresh + detail-plan pointer
# law: BM plan sec.5 consumption surface (2) -- group BigMoney-section detail pointer
# recipe: r1049 group CAS surgical (zero tree touch, temp index, commit-tree, CAS push)
import subprocess, sys, os, json, tempfile
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
PATH = 'cph4/fleet/GROUP-AUTOMATION-PLAN-v1.md'

def g(*args, env=None):
    r = subprocess.run(['git','-C',GRP]+list(args), capture_output=True, text=True,
                       encoding='utf-8', errors='replace', env=env)
    return r.returncode, (r.stdout or '')+(r.stderr or '')

rc, _ = g('fetch','origin')
assert rc == 0, 'fetch failed'
rc, base = g('rev-parse','origin/main')
base = base.strip()
print('base', base)

rc, raw = g('show', '%s:%s' % (base, PATH))
assert rc == 0 and raw, 'origin blob read failed'
orig = raw

START = '## ③ BigMoney 量化'
END = '## ④ BigDomain'
i = orig.find(START); j = orig.find(END)
assert i > 0 and j > i, 'section anchors not found'
old_block = orig[i:j]

NEW_BLOCK = '''## ③ BigMoney 量化（W 波自跑已验证）
- **现状**：五要素全 OK（10-19 审计面机读 E1-E5 全绿·gaps=0）——①循环✓（iteration_loop v2 24/7·W 波 276 波连续自跑）②自领活✓（idle_trigger 双字面+backlog/pool 清点在环）③质量闸✓环内（判负关线 CLOSED_FAMILIES 运行侧硬拒+预注册预算运行时自动停+假绿 claimable 交叉面三闸 A1/A3 落地）④日进化✓（盈亏归因日账 A2 落地·streak 1/5 交易日累积中）⑤定位律✓（近 5 轮产品轮 3·等待占比 0.0）。
- **建设案细化正身**（本节细化指针·上链归 @quant 席/GM 面·BM 仓正身）：quant/bigmoney `research/AUTOMATION-LINE-PLAN-v1.md`（§一 五要素实测映射/§二 缺口清单 G1-G5/§三 建设排期 A1-A5〔A1-A4 已落地·A5 验收中〕/§四 验收判据 V1-V5/§五 消费面与回执律）+ 常设审计面 `scripts/automation_line_audit.py`→`results/automation_line_audit.json`（S6 常设腿）+ A5 验收记录载体 `scripts/a5_acceptance_pack.py`→`results/a5_acceptance/PACK-*.md`（幂等再生·当日重跑原地再生）。
- **验收**：≤10-31 首线实装验收（§四判据 V1-V5 全过=V2 归因 streak ≥5 交易日+V5 审计连绿 ≥3 日累积中·验收记录面已立）+循环 72h 自续+闸内零违例；BM 仓 O 令由 bm-b/CEO-PROXY 镜像。

'''
new = orig[:i] + NEW_BLOCK + orig[j:]
# --- assertions: everything outside the block byte-identical, structure sane
assert new[:i] == orig[:i] and new[i+len(NEW_BLOCK):] == orig[j:], 'outside-block drift'
assert new.count('## ①') == orig.count('## ①') == 1
assert new.count('## ⑨') == orig.count('## ⑨') == 1
assert new.count('## ③ BigMoney') == 1
assert 'AUTOMATION-LINE-PLAN-v1.md' in new and 'a5_acceptance_pack' in new
assert '<<<<<<<' not in new and '>>>>>>>' not in new
print('surgery OK: block %d -> %d bytes, outside byte-identical' % (len(old_block), len(NEW_BLOCK)))

# --- CAS: temp index -> hash-object -> update-index -> write-tree -> commit-tree -> push
tmpdir = tempfile.mkdtemp(prefix='_r1074bma_grpcas_')
blob_path = os.path.join(tmpdir, 'blob.md')
open(blob_path, 'w', encoding='utf-8', newline='').write(new)
msg_path = os.path.join(tmpdir, 'msg.txt')
open(msg_path, 'w', encoding='utf-8', newline='').write(
    'GROUP-PLAN BigMoney sec.iii refresh: five-element audit face (E1-E5 all OK 10-19, gaps=0) '
    '+ detail-plan pointer to quant/bigmoney research/AUTOMATION-LINE-PLAN-v1.md (sec.5 consumption '
    'surface, @quant seat face) + A1-A4 landed face + A5 acceptance-record carrier pointer. '
    'Group order 2026-10-18 21:11 nine-company plan; BM section only, other sections byte-identical. '
    'Executor: bm-a loop r1074 (CAS surgical, zero tree touch)')
env = dict(os.environ); env['GIT_INDEX_FILE'] = os.path.join(tmpdir, 'tmpindex')
import re
def _sha40(out):
    for line in out.splitlines():
        line = line.strip()
        if re.fullmatch(r'[0-9a-f]{40}', line):
            return line
    return ''

rc, _ = g('read-tree', base, env=env); assert rc == 0, 'read-tree failed'
rc, out = g('hash-object', '-w', blob_path); blob = _sha40(out)
assert len(blob) == 40, 'bad blob sha: %r' % blob
rc, _ = g('update-index', '--cacheinfo', '100644', blob, PATH, env=env); assert rc == 0
rc, _o = g('write-tree', env=env); tree = _sha40(_o)
assert len(tree) == 40, 'bad tree sha'
rc, _o = g('commit-tree', tree, '-p', base, '-F', msg_path); newc = _sha40(_o)
assert len(newc) == 40, 'bad commit sha'
print('blob', blob[:12], 'tree', tree[:12], 'newc', newc[:12])
# --- push (CAS: fast-forward against fresh base; one fresh-base retry on race)
for attempt in (1, 2):
    rc, out = g('push', 'origin', '%s:refs/heads/main' % newc)
    print('push attempt', attempt, 'rc', rc, out.strip()[:200])
    if rc == 0:
        break
    rc2, base2 = g('rev-parse', 'origin/main'); base2 = base2.strip()
    if base2 == base:
        print('PUSH FAILED AND BASE UNMOVED -- genuine reject, abort'); sys.exit(1)
    # race: rebuild on fresh base
    base = base2
    rc, raw = g('show', '%s:%s' % (base, PATH)); assert rc == 0
    if raw == orig:
        new = raw[:raw.find(START)] + NEW_BLOCK + raw[raw.find(END):]
        open(blob_path, 'w', encoding='utf-8', newline='').write(new)
        rc, _o = g('hash-object', '-w', blob_path); blob = _sha40(_o)
        rc, _ = g('read-tree', base, env=env)
        rc, _ = g('update-index', '--cacheinfo', '100644', blob, PATH, env=env)
        rc, _o = g('write-tree', env=env); tree = _sha40(_o)
        rc, _o = g('commit-tree', tree, '-p', base, '-F', msg_path); newc = _sha40(_o)
        print('rebuilt on fresh base', base[:12], 'newc', newc[:12])
    else:
        print('origin BigMoney section CHANGED by another writer -- content re-read, abort for adjudication')
        sys.exit(3)
if rc != 0:
    print('PUSH FAILED both attempts'); sys.exit(1)
# --- verify delivery: fetch + tip + path blob equality
rc, _ = g('fetch', 'origin')
rc, tip = g('rev-parse', 'origin/main'); tip = tip.strip()
print('post-push origin tip', tip[:12], 'match', tip == newc)
rc, verify = g('rev-parse', 'origin/main:%s' % PATH); verify = _sha40(verify)
print('path blob on origin', verify[:12], 'match-new-blob', verify == blob)
json.dump({'base': base, 'newc': newc, 'blob': blob, 'tip': tip,
           'path': PATH, 'ts': 'r1074 bm-a'},
          open(os.path.join(r'C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\results',
                            '_r1074bma_group_plan_receipt.json'), 'w', encoding='utf-8'), indent=1)
print('RECEIPT WRITTEN')
