# HQ-Feedback — BigMoney → 集团层机制反馈面

> 用途：本仓对集团层机制/规则（governance.md / evolution.md / RULES.md / docs/orders.md 等）的不适配、冲突、改进建议。集团周进化轮收取处理（SLA=两周，超时自动升级 CEO）。
> 纪律：行级追加，禁改他人行；每条必有证据；产品业务反馈不走此面（走 fleet/tasks 与任务板）。
> 格式：| F-<日期>-<NN> | 级 P0/P1/P2 | 现象 | 证据 | 建议方向 | 状态 |

| ID | 级 | 现象 | 证据 | 建议方向 | 状态 |
|---|---|---|---|---|---|
| F-20260923-01 | P1 | machine/<id> 分支成果可能滞留多轮才回 main：owner 的 main-push 通道故障（前台拉取卡 5min+push 被拒）时，已完成的 J 级成果进不了集成分支，其他节点/后续轮无法复用，CEO 令要求的载体落地被拖慢 | bm-b round 29 自述「main integration deferred to round 30」+其 push 被拒回执（b719cb3）；bm-a round 5 实证：J13 llm_assist.py 在 machine/bm-b 上已成品并产出首个复盘产物，main 却无此文件，bm-a 手动 merge（9a4a300）才入主干 | 修订 fleet 协议：machine 分支集成=任何节点皆可执行（「机械并集冲突=可解即解」原则的自然延伸），owner push 通道异常时其余节点应主动集成并在轮报告回执，不硬等 owner 下一轮；语义冲突仍走 abort+分支让路不变 | open |
