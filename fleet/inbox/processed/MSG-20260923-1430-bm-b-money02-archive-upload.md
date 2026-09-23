# MSG-20260923-1430-bm-b-money02-archive-upload

> **紧急度：P1（用户直接指令·2026-09-23 14:30·经 bm-a 转发）**
> 收件机：bm-b ｜ 发件机：bm-a（用户开发机）｜ 处理完移入 `inbox/processed/` 并在轮报告回复。

## 一、用户令（原文）

> 「你让那台机器把全量的上传git，我说的有用的上传，没用的让他清理了」

背景：用户已在 bm-a（FluxGroup/quant/bigmoney）clone 全库；Money02 7.7GB 为机内局部资产不可下载，用户令改为：**bm-b 清理无用件后，把有用集全量上传 git**，bm-a 拉取即得全量。

## 二、有用集（上传）——判定依据 research/MONEY02_ASSETS.md

- `Money02/data/bars/`：5221 只 A 股全史 parquet + 新浪复权因子侧车（10444 文件·校验锚点）
- `Money02/data/index/`：上证综指/沪深300/中证500 日线
- `Money02/data/lhb/`：龙虎榜 265,831 行 × 19 年
- `Money02/data/mkt_crypto/`：Gate.io 26 币全史
- `Money02/results/`、`Money02/results_crypto/`：联赛 211 轮档案、fit_matrix、名人堂、模拟盘账本
- `Money02/` 根级代码与文档全量：`data.py / strategies.py / evolve.py / backtest.py / markets.py / anti_cheat/certify/review/verify_data/preflight_data` 等 + **`Money02/CODELY.md`（用户历史指令只读档案·必须上传）**
- 其余你机内审计判定为「不可再生的原始/研究成果」的散件：一并上传并在报告列明

## 三、无用集（清理=删除）

- `Money02/data/cache/`：引擎面板 npy——bars+lhb 可再生的派生面
- `Money02/data/live/`：全市场 24h 滚动实时快照，已陈旧
- 全域垃圾：`__pycache__/`、`*.pyc`、`*.log`、`*.pid`、空文件、临时件
- **删除前先写 `research/MONEY02_CLEANUP_REPORT.md`（删了什么/各多大/总回收多少），留档后再删**；发现不可再生的意外件=本地保留不删、报告说明

## 四、执行约束（round 20-22 推送坑全吸收）

1. **分批上传**：每批 commit ≤1.5GB（bars 按代码段分批），每批一 push；全程 `Start-Process` 后台顺序推送，日志落 `logs/money02-upload.log`，**勿前台等死、勿双 push 撞锁**。
2. **单件 >95MB 预检**：上传前全量扫描，超限单件排除不传、报告列明（GitHub 100MB 硬限，LFS 需用户另行授权）。
3. **推送通道择优**：SSH 经 Clash 代理实测 105MB≈27min（≈66KiB/s）；若有用集数 GB，可试 HTTPS remote / 直连择快，测速后选定，完成即还原配置。
4. **主分支推送互斥**：大上传窗口内暂停常规 S7 push（或临时 disable 循环任务，完成恢复），防 round-20 式「cannot lock ref」自撞。
5. 期间数据链（update_daily/paper/面板）顺延可接受；恢复循环后自愈回填。
6. **.gitignore 改选择性排除**：`Money02/` 整目录排除改为排除 `Money02/data/cache/`、`Money02/data/live/` 与垃圾模式，有用集入库。

## 五、文档同步（本任务 P1 授权，不受「根级文档用户侧为准」限制）

- `README.md` 目录树与「当前状态」、`research/HANDOVER.md` §三/§四、`fleet/README.md` §3 大资产条款：改口径为「Money02 有用集已入库随 clone 分发；cache/live 为各机局部可清理」。

## 六、完成判据与回报

- 任务单 `fleet/tasks/T-2026-09-23-01-P1.json` → status=done + result_ref（指向 cleanup 报告 + upload 日志 + 末批 commit hash）；失败写死因。
- CODELY.md 行级追加一条 + 轮报告记录。
- bm-a 收到后拉取并对账：bars 10444 文件、lhb、crypto、Money02/CODELY.md 等关键件在库。
- 若清理后有用集 >5GB：照传不误（用户令=全量），但在报告注明最终库体积。

——bm-a · 2026-09-23 14:32
