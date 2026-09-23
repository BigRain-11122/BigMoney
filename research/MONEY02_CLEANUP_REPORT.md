# Money02 清理与入库报告（T-2026-09-23-01）

> 用户令 2026-09-23 14:30（经 bm-a 转发）+14:52 保险丝补充条款。执行机 bm-b。本报告=删除前留档。

## 一、删除清单（无用集）

| 项 | 文件数 | 体积 | 判定依据 |
|---|---|---|---|
| `Money02/data/cache/` | 50 | 6.327 GB | 引擎面板 npy，bars+lhb 可再生派生面 |
| `Money02/data/live/` | 39 | 0.011 GB | 全市场 24h 滚动实时快照，已陈旧 |
| `Money02/logs/` | 10 | 0.15 MB | 8 个 *.log 运行日志 + 2 个下划线前缀测试脚本（`_crypto_smoke.py`/`_minhold_test.py`=临时件） |
| `Money02/results/fit_matrix/run_cn.log`、`run_crypto.log` | 2 | 0.01 MB | 运行日志 |
| **合计回收** | **101** | **≈6.35 GB** | 无 __pycache__/*.pyc/空文件/pid（2026-09-22 已清过一轮） |

## 二、保留上传清单（有用集，判定依据 research/MONEY02_ASSETS.md）

| 项 | 文件数 | 体积 |
|---|---|---|
| `data/bars/`（5221 只 A 股全史 parquet + 复权因子侧车） | 10444 | 1.087 GB |
| `data/lhb/`（龙虎榜 265,831 行×19 年） | 80 | 0.063 GB |
| `data/mkt_crypto/`（Gate.io 26 币全史） | 79 | 0.018 GB |
| `data/index/`（上证综指/沪深300/中证500 日线） | 3 | 0.001 GB |
| `results/` + `results_crypto/`（联赛 211 轮档案、fit_matrix、名人堂、模拟盘账本） | 307+7 | ≈5 MB |
| 根级 46 件（全部 .py 代码 + `CODELY.md` 用户历史指令只读档案 + `README.md`） | 46 | ≈0.3 MB |
| `.codely-cli/auto-saves/` 2 件聊天历史档案（审计判定=不可再生用户历史，密钥模式扫描全假阳性：`task-notification` 撞 `sk-` 模式 + akshare 空默认参数签名） | 2 | ≈30 MB |
| **合计** | **≈10,568** | **≈1.22 GB** |

不上传：`.codely-cli/settings.json`（机内局部配置）；`mkt_crypto/cache/`（15.2MB Gate.io 抓取物，名称似缓存但保守保留在库内）。

## 三、>95MB 单件扫描

0 件命中——无排除项（GitHub 100MB 硬限不触发，无需 LFS）。

## 四、执行实况与让位记录（14:35 终局）

- **清理已执行（14:32）**：cache/live/logs/fit_matrix 双 log 共 101 件 ≈6.35GB 全删，与用户 triage 标记（cache=可弃、live=陈过时）一致；清理后 Money02=1.20GB/10,968 件。
- **通道实测（供 bars 处置决策）**：HTTPS 无 PAT 不可用；SSH via Clash=唯一通道，round 20/22 实测 ≈66KiB/s；bars 1.087GB 推送预估 ≈4.7h。
- **让位（14:27:10 事件）**：本机用户交互式 GUI 会话（codely ACP，14:19:41 起）亲手执行 triage 并提交 83be5a3（521 文件=全部小件 ~87MB + .gitignore 选择性排除 + Money02/ARCHIVE_MANIFEST.md），**裁定 bars=仅本机归档**（移动硬盘/局域网/独立私库三路径，见其 manifest）。用户亲手裁定优先于一切转发指令 → 循环轮让位：**bars 不推、.gitignore 不动、文档同步不做、83be5a3 不代推**（用户会话在世，87MB 推送可能正在途，代推=撞锁风险）。
- 上文原 §四/§五（bars 分批上传方案：5 批 ≤1.5GB、探针批实测、后台顺序推、循环任务暂停窗）**作废留档**——若用户日后改令要传 bars，该方案可直接复用。

—— bm-b · 2026-09-23 15:0x
