# R-20261001 bonsai bm-a 4070S GPU 档夜窗复验回执 — T-2026-10-01-135（D-20261001-02 派单）

- 集团决策 D-20261001-02（「bm-a GPU 档复验=夜窗排程归 BigMoney 自领」）·fleet 票 T-2026-10-01-135 ·唯一规格件 = cph4/research/R-20260928-bonsai-fleet-trial.md（HQ 仓·引用不复制）
- 机：bm-a（RTX 4070S 12GB）·窗：2026-10-01 01:4x-01:5x 真夜窗（三只 Tuanjie 编辑器缺席·GPU util 0%）
- 证据（机器可读·实跑零预写）：`results/_r497bma_bonsai_gpu_reverify.json`（编排器 `results/_r497bma_bonsai_gpu_reverify.py`）

## 1. deploy — PASS

- 字节锚 3/3 MATCH：model 5,946,648,928 ·llama-bin.zip 257,322,810 ·cudart.zip 391,443,427（labbench/bonsai2 在盘）
- runtime 解包 `labbench/bonsai2/runtime/`（PrismML-Eng fork b10743/adfffbe41 Win CUDA 12.4）
- llama-server `-ngl 99 -fa on -c 4096` port 8077：`/health` ok **4.6s**

## 2. speed — 夜窗裸窗 tg128 = 58.33 ± 0.20 tok/s

- llama-bench `-p 512 -n 128 -r 3`（与 09-27 锚同法）：**tg128 = 58.33 ± 0.20**，pp512 = 1649.55 ± 59.12（墙钟 15.1s）
- 对 09-27 锚 54.7：+6.6%（裸窗更干净·包络一致·**4070S GPU 档复验达标**）

## 3. coexist — can-co-reside（实测共驻跑通）

- 共驻态 = 在役 J13/MiniGame 栈 qwen2.5:7b-instruct 常驻（4.77 GiB，keep_alive=-1）+ bonsai 全量上卡（-ngl 99）
- 共驻 tg128 = **58.01 ± 0.56**（裸窗保有率 **99.5%**），pp512 = 1647.55 —— 12GB 卡双模型共存成立，规格件 §二「与 Ollama 栈共卡可跑」09-27 宣称复验成立
- 让路纪律实弹：夜窗内 MiniGameOllamaKeepWarm（10 分钟班）01:43:59 曾把 7b 拉回占卡；本次按 U020 释放阀（`gaming/MiniGame/.codely-cli/engine-tick/keepwarm.pause`，bm-b 让路窗先例）暂停 keeper→优雅卸载（keep_alive=0）→裸窗先占先得→复测完毕即复温 7b（keep_alive=-1·keeper 设计态）→**阀旗已撤、终态 7b 在册=与窗前一致**
- 独立 5min-TTL 复温客户端在卸载后 ~25s 即重拉 7b（非 keeper 脚本·旗标不管辖）——已如实记入证据件 `window_note`

## 4. quality — 不在本票范围（复用在案：09-27 GPU 抽检回文码逐字全对 + 09-28 CPU 档三探针 §三）

## 机队对照表（fleet comparison face 新行）

| 机 | 档 | tg128 tok/s | 形态 | 出处 |
|---|---|---|---|---|
| bm-a 4070S 12GB | GPU | **58.33 ± 0.20**（裸窗）/ **58.01 ± 0.56**（共驻 7b） | can-co-reside | 本件（10-01 夜窗复验·T-135） |
| bm-a 4070S 12GB | GPU（旧锚） | 54.7 | 裸窗基准（09-27） | R-20260927-ternary-bonsai（引用级） |
| bm-c 3070魔改 16GB | GPU | 40.52 ± 1.10 | 共驻态（7b 5.1GB 常驻） | T-100（D-20261001-02 卷面） |
| bm-b 3070 8GB | GPU·紧 | 40.75 ± 0.30 | 裸窗独占 | T-99 / R-20260928-bonsai-trial-bm-b.md |

## 结论（三态）：**observe 维持（复验面全 PASS·与集团定谳一致）**

- bm-a GPU 档 58.33/58.01 复验达标且共驻成立；业务适配面维持集团 D-20261001-02 拍板（深度问答/复杂一审 14b 对照档·编码产线除外=T-70 判负在案）
- 复验=观察面，不触发 adopt 三前置（O-2175 评估+fleet-allocations §8.4 改表归集团 CEO 轮）
- 工程坑律留痕：llama-bench stdout=UTF-8 而 subprocess text=True 按 cp936 解码→± 字形变哑字符→字面正则静默失配（解析器已改 charset-agnostic `\D+` 分隔并写入证据件 parser_note；同族=一切跨「外部进程输出×本机 GBK 控制台」界面的文本匹配先探字符面）

## 验证声明

本件全部数字=本窗实跑（证据件 results/_r497bma_bonsai_gpu_reverify.json）或直读引用（09-27/09-28 锚·T-99/T-100 卷面数字出自 D-20261001-02 引用级）；零未跑先写；终态=7b 在册+阀旗已撤（与窗前一致）。
