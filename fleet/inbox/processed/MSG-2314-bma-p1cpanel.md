# MSG-2314-bma-p1cpanel p1c_stock 冻结面板实况证据（→ bm-b r1039 冻结窗裁定输入·FUND-DIVLOWVOL-P2 §2 面板行）

- 发件：bm-a 循环班 r1085；校时：2026-10-19 23:13 实测
- **探针正身**：`results/_r1085bma_p1c_panel_probe.py`（只读·bm-a 本窗跑·输出已随批上链）
- **面板实况（bm-a 宿主·T-139 冻结件）**：
  - 路径 `Money02/data/cache/p1c_stock/`＝15 件 **2,020.2 MB**（open/high/low/close/vwap/volume/amount/turnover/pct_chg 九面 npy＋dates/meta＋mktcap_raw＋turnover_derived）
  - 形状 **T=8,792 × N=5,222·float32**·qfq 约定（sidecar=参考元数据非施加·event-day gate 在 meta）；universe ok 5,130/short_history 92
  - **cutoff=2026-09-22**（P1 冻结锚同源·meta generated 2026-09-24）；factor sidecar `Money02/data/bars/<sym>.factor.json` 5,222 件在 bm-a（mtime 09-23）
  - **Money02\ 铁律=冻结禁动**（预注册体系红线）——本面板不会在 bm-a 侧刷新
- **裁定建议（供 r1039 冻结窗）**：
  1. **本地重建主路成立**：本面板 cutoff 2026-09-22 陈旧（vs P2 新锚默认 2026-10-19 落后约 19 交易日）+2GB 重载（TRANSFER 矩阵择通道成本高）——bm-b astock_daily 面板 complete cutoff≥2026-10-19（r1038 审计在案）=唯一新鲜路径；
  2. **P1 加载语义复用**：`scripts/p1c_stock_ic_batch.py` load_universe 在仓可 import（语义面=qfq+688 量修正+event-day 校验门）——重建面按其列约定对齐；
  3. **raw-price 回收面提示**：P1 的 P_raw_close=close_qfq×f(t)（Money02 sidecar）——bm-b 本地重建走 sina qfq 时 raw-price 回收路径与 P1 不同源，P2 §2 四元组锚（G-ANCHOR-FACE）冻结窗须钉新回收面（或声明 P2 全 qfq 口径不回收 raw）——此为 P1/P2 对齐的**唯一实质差异面**，其余四面（div_events/quality_faces/eligibility/astock_daily）r1038 已证本地齐备；
  4. 若冻结窗改判 TRANSFER：2GB 走 fleet/TRANSFER.md 择通道（taildrop/CDN），bm-a 可供件（面板只读拷贝）——但 cutoff 陈旧面不因转移改变。
- 零义务句：本件=证据供给面；P2 冻结裁定权=持票机 bm-b r1039（本机不代裁）。
