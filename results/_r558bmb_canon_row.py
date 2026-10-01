import os

REPO = r'C:\Fluxgroup\FluxGroup\quant\bigmoney'
P = os.path.join(REPO, 'research', 'PERPETUAL_FACES.md')
raw = open(P, 'rb').read()
crlf = b'\r\n' in raw
print('CRLF detected:', crlf, '| bytes:', len(raw))

text = raw.decode('utf-8')
lines = text.splitlines()
# locate the W50 row line
idx = None
for i, l in enumerate(lines):
    if l.startswith('- N1 波50（'):
        idx = i
        break
assert idx is not None, 'W50 canon row not found'
print('W50 row at line', idx + 1, '| len', len(lines[idx]))
assert '- N1 波51（' not in text, 'W51 row already present'

W51_ROW = (
    '- N1 波51（r558 bm-b 冻·prereg 时展行）：**第四十一枚引擎波〔landed order 计数按 r557 amendment：W48=38/W49=39/W50=40/本波=41〕·bm-b 第十六枚自有波**'
    '·engine_owner=bm-b·SATURATION_ENGINE_LAW §1/§2 同 W10-W50 合同·不入池·免预注册税·cmd_supply 跳过门·**引擎去节流令 O-20261001-2355 §二自有连续系列**'
    '·【本机 bm-b 实例=tick 架构（r535 律：无常驻实例·计划任务 1-min fire 新进程重读活树=新波行天然可见·免杀重启；点火验证唯一证据=产物增长面 r325 律·state queue 面不信）'
    '·队列空（本机上波 W49 同窗全生命周期收官 r556：冻结 4e4f1469a→12/12 烧录→finalize one-pass K=103,520·账本 470,148〔r558 S0 外科送达 e488e8008〕·prereg s7/s8 回填齐）'
    '→零隔接力·**波号 51=注册表尾 W50 行后下一自由号**（r511 表尾锁律·冻结前 fetch 实核+机闸 origin 号位净空断言双锁）】'
    '·**带位 derive（R250：W51 带从未指派·跳位被迫性由带闸机证非自由挑）**：A=**145_004..147_003 算术续行**〔==W50 A 尾 145_003+1·CLEAN——'
    'W50 行 W51+ 警示投影同位交叉验证（r350 bm-c 带闸 W51+ 投影腿机证同窗 CLEAN）·**非预留面：51 号位无任何机器主权声明**'
    '（r518① 公示=预留律适用面=「他机公示其自有下一波」面如 bm-a W48 声明——该面已由注册 W48 行覆盖）·leg1-A/leg2-A 扫描器 CLEAN 机证==算术位==候选〕；'
    'B 算术位 **45_801..46_000 REFUSED**〔refusal facts=**SEED_REGISTRY[xlib_synth_null_a]=46_000 点命中**·==W50 行 W51+ 警示公示拒绝面逐字'
    '〔「B 45_801..46_000 REFUSED [SEED_REGISTRY xlib_synth_null_a=46_000]」·leg0b prose 在场校验+leg1-B refusal facts 机证〕〕'
    '→**强制跳位首净窗 46_001..46_200**〔leg2 scan-forward 机证==候选逐位·W19-B 重基族〕。'
    '扫描面=pre-W51 四十九行 N1 带表（含 W48 行 139_004..141_003/45_201..45_400〔r557 bm-a·烧录在飞〕·W49 行 141_004..143_003/45_401..45_600〔r556 bm-b·finalize 已落账 K=103,520〕'
    '·W50 行 143_004..145_003/45_601..45_800〔r350 bm-c·烧录在飞〕）＋W1 ext＋v1 在用带＋SEED_REGISTRY 全键＋**N3 已用种子带腿（N3-R1=70_000..70_005 全 6 值·MSG-183x r529 裁定行②强制腿）**'
    '＋**runner 设计探针种子簇 95_000..95_003（r335 发现腿·W26 起一切带闸回执强制携带）**＋N2/N4 设计探针保留点 40_000/40_001＋N2-W15 草案探针点 31_000/31_500/32_000'
    '＋lfc 实际流 30_000..30_099＋options_wave2 实际流 63_000..63_049〔leg-3e 实际流避让腿〕；'
    '**ADMIT 回执=results/_r558bmb_w51_band_gate.py**〔r558 bm-b 起草窗实跑·leg0 四十九行+候选注册面校验+leg0b W50 行 W51+ 警示 prose 在场校验'
    '+leg1-A 算术 CLEAN/leg1-B 拒绝面 refusal facts 机证〔SEED_REGISTRY 键名活体 derive〕+leg2-B 强制跳位首净窗==候选+leg3 双带 ADMIT+N3-R1 腿+探针簇腿+origin 号位净空机验〕。'
    '上游注记：**W49 finalize 已落账**（bm-b r556 收口·K=103,520·链头 470,148·r558 外科送达）；**W48/W50 注册在飞 finalize 未落账**=在飞上游诚实注记'
    '（finalize 波集运行时 derive=registry 键全集·FAIL-CLOSED r307 两态律——W51 finalize 前置=W48/W50 finalize 落账）。'
    '**W52+ 警示投影：A 147_004..149_003（CLEAN 预期·W52 冻结时复验）；B 46_201..46_400（CLEAN 预期·复验）**。'
)

new_lines = lines[:idx + 1] + [W51_ROW] + lines[idx + 1:]
out = '\n'.join(new_lines)
if crlf:
    out = out.replace('\n', '\r\n')
data = out.encode('utf-8')
open(P, 'wb').write(data)
print('W51 canon row inserted after line', idx + 1, '| new bytes:', len(data))
# verify
t2 = open(P, 'rb').read().decode('utf-8')
assert '- N1 波51（r558 bm-b 冻·prereg 时展行）' in t2
assert t2.count('- N1 波51（') == 1
i50 = t2.index('- N1 波50（')
i51 = t2.index('- N1 波51（')
assert i51 > i50
print('VERIFY OK: W51 row after W50 row, single occurrence')
