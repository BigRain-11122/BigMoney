# r1054: CAS surgical append — BigMoney 司流程清单行 → council C-20261018-02 case file
# r1049 recipe: temp-index + commit-tree + push origin <sha>:main; 40-hex hard validation (r1002 CAS law)
# zero working-tree touch (council session live on group tree)
import subprocess, sys, os, tempfile, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
GRP = r'C:\Users\sjs20\Desktop\FluxGroup'
PATH = 'cph4/council/C-20261018-02-全流程梳理冲突对账案.md'

def run(args, cwd=None, inp=None):
    p = subprocess.run(args, capture_output=True, cwd=cwd, input=inp)
    return p.returncode, p.stdout, p.stderr

def die(msg):
    print('CAS_FAIL: ' + msg); sys.exit(2)

# 1) fresh fetch
rc,_,err = run(['git','-C',GRP,'fetch','origin'])
if rc != 0: die('fetch rc=%d %s' % (rc, err.decode('utf-8','replace')[:200]))
rc, tip, _ = run(['git','-C',GRP,'rev-parse','origin/main'])
tip = tip.decode().strip()

# 2) origin blob content
rc, blob_bytes, _ = run(['git','-C',GRP,'show','origin/main:'+PATH])
if rc != 0 or not blob_bytes: die('origin show rc=%d' % rc)

APPEND = '''

---

## 六、BigMoney 司流程清单行（供证·bm-a 循环席 2026-10-18 11:5x 落位·24h 窗内）

> 按 §二.1 schema 现读供证（源=Bigmoney-IterationLoop 轮协议正本+schtasks 现读+本轮 43 腿 S6 链实录）；裁决权归委员会，本节零新法零裁决。

| ID | 流程 | 执掌席 | 触发节律 | 写入资源面 | 依赖面 | 预算与产出账 |
|---|---|---|---|---|---|---|
| BM-1 | 轮班链 S0-S8（身份锚定/令扫描/冒烟/任务/S6/收口） | 三机循环席（bm-a/bm-b/bm-c） | Bigmoney-IterationLoop PT10M（v2 活性门控预算=240min 硬顶+25min 零输出静默门·O-20261018-0948 根治后形态） | state-<id>.json+round_reports-<id>.md+fleet/machines/<id>.json+轮收口 git push | git origin/数据源/S6 脚本族/计划任务 | ~2-5min CPU 轻面/轮·产出=轮报告+回执+任务闭环 |
| BM-2 | LoopWatchdog 看门狗 | 循环席 | PT30M（Tools/watchdog.ps1） | 循环任务复活 poke+watch log | schtasks | 零算力·产出=任务存活自愈 |
| BM-3 | HQ-FleetIdleWatch v3 自动复活响应者 | 机队运维席 | 常驻监听+心跳冻结>120min 触发+30min 限速 | watch.log+该机 roster wake_tasks poke | 集团心跳 origin 只读 fetch | 零算力·产出=死窗自愈 ≤30min（10-18 事故 4.5h 零响应的结构性缺口封堵件） |
| BM-4 | 饱和引擎 SatEngine（N1 永续波常供给） | 循环席（bm-a=scripts/·tick 随轮） | tick 随轮+runnable_pool 池续批（autofill watchdog C8） | results/runnable_pool.json+crash_fuse.json+results/p2cal_ext/n1_w*/ 波产物 | N1 引擎队列+science_gates 冻结判据 | CPU 分片>5min 一律入池·产出=波烧批（现役 W267 在飞·W1-W266 全链闭合） |
| BM-5 | S6 数据与面板维护链 43 腿 | 数据道宿主制（R31 判例：leg 级 host 护栏·他机 stdout-only no-op） | 每轮随链跑（gate 脚本族节流：15:30 门/30min 节流/conn-fuse 3） | data/ 面板族+results/ 审计面+docs/live_usage+daily_report | akshare/sina/EM/tushare 源 | 周末/盘中大多合法 no-op（本轮 43/43 rc0）·产出=面板新鲜+四档 exit code 契约 |
| BM-6 | D-19 集团令水位消费 | 循环席 | 每轮轮首+S7 双扫 | state 水位键（SHA-256 内容寻址）+orders_ack 双面 | 集团 origin docs/orders.md+docs/decisions.md | 零算力·产出=CEO 令消费闭环（本轮=11:28 漫剧 3D 转向行/11:3x 本令两行已消费） |
| BM-7 | 孤儿面探针+pre-commit 冲突标记钳+pre-push 所有权爪+attrition 守卫 | 循环席 | 轮首探针+钩子触发+轮尾 scan | results/_orphan_face_probe.*.json+钩子拦截面+attrition 台账 | git hooks+Tools/git_claw.py | 零算力·产出=守卫拦截（本轮孤儿面=0/24） |
| BM-8 | orders_ack 双面回执闸 | 循环席 | 轮收口时 | state-*.json+fleet/machines/*.json 双面同写（per-face 幂等+奇偶校验 exit4） | Tools/orders_ack_append.py+orders_ack_scan.py（10-18 r1053 落地） | 零算力·产出=回执面奇偶恒等（禁手搔单面写） |

**在册治理面供证（已知多写者/活写竞速对·均有在册配方·无新增冲突）：**
- watermark_red.json 双写者（watchdog Invoke-C7 腿 vs py_watermark 探针）→ r1028 newer-wins 吸收配方在册治理 ✓
- S0 rebase vs 运行时活写面（心跳/探针/watermark 三面/轮脏树）→ r751 fetch-only+收口 add -A 吸收在册 ✓（本轮实录：pull --rebase 拒→fetch-only 路径）
- 旧 25min 墙钟 vs 长轮（案卷行 2 同源）→ 三机 TIMEOUT 清账已闭（bm-a 407/bm-b 13/bm-c 432·O-0948 回执窗全闭 10-18）✓
'''

new_content = blob_bytes.rstrip(b'\n') + b'\n' + APPEND.encode('utf-8')

# 3) hash-object new blob (temp file OUTSIDE group tree)
tmpf = os.path.join(tempfile.gettempdir(), '_r1054bma_cas_append.md')
open(tmpf,'wb').write(new_content)
rc, blob, err = run(['git','-C',GRP,'hash-object','-w',tmpf])
blob = blob.decode().strip()
if rc != 0 or not re.fullmatch(r'[0-9a-f]{40}', blob): die('blob rc=%d blob=%r' % (rc, blob))

# 4) temp index → read-tree origin/main → update-index → write-tree
tmpidx = os.path.join(tempfile.gettempdir(), '_r1054bma_cas.idx')
env = dict(os.environ); env['GIT_INDEX_FILE'] = tmpidx
if os.path.exists(tmpidx): os.remove(tmpidx)
p = subprocess.run(['git','-C',GRP,'read-tree',tip], capture_output=True, env=env)
if p.returncode != 0: die('read-tree rc=%d' % p.returncode)
p = subprocess.run(['git','-C',GRP,'update-index','--cacheinfo','100644,%s,%s' % (blob, PATH)], capture_output=True, env=env)
if p.returncode != 0: die('update-index rc=%d %s' % (p.returncode, p.stderr.decode('utf-8','replace')[:200]))
p = subprocess.run(['git','-C',GRP,'write-tree'], capture_output=True, env=env)
tree = p.stdout.decode().strip()
if p.returncode != 0 or not re.fullmatch(r'[0-9a-f]{40}', tree): die('tree rc=%d tree=%r' % (p.returncode, tree))

# 5) commit-tree
msgf = os.path.join(tempfile.gettempdir(), '_r1054bma_cas_msg.txt')
open(msgf,'w',encoding='utf-8').write('council C-20261018-02 §六: BigMoney 司流程清单行供证（BM-1..BM-8+3 在册治理面·24h 窗内首班前落位·现读源=轮协议正本+本轮 43 腿实录） via bm-a r1054\n')
p = subprocess.run(['git','-C',GRP,'commit-tree',tree,'-p',tip,'-F',msgf], capture_output=True, env=env)
newc = p.stdout.decode().strip()
if p.returncode != 0 or not re.fullmatch(r'[0-9a-f]{40}', newc): die('commit-tree rc=%d newc=%r' % (p.returncode, newc))

# 6) push with race retry (r1049 attempt-2 law)
def try_push(base_tip, commit):
    rc, out, err = run(['git','-C',GRP,'push','origin','%s:refs/heads/main' % commit])
    txt = (out+err).decode('utf-8','replace').lower()
    ok = rc == 0 and not any(k in txt for k in ('fatal','rejected','failed','error'))
    return ok, (out+err).decode('utf-8','replace')[:300]

ok, ptxt = try_push(tip, newc)
if not ok:
    print('push attempt-1 raced, retry on fresh base...')
    rc,_,_ = run(['git','-C',GRP,'fetch','origin'])
    rc, tip2, _ = run(['git','-C',GRP,'rev-parse','origin/main'])
    tip2 = tip2.decode().strip()
    # rebuild on fresh base: same content, new parent
    if os.path.exists(tmpidx): os.remove(tmpidx)
    subprocess.run(['git','-C',GRP,'read-tree',tip2], capture_output=True, env=env)
    subprocess.run(['git','-C',GRP,'update-index','--cacheinfo','100644,%s,%s' % (blob, PATH)], capture_output=True, env=env)
    p = subprocess.run(['git','-C',GRP,'write-tree'], capture_output=True, env=env)
    tree2 = p.stdout.decode().strip()
    p = subprocess.run(['git','-C',GRP,'commit-tree',tree2,'-p',tip2,'-F',msgf], capture_output=True, env=env)
    newc2 = p.stdout.decode().strip()
    if p.returncode != 0 or not re.fullmatch(r'[0-9a-f]{40}', newc2): die('rebuild newc bad')
    newc = newc2
    ok, ptxt = try_push(tip2, newc)
    if not ok: die('push attempt-2 failed: %s' % ptxt)

# 7) post-push verify: fetch + tip equality + per-path blob equality
run(['git','-C',GRP,'fetch','origin'])
rc, tipv, _ = run(['git','-C',GRP,'rev-parse','origin/main'])
tipv = tipv.decode().strip()
rc, blobv, _ = run(['git','-C',GRP,'show','origin/main:'+PATH])
equal = blobv == new_content
print('CAS_PUSHED' if (tipv == newc and equal) else 'CAS_VERIFY_MISMATCH tip=%s newc=%s blob_equal=%s' % (tipv, newc, equal))
print('newc=%s' % newc)
