"""r555 helper: insert canon W47 row after W46 row (CRLF working tree, autocrlf-normalized)."""
PATH = 'research/PERPETUAL_FACES.md'
data = open(PATH, 'rb').read().decode('utf-8')
nl = '\r\n' if data.count('\r\n') > 0 else '\n'
print('working-tree EOL:', repr(nl), '| lines:', data.count(nl))

marker = '- N1 波46'
i = data.find(marker)
assert i > 0, 'W46 row not found'
j = data.find(nl, i)
assert j > 0

ROW = (
    '- N1 波47（r555 bm-a 冻·prereg 时展行）：**第三十七枚引擎波·bm-a 第十一枚自有波**'
    '·engine_owner=bm-a·SATURATION_ENGINE_LAW §1/§2 同 W10-W46 合同·不入池·免预注册税·'
    'cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**·'
    '【本机 bm-a 实例=tick 架构（r535 律族——冻结 commit 后下一 tick 新进程重读活树即见 W47 行'
    '=免杀重启·W44/W45 同窗实证 r553/r554「tick 自燃」·点火验证唯一证据=产物增长面 r325 律）'
    '·队列空（本机上波 W45 同窗全生命周期收官 r554：冻结 12f77f174→12/12 烧录→finalize one-pass '
    'K=96,920·链头 463,548；上游 W46 bm-c r348 亦已收官 K=99,120·链头 465,748'
    '——链全追平 W1..W46 零在飞上游面）→零隔接力·波号 47=W46 行落账后首个自由号'
    '·r511 表尾锁例冻结前 fetch 实核表尾时 W47 号位净空·first-free-number 法】·'
    '【never-dry 供给律常设步·r555 实况=引擎活·status exit 0·queue_depth 0·idle·禁空转禁等 CEO 提醒】·'
    'A-ext seed=**137_004..139_003**（**A 面算术顺延**·=W46 A 尾 137_003+1·步长逐字·**零跳位**·'
    '【机证净空 registry-derive——leg1-A 机证==W46 行 W47+ 警示投影 CLEAN==候选】·'
    '扫描面=pre-W47 四十四行 N1 带表【含 W44 行 131_004..133_003/44_201..44_400'
    '（r553 bm-a·finalize 实落账 K=94,720·链头 459,340）·W45 行 133_004..135_003/44_401..44_600'
    '（r554 bm-a·finalize 实落账 K=96,920·链头 463,548）·W46 行 135_004..137_003/44_601..44_800'
    '（r348 bm-c 冻结·finalize 实落账 K=99,120·链头 465,748）】·带域不相交·异带共存 r531 律·'
    'W1 ext·v1 在用带·SEED_REGISTRY 全键 161（int 值 160·LOWAMP-P1/P2/P3 键 20.33M 域零交集·'
    '**pc_l2_ic=45_000 命中面=W47-B 拒绝事实**）·**N3-R1 实际种子带 70_000..70_005**'
    '（r529 裁定行强制腿）·**runner 探针种子簇 95_000..95_003**（r335 发现腿·W26 起强制）·'
    'N2/N4 设计探针保留点 40_000/40_001·N2-W15 草案探针点 31_000/31_500/32_000·'
    'lfc 实际抽带 30_000..30_099·options_wave2 实际抽带 63_000..63_049·leg-3e 实际流避让】·'
    '**ADMIT 回执=results/_r555bma_w47_band_gate.py**·r555 bm-a 起草窗实跑'
    '【leg0 四十四行+候选注册面校验+leg0b W46 行 W47+ 警示 prose 在场校验'
    '+leg1-A registry-derive 算术面 CLEAN 机证+leg1-B 拒绝事实机证（45_000=pc_l2_ic 命中）'
    '+leg2-A/leg2-B 首净窗==候选（A 零跳位/B 强制跳位族）+leg3 双带 ADMIT+N3-R1 腿+探针簇腿'
    '+origin 号位净空机验·非重挑 R250·W47 带从未指派·测量面零结果可钓·'
    '同号竞速窗如实披露=W42/W43/W44 同号草案让路先例下 fetch+机闸双锁】·'
    'B-ext exit seed=**45_001..45_200**（**B 面强制跳位族**·算术位 44_801..45_000 '
    '**机证 REFUSED——SEED_REGISTRY[\'pc_l2_ic\']=45_000 命中**'
    '〔W39-B/W43-B/W5/W6/W7 先例族·disjoint 硬律胜过步长惯例〕·'
    '**r307 尾律 scan-forward 首净窗=45_001..45_200**【机证 derive——leg1-B 拒绝事实+'
    'leg2-B 首净窗机证·非自由挑位】）。**N2/N4 让位注记**：本波 A 带 137_004..139_003'
    '——N2/N4 波预注册时避开此带即可（扫描腿已含）。**W48+ 警示**：A +2_000 算术位 '
    '139_004..141_003（投影 CLEAN——W48 prereg 机闸为准）；B +200 算术位 45_201..45_400'
    '（投影 CLEAN——同上·B 面基已随 W47 跳位移至 45_001 基·尾律以 W47 B 尾 45_200+1 起）'
    '·去节流令=首落号成后发波·号位指派律。'
)

# insertion point: after W46 row line + following blank line
k = j + len(nl)
assert data[k:k + len(nl)] == nl, 'expected blank line after W46 row'
insertion = ROW + nl + nl
new = data[:k + len(nl)] + insertion + data[k + len(nl):]
open(PATH, 'wb').write(new.encode('utf-8'))
print('inserted; new lines:', new.count(nl))
