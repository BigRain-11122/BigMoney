# R-20260928-bonsai-fleet-trial — Ternary-Bonsai-2-27B 机队分发试用规格件（CEO 令·P-2026-09-28-07）

> 溯源：CEO 令 2026-09-28 ~13:0x「分发给我的机队，适配的业务都尝试这个大模型本地运行」（交互会话直令·承接 P-2026-09-28-06 实测件）。
> 定位：机队分发**唯一规格件**——各机任务单/各司令牌一律引用本件（引用不复制·禁重复扩写）。实测锚=R-20260927-ternary-bonsai（GPU bench+抽检）+本件 §三（本窗 CPU 档实弹）。

## 一、部署配方（各机直下·U187/U240 律：禁 git/禁 LFS/禁跨机传输）

1. 模型：hf-mirror `prism-ml/Ternary-Bonsai-2-27B-GGUF` 取 `Ternary-Bonsai-2-27B-PTQ1_0.gguf`——**字节锚 5,946,648,928**（不齐=重下，禁带病上岗）。
2. 运行时：GitHub `PrismML-Eng/llama.cpp` fork releases（prism-b10743 档·Win CUDA 12.4）——原版 llama.cpp 拒载 PTQ1_0（私有三元核·其 README 明示）。同源件对照（bm-a labbench 在盘）：llama-bin.zip=257,322,810 字节·cudart.zip=391,443,627 字节。
3. 坑律：PS 下 `curl`=Invoke-WebRequest 别名（`-C -` 解析炸且 exit 0 假成功）——**必 curl.exe 显式**；部署成功判据=加载试跑（llama-server 起→/health ok）。
4. 服务形态：llama-server（OpenAI 兼容 `/v1/chat/completions`）·端口自选避开在役（bm-a 试用 8077）·长驻与否=试后另裁（O-2175 流程）。

## 二、机队包络与准入（对表 R-20260928-cph4-model-matrix §一）

| 机 | 档 | 准入 |
|---|---|---|
| bm-a（4070S 12GB） | GPU | ✓ 已实测（bench tg128=54.7 tok/s·权重 5.53GiB·与 Ollama 栈共卡可跑）；共享机让路律照旧 |
| bm-c（3070魔改 16GB） | GPU | 宽裕（7b serve 5.1GB 共驻后仍可载）；兼验官方 16GB 30+ tok/s 宣称（复测触发器在册） |
| bm-b（3070 8GB） | GPU·紧 | 权重 5.53GiB+KV≈6.3GB——**须独占窗**（7b keepwarm 暂停让位·fleet §10·跑毕复位）；载不下=如实报 |
| bigstream（无 GPU） | CPU | 锚见 §三：≈3 tok/s 档——句子级可用·批量重批不实用·如实判 |
| BG-B | 观察位 P3 | 美术深度批机 LLM 消费面薄+verdict RAM 紧保护——空窗才试·不派单 |
| CEO 笔记本 | **永禁** | 零部署豁免位（CEO 定位令） |

## 三、bm-a 实弹锚（2026-09-28 本窗·CPU 档——GPU 窗被三只 Tuanjie 编辑器+7b serve 占满 10.3/12.3GB·让路律不抢·GPU 服跑重验排夜窗）

- 服起（-ngl 0）：健康态 **5s**；速度 **2.7-3.3 tok/s**（32 核）·进程 RAM **8.3GB**·**显存零占用**·与全栈并行零冲突。
- 业务代表探针三枚：①台词（BigLife 线）**✓ 一次过成品**（居民口吻完整句·finish=stop）②研究摘要 40 字（CPH4/BigCompute 线）**✓ 数字全对**（-1/0/+1·九分之一·5.95GB·27B·98.2%·弱项知识视觉）③编码 advisory（Biggame T1 胶水位）**✓ 诊断/修法全对**（RemoveAt 索引错位→倒序遍历）·长代码受 400 token 顶截断（GPU 档无此忧——09-27 GPU 抽检回文码逐字全对在案）。
- **弱机档要领（实测教训）**：思考链型任务必 `chat_template_kwargs:{"enable_thinking":false}`——首测无此参数，两枚探针被思考吃满预算、正文零输出（p2/p3 首测实录）。
- 诚实注记：本窗实测前零数字入档（P-06 虚报自纠案承接）·探针原始件=labbench/bonsai2/（gitignored R3）。

## 四、业务适配矩阵（试=证据包·**非产线切换**）

| 业务 | 机/档 | 试验面 | 级 |
|---|---|---|---|
| BigLife | bm-a（台词池主跑）+bm-c | 台词池批量样本 vs 现役 7b 对照（句级延迟+风味抽检） | P1 |
| BigMoney | bm-a/bm-c | 深度问答/复杂一审档（14b 档对照·O-2175 L2 流程）；**编码产线除外**（T-70 判负·云端保留面不切换） | P1 |
| CPH4 Labs | bm-a | 研究摘要/判断档（§三已锚） | P1 已测 |
| BigStream | bigstream CPU 档 | 内容草稿/文案短件（句子级可用边界判） | P2 |
| BigCompute | 借 fleet 机 | 赋能摘要批（对照 7b 档） | P2 |
| Biggame | bm-a advisory+bm-c 机 | 编码 T1 胶水 advisory 位（非产线·T-70 边界律）；BG-B 不派单 | P2 |
| BigDomain | bm-a 轻档 | 商业文案/客服话术 advisory | P2 |

## 五、判据预注册（回执四件套·缺一不算 done）

1. 部署=字节吻合+服起 /health ok；2. 速度=tg128 实测（对照包络）；3. 共存=与在役栈同卡结果如实（可共驻/须让路窗/载不下）；4. 质量=本域样本 ≥3 抽检（对错自评+引用级）。
- 结论三态：**adopt**（某业务面采用——须过 O-2175 评估+fleet-allocations §8.4 改表）/ **observe**（继续观察）/ **reject**（如实判负）。
- 回执窗：认领 ≤24h·**48h 回执关单**（09-30 13:00 首轮呈 CEO）；failed 必写死因。

## 六、防重复纪律

同款试验单机一次（禁双机双批双产·fleet-protocol §三.2 护栏）；本件=唯一样式源；结果回写本件 §三扩行或各司自建 R- 件+指针回本件。

## 验证声明

本件全部数字=本窗实跑（§三）或直读引用（§一§二锚 R-20260927-ternary-bonsai/R-20260928-cph4-model-matrix）；零未跑先写；他机现役态=正典引用级非本窗直测。
