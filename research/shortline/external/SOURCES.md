# 外部资产台账（research/shortline/external/）

> 下载日 2026-09-23 · 下载执行=quant 专管会话（CEO 令 O-20260923-1545「去调研，去下载」）
> 纪律：件件带出处；许可状态如实记录；本目录资产=研究参照与实现底料，**生产采纳一律走 G1'/G2 门禁**（firm/RULES.md §2）。

| 文件 | 来源 | 许可 | 说明 |
|---|---|---|---|
| `gtja191_alpha191.py` | github.com/Daic115/alpha191（国泰君安《基于短周期价量特征的多因子选股体系》191 因子社区实现） | **无显式 LICENSE** → 仅内部研究参照+出处注记，禁再分发 | 95KB·191 因子；pandas 宽面板输入（date×symbol），与我方 `engine/factors.py::compute_all` 同构；依赖本目录 `gtja191_lib_*.py`；部分回归类因子可选依赖 qlib rolling ops（缺失时自动降级提示） |
| `gtja191_lib_base.py` / `gtja191_lib_factor_ops.py` / `gtja191_lib_method_attrs.py` | 同上 | 同上 | FactorBase 与算子库（RANK/SMA/TS_RANK/CORR/DECAYLINEAR/REGBETA 等） |
| `gtja191_README.md` | 同上 | 同上 | 用法原文 |
| `worldquant101_alpha101.py` | github.com/OctopusTakopi/toraniko-alpha101 | **MIT**（见 `worldquant101_LICENSE`） | 36.7KB·WorldQuant《101 Formulaic Alphas》全量实现（Kakushadze, arXiv:1601.00991, Wilmott 2016；平均持仓 0.6-6.4 天=短线经典）；**Polars 长表实现** → 作公式权威参照，pandas 适配由研究部做 |
| `worldquant101_LICENSE` / `worldquant101_README.md` | 同上 | MIT | 许可与说明原文 |
| `qlib_alpha158_loader.py` / `qlib_alpha158_handler.py` | github.com/microsoft/qlib（`qlib/contrib/data/loader.py::Alpha158DL` + `handler.py::Alpha158`，文件末次 commit `a7d5a9b500de` 2024-07-05，取于 2026-09-24） | **MIT**（qlib 仓库根 LICENSE） | 21.2KB 两件**逐字节原样** vendored（R59 bm-a·O-1636 外调队「Alpha158 对照导出」专用对照源，**永不 import 执行**——顶部 qlib import 天然防误执行）；158 特征定义层=对照导出对象非计算依赖（DIGEST-20260924-alpha158-comparison；采纳缺口族开批=各自预注册） |

## 参照文献（不下载，引用即够）

- Kakushadze, Z. *101 Formulaic Alphas*. arXiv:1601.00991；Wilmott Magazine 2016(84) 72-80。
- 国泰君安证券金融工程《基于短周期价量特征的多因子选股体系》（GTJA 191 因子原始研报，公开流传版）。
- Microsoft qlib（github.com/microsoft/qlib）：Alpha158/Alpha360 因子集与滚动回归算子——重型框架，仅按需取算子思想，整框架引入=P1。

## 指标库选型结论（2026-09-23 调研）

- **pandas-ta（twopirllc）原仓库已 404**（2026-09-23 实测）→ 不引入。
- 选 **`ta` 库**（github.com/bukosabino/ta）：43 指标·纯 pandas+numpy·MIT·`pip install ta`——研究环境够用；生产不装（内部向量化指标集为生产口径）。
- TA-Lib：C 库依赖安装痛，Windows 折腾成本高，不引入。
