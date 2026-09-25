# T-70 本地编码试点 · 中期判读备料卷（证据面）

- 判读日=2026-10-09（本件=确定性备料证据，判读本体=当日 GM 按冻结判据裁决）
- 冻结过线定义（prereg 原文）：①功能通过率 ≥ 云端−0 件 AND ②码质非劣 AND ③④如实呈报（无硬线，资源面=披露项）→ 过线；任一不满足→如实报坑清单
- 数据源：ledger.jsonl（10 行）+ blind_eval/verdict.json（R206 聚合）+ 冻结分类表（R198-R206 实证）

## 判据① 功能通过率（冻结门=交付可验口径）

| 面 | 云端 A | 本地 B | 差距 |
|---|---|---|---|
| 交付可验率（verify_cmd 门） | 10/10 | 2/10 | −8 件 → **①FAIL** |
| 实现正确率（live 面分列） | — | 5/10（02、03、05、06、07） | −5 件（对 A 10/10） |

两面分列（R201 判读要求）：**验证逻辑病** 3 件（05、06、07＝live 面正确而自测期望算术错）+ **实现病** 5 件（01、04、08、09、10）。
即便按宽容实现面口径，① 仍差 5 件不过线——坑清单路径成立。

## 判据② 码质盲评非劣（R206 收口）

- 云端 A=8.875 vs 本地 B=5.775，阈值=B >= A - 0.5 = 8.375，差距 **-3.10** → **②FAIL**（远超 −0.5 容许带）
- 四维全负：readability -2.6／idiomatic -3.1／boundaries -3.7／structure -2.6（边界处理最差）
- 盲评缺陷与判据-1 B 失败族独立收敛互证（u-08/u-09/u-10 ↔ 实现病三例）——收敛效度在册。

## 坑清单（如实·按冻结分类表）

- **falsy-ternary+render-consistency**（1 件：09）
  - task09：len==0 and 0 or c+1 empty-branch bug ([]->1) + lowercase bool render, live done_mismatches=1 vs A 0 ｜证据=ledger row 09 + blind finding u-09
- **helper-confusion+output-contract-omission**（1 件：10）
  - task10：double-render valid-clock->bad + VERDICT line never appended (live 3/3 reproduced, IndexError) ｜证据=ledger row 10 + blind finding u-10
- **impl-detection-gap**（1 件：01）
  - task01：own validator misses case4 empty-field + case5 invalid-timestamp (product detection gap, not fixture math) ｜证据=tasks/01/B/rr_lint.py + ledger row 01
- **selftest-expectation-arithmetic**（3 件：05、06、07）
  - task05：live face correct; own fixture duplicated synthetic rows + hand-computed expectation mismatch ｜证据=ledger row 05 + prompt.md 勘误段
  - task06：live face correct; 2 embedded fixture-arithmetic expectations wrong ｜证据=ledger row 06
  - task07：live face byte-identical to A; fixture ts yield 23h vs expectations copied 49h/25h ｜证据=ledger row 07
- **spec-interpretation-tz**（1 件：04）
  - task04：live digest naive-tz UTC skew vs spec-3b (+ own selftest crash) ｜证据=ledger row 04 + tasks/04/B
- **type-confused-count+contract-flattening**（1 件：08）
  - task08：dup_codes [raw lines].count(value) always-0 + panel-face flattening live MISMATCH fails=4 ｜证据=ledger row 08 + blind finding u-08

## 资源与经济面（③④=披露项，无硬线）

- 本地生成 token：合计 29161（区间 1172–5143/件，qwen3-coder:30b Q4_KM）
- B 臂耗时：10 件合计 1283s（区间 86–209s，agent 通道非纯 API 口径 A 臂不作 1:1 对比）
- GPU 峰值 11630 MiB（12GB 4070S 内）、OOM 0、上下文溢出 0、让路事件 0；云侧 token 成本不可从轮上下文分离（bytes/3.5 估口径在册）
- 辅助评员 qwen2.5:14b：not run (optional face, honest disclosure; RUBRIC §2.4 A-arm style-residual limitation stands)

## 修复对策候选（未定·非冻结）

- （候选·未定）prompt 规格给出可复用 fixture 模式，压缩 B 臂心算期望面（task05/06/07 族根源）
- （候选·未定）prompt 显式输出契约行清单（VERDICT/汇总行逐条点名，task10 族）
- （候选·未定）prompt 注明类型面计数口径（禁 and/or 三元链式计数、bool 渲染大小写，task08/09 族）

## P-08 机队机型适配矩阵数据点

qwen3-coder:30b 定性证据＝**实现理解强（live 面多件正确/字节恒等）、自证验证弱（自测期望算术+契约缺失+类型面计数三簇）**；双必需门皆负。过线则提 24GB 专用编码机 P1 采购案、不过则坑清单路径——判读本体 2026-10-09 呈报。

（本卷由 scripts/t70_midterm_dossier.py 确定性生成，可再生成；判据冻结引用，禁看结果调线。）
