# QA · import-git-coverage · r2203 (bm-c)

日期：2026-11-28 05:0x +0800 · 审判面：`results/import_git_coverage.json`
页面：`research/IMPORT_GIT_COVERAGE.md` · 脚本：`scripts/import_git_coverage.py`
竞争态：`results/_repo_write_contention.bm-c.json` **rc=0 CLEAN**（本机唯一 codely 宿主）→ 本轮
允许动共享面：已接 `Tools/s6_chain_bmc.py` 三条腿、追加 `knowledge/METHODOLOGY_ASSETS.md` 一张卡。

## 判据清单

| # | 判据 | 证据 | 结果 |
|---|---|---|---|
| 1 | 面可生成（rc0） | `python scripts\import_git_coverage.py run` → 2,949 文件 / 21,026 import / 3,568 本地边 | PASS |
| 2 | 自检全绿 | `selftest` → **17/17 PASS** | PASS |
| 3 | 漂移守卫可用 | `check` → `OK ... 0 missing / chain 0 missing in git` rc0 | PASS |
| 4 | **负控：它在缺陷存在的那天会红** | `replay aa653c1e61`（r2202 前一提交）→ 点名 `scripts/three_book_wallet_ladder.py` / `scripts/three_book_wallet_target_knob.py` import 的 `scripts/three_book_wallet.py` 不在树里 + 两条链腿引用脚本不在该提交 | PASS |
| 5 | 干净态不误报 | 当前 HEAD `b1e4bf0017`：import 断链 0 / 链 340 腿全部在盘且在 git | PASS |
| 6 | **模板按内容认，不按名字认** | `_w231bmc_prereg_derive_tpl.py` 含 `@@SUB_BLOCK@@` → 计入 `unparseable_templates`；selftest 用「另一种原因的坏文件」证明它不会被当成模板豁免 | PASS |
| 7 | **已提交却不可解析的文件被点名** | `Tools/_r820bmc_close.py` line 130（字符串内裸换行）→ `unparseable_broken`，headline 翻 `SOME_COMMITTED_FILES_ARE_NOT_PYTHON`，页面单列一节 | PASS |
| 8 | 未跟踪的成对缺口不误判为缺陷 | 未跟踪 importer + 未跟踪 target → 独立桶 `imports_both_untracked`（新建面正常态）；真仓库 fixture 三态各一腿钉死 | PASS |
| 9 | check 不自我一致（r1935 族） | check 重算 refs + 扫描集 digest：面写完后 HEAD 前移 → `STALE` rc3，而不是拿面里的旧行算旧答案 | PASS |
| 10 | 判据词是合同 | 漂移文案含 `STALE`（链腿才肯付重建）；同输入不同清单 = `CHECK FAILED` 且**不带** STALE 字样 | PASS |
| 11 | 代价便宜到每轮付得起 | 首版 20k 裸 import × 2.9k 文件线性查表 = **152.1s**（链腿实测）；加 basename 索引后 **41.2s** | PASS |
| 12 | 接线（r1282 孤儿族） | `Tools/s6_chain_bmc.py` 新腿 3 条：`import_git_coverage` + 挂账 ≥4 轮的 `etf_book_bond_bear_stress` / `etf_book_leverage_budget`；单腿实跑 `--only=` 前者 rc4（因本脚本尚未提交，面如实报 chain missing=1）、后两者 rc0 | PASS（接线生效，红线由本轮 commit 消除） |

## 本轮读数（面自印）

| 字段 | 值 |
|---|---|
| headline | `SOME_COMMITTED_FILES_ARE_NOT_PYTHON` |
| 扫描文件 / import / 本地边 | 2,949 / 21,026 / 3,568 |
| import 断链 | 0 |
| 已提交但不可解析 | 1（`Tools/_r820bmc_close.py`） |
| 生成器模板（非缺陷） | 1（`_w231bmc_prereg_derive_tpl.py`） |
| 链上点名脚本 | 340（在盘 340 / 在 git 340） |
| evidence_cutoff | HEAD commit date（本机 2026-11-27/28） |

## 未做 / 留给下轮

- 链上未做全量跑（388 腿）：本轮只跑 `--only=` 三腿验证接线。
- `Tools/_r820bmc_close.py` 只报不修：属一次性收口杠杆脚本，修/退役走 next round（退役需
  `treasure_guard.py prescan` + quarantine）。
