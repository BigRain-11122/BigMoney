# QA — r2163：两条 (check, run) 对的 STALE 契约

日期：2026-11-27 05:4x–06:1x+0800
机器：bm-c
范围：`scripts/etf_book_premium_phases.py`、`scripts/etf_book_year_caliber.py`

## 1. 要修的是什么

`results/chain_contract_word_audit.json` 的 21 条候选中，这两条在链 `Tools/s6_chain_bmc.py` 里本来
就是 `(check, run)` 一对（重算分别约 7 分钟 / 74 秒一直挂在腿上），但两个 `check()` 都**只从面自己
的算术重派生判词**——上游面推进、面板滚 bar 时它们不会说自己过期。而 `run_leg::_repairable` 只在探针
文本里出现 `stale` / `face missing` 时才付钱重生，于是这两条腿红着并永远红，共享面冻在旧的一天。

实测证据（修前）：`python scripts/etf_book_year_caliber.py check` → `STALE: the published arm
re-derived on 2026-11-26, this face proved identity on 2026-10-23` 一旦接上 drift 就立刻暴露——
这个面自 10-23 起一直印绿。

## 2. 改了什么

### etf_book_premium_phases.py

- 新增 `UPSTREAM = results/etf_book_production/latest.json` 与 `upstream_reads()`（一次小 JSON 读，
  不碰面板）、`drift()`：比 `evidence_cutoff` 与 `n12_vt08.full.cagr`（`PUBLISHED_TOL=1e-6`）。
- `build()` 的产物新增 `upstream` 块（artifact / evidence_cutoff / published_cagr / ts）。
- `check()` 改成三态：drift 非空 → 逐句印 STALE + `CHECK_STALE` + rc3；否则原 `check_payload` 逐项
  比对（真算错仍抛 SystemExit → rc1）。
- 缺锚（旧面没有 `upstream`）→ `STALE: this face does not record which book it compared against
  -- rebuild it`，不再沉默读成干净。
- selftest 26 → **37 腿**：drift 四态 + 端到端（拷真面、置 `globals()["OUT_JSON"]`、调真 `check()`，
  原样 rc0 / 锚前移一格 rc3）。
- 顺带修掉 selftest 内部一处命名遮蔽（局部 `drift` 变量改成 `retuned`，否则模块级函数不可见）。

### etf_book_year_caliber.py

- 新增 `upstream_reads()`（`C.load_published`）与 `drift()`：比 `published_arm.as_of` 与
  `numbers{cagr,sharpe,maxdd}`（容差用该模块自己的 `PUBLISHED_ULP`）。
- `check(up="disk")` 三态同上；缺锚 → 要求一次重生。
- **run 的 phase identity 加 vintage 门**：r1425 的冻结 receipt（11-22：5,285 bars / 1,528 names）
  与本次面板（5,289 / 1,536）不同代时，旧逻辑 `REFUSED` rc3 使面永远停在旧 bar；改为印
  `phase identity SKIPPED: receipt priced 5285 bars / 1528 names, this run 5289 / 1536` 并写进面，
  **同一代而数字不等仍然 refuse**。
- selftest 33 → **40 腿**：drift 五态 + 端到端（真面副本，绿 / 锚退到 1999-01-01 → rc3）。

## 3. 验证（全部实跑）

| 检查 | 结果 |
|---|---|
| `etf_book_premium_phases.py --selftest` | **37/37 PASS**（4.5s） |
| `etf_book_premium_phases.py run` | 落盘 11-26 面板（5289 bars / 1536 names），verdict `level: positive on 4/4 phases (median +6.64pp/yr)` |
| `etf_book_premium_phases.py --check` | `OK {'phases': 4, 'positive_phases': 4, 'median_pp': 6.64}` rc0 |
| `etf_book_year_caliber.py selftest` | **40/40 PASS**（1.5s） |
| `etf_book_year_caliber.py run` | 落盘 11-26；identity dev `{cagr:0.0, sharpe:0.0, maxdd:0.0}` ok=True；phase identity 如实记 vintage 差 |
| `etf_book_year_caliber.py check` | `check PASS: primary=effective_years composite=FAIL` rc0 |
| 链腿 `--only=premium_phases,year_caliber` | **2/2 rc0**，各 1.2s（结算态） |
| **自愈实测** | 毒化 `published_arm.as_of`→2026-10-23 → check rc3+STALE → 链腿印 `76.1s check PASS ... +refresh(rc=0,73.7s)` → 面回到 11-26 |
| `chain_contract_word_audit.py run/--check/--selftest` | n_candidates **21→19**、`ok:true, n_current:19`、8/8 |

## 4. 如实记的未做 / 未验证

1. **全量冒烟本轮未跑完**（05:40 起后台，到 06:1x 仍在跑），故不宣称套件总数。观测到的一条红
   `chain contract-word audit (live column still matches its scripts)` = 本面新旧交替期，run 后
   `--check ok:true` 已清。
2. 本轮未跑 S6 全链（只跑两条点名单腿 + 自愈实测）。
3. 余额 **19 条**结构风险腿只在审计面 rows 里点名，本轮未动。
4. `premium_phases` 的重生成本很高（单次 run 约 7 分钟 / 4 phases）；本轮只在面板推进时才付。
5. r2159 余下三条欠账（CEO 页 declared starting book、bets/derisk 无链腿、ah_panel 采样尾）仍未动。
