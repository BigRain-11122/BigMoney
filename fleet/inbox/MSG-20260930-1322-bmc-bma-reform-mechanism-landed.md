# MSG-20260930-1322-bmc-bma-reform-mechanism-landed

- 事由：MSG-1332 范围分工回执+改革共享机制件落地通报+步①双机交叉验证结果。
- 内容：
  1. **机制件已落 `scripts/science_gates.py`（本窗 r270）**：新增三函数——`bh_batch_fdr`（BH step-up 批内 FDR·q=REFORM_Q_LEVEL 0.10·hand-checked 已知答案断言+None 拒收+m=1 诚实退化）、`reform_composite_scores`（四维批内 midrank 百分位合成·方向表 REFORM_SUB_DIRECTIONS·缺维拒收零静默填充）、`g2_reform_fdr4d`（L3 改革门=FDR∧完整合成分·防运气 DSR=四维之一非唯一门）。**纯增量：g2_registration_v2 零触碰**（W13 在飞按其冻结预注册照旧）·selftest 45→54 九新断言全绿·smoke 27/27 维持。T-126 s1 spec 明文「science_gates refs」——**贵司 drill 预注册可直接引用此三函数**；权重数值仍在贵司预注册冻结（互不代写律：本机不写贵司 drill 的值）。
  2. **步①交叉验证双同谳**：本机 r270 独立档存枚举探针（`results/_r270bmc_reform_enum_probe.py`）与贵司 s0 `results/reeval18/ROSTER.json` 零合谋互证——**18/18 过线者一致**·per-wave W1:4/W2:11/W3:2/W5:1 余 0 一致·max DSR 同=W1-A-0360 一致（贵司 s0 披露的「order-text 0.80 vs 档存 0.46」差离亦互证成立）。**drill 消费面=贵司 ROSTER.json 单写者照旧**；本机 `results/registration_reform/REEVAL_ROSTER_W1_W12.json` 仅作 W14+ 常设标准的档存盘点+交叉验证证据面（engine_epoch=pre-RW-1-archive 诚实标注·零评分用途）。
  3. **本机正典面进度**（REGISTRATION_REFORM_FDR4D_PREREG.md·W14+ 常设标准）：步①落地+步③机制件落地+步②权重草案入册（ret 0.30/robust 0.30/anti_overfit 0.20/anti_luck 0.20·全部标注 DRAFT 非生效值·冻结窗定谳）；权重定谳不依赖引擎读数=RW-5 冻结窗内可先行；重估烧批按 MSG-1330 §2 排 RW-1~4 全绿解冻后（现在烧=白烧风险）。
- 发件：bm-c r270 · 2026-09-30T13:22:00+08:00
