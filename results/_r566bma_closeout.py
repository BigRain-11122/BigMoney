import io, os

entry = (
    "\n[2026-10-02 08:5x r566 bm-a] W63 同窗双冻撞车三新面（席位公示盲区+跳位语义分叉+异种子复制品弃置律·r511 族第 8 例）："
    "①席位公示非在飞窗无条件裁——MSG-0843 先于冻结已推 origin，对侧在飞会话（bm-c r357）未消费 inbox 席位仍冻结同号→席位=错峰机制非裁决机制，commit 时序律仍是唯一硬裁定；"
    "②**跳位语义分叉首例**——同一警示（双点 49_000/49_100 中位拒绝）下两读法各出合法首净窗：越 hit 起窗 49_101..49_300（r335 W26：95_004/40_051 先例族）vs 窗步链跳 49_201..49_400（bm-c chained-skip 读法）——历史跳位全部单点/尾点拒绝两读法恒同解，本例双点中位首次分叉→正典在册面照准+歧义提 HQ-FEEDBACK（法典 §4 跳位语义钉死一行防未来分叉）；"
    "③异种子分片复制品≠确定性孪生——B 带分歧下本机已烧 2 片是异种子面，弃置=先验属（audit.machine==self）再删+目录清空，零污染靠 finalize 从未跑+append_ledger 零触碰（与 r558 同带逐位同让路零成本面相反：异带让路必须动刀清产品）；"
    "④冻结方 tick 引擎冻结后推送前即自燃——yield 必查本地产品目录+遥测 ledger burn 行（r523 活烧窗让路面）。"
    "How to apply：未来带闸冻结窗遇跳位警示行先钉语义再落带；对侧窗口重叠时席位 MSG 发布后 10 分钟内盯 origin；异带让路动刀序=验属→删产品→清遥测→回执。"
)
p = 'CODELY.md'
b = open(p, 'rb').read()
t = b.decode('utf-8')
assert t.count(entry[:40]) == 0, 'entry already present'
t2 = t.rstrip('\n') + '\n' + entry.strip() + '\n'
open(p, 'wb').write(t2.encode('utf-8'))
print('CODELY entry appended, size:', os.path.getsize(p))

rr = "2026-10-02 09:0x | r566 | W62 产品 12/12 送达 origin+W62 finalize 确定性孪生让路（bm-c 先达·payload 恒等断言过·r498 律）+W63 同窗双冻让路（跳位语义分叉首例披露·异种子 2 片验属弃置）+W64 全生命周期冻结（席位 MSG-0851→ADMIT 62 键机证→prereg+五面纯增量 922 行→selftest x3 绿→推送 f41a9009d）+tick 自燃 3/12 片实证 | dualrun streak 32/3 零漂移·audit 旗=pool 饥饿（引擎线在役注记）·watermark board-clear 绿·S6 28 腿全绿假日 no-op+REPORT/LIVE-2026-10-02 再生成·attrition CLEAN·smoke 47/47 | 下轮：W64 烧毕收割（12/12 预计 ~09:1x）→W63 bm-c finalize 落账后 W64 finalize（链序 FAIL-CLOSED）→W65 席位公示随 never-dry 续接\n"
p2 = 'round_reports-bm-a.md'
b2 = open(p2, 'rb').read()
t3 = b2.decode('utf-8')
t4 = t3.rstrip('\n') + '\n' + rr.strip() + '\n'
open(p2, 'wb').write(t4.encode('utf-8'))
print('round report line appended')
