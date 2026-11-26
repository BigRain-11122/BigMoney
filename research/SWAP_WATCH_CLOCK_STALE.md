# 换票的两只表，谁都不说自己过期

r1465 给这张桌面报了一个数：把同一篮子从 159501/513100 换到便宜的 159513，多拿 9,762 元篮子。
r1522 再把「换回来要多少钱」标了价（一次交换 0.16 pp / 两次 0.32 pp）。两个面都在链上，都印
CHECK_OK —— 直到面板前进一根 bar。

## 两个面在过去是怎么冻住的

| 面 | check 在做什么 | 输入一动时它印什么 | 后果 |
|---|---|---|---|
| `etf_book_swap_trigger` | 从 gap 面**整条重生**再逐字段比 | `CHECK_FAIL: verdict, today_gap_pp, …` | 链只在探针自己说 **STALE** 时才付钱（`run_leg::_repairable`, r1850）→ 永久红，面停在上一个 session |
| `etf_book_swap_toll` | 只在自己已发布的 rows 上做算术（`want_in = notional*bp/10000*2`） | `CHECK_OK rows=0` | 面**从不看外面**，于是它会一直绿着报昨天的动作（r1935 的「自检只重算自己」） |

第二种更坏：红至少还会被人看见，绿着冻住的成本面会被当成今天可下单的过路费。

## 修法：把输入的身份写进面，check 先比身份

两个脚本各自记录自己被定价的那份文件，按**字节**（r1311：不是按日期，同日改写也算动）：

```python
face["inputs"] = {"gap": {"path": "results/etf_book_sibling_gap.json", "sha256": "…"}}
# toll: {"stack": {…}, "trigger": {…}}
```

`check()` 开头只问一件事：**我记的那份字节还是盘上那份吗**

* 不是 → `CHECK_STALE: …` / `STALE …`，rc **3**，并且**不再重生**（重生是写者的活；在这里
  重生只会把一个上游事件印成一个幻影缺陷）；
* 是 → 才开始逐字段比对，不符仍是 `CHECK_FAIL` rc 1（r1934 双词钉死：真缺陷不许借 STALE 逃）；
* 面里没有指纹 → 也算 STALE（「我不知道在跟谁比」不是「我很好」，r2163 卡④ 同族）。

链序本来是对的：`swap_trigger`（第 2207 行）在 `swap_toll`（2222）之前，`sibling_gap` 更前。

## 实测

* `etf_book_swap_trigger.py --selftest` **33/33**（新增 6 腿，其中 2 条端到端：毒化副本 → rc3 且
  出现 STALE；同措辞下改一个 pair 的 toll_pp → rc1 `CHECK_FAIL` 且**没有** STALE）
* `etf_book_swap_toll.py --selftest` **27/27**（新增 6 腿，含 L26/L27 同一对端到端）
* 真面上的探针 `results/_r2163bmc_swap_stale_probe.py` **4/4**：
  * `trigger` 钉一个不是盘上的 gap sha → `CHECK_STALE: the gap face … was re-derived`，rc 3，
    恢复后 sha 与原字节**逐位相同**
  * `toll` 钉一个不是盘上的 stack sha → `STALE the stack face …`，rc 3，恢复后逐位相同
  * 两个面在干净输入下 rc 0 且**不**出现 STALE（一条永远喊 STALE 的面过不了这一腿）
* 链：`--only=swap_trigger,swap_toll` → **2/2 rc0**（1.3s / 0.1s）
* 自愈付钱实证：把已发布 trigger 面的 gap sha 钉成 `0…0` → 同一把 `--only=…` 印
  `swap_trigger 2.7s CHECK_OK … +refresh(rc=0,1.3s)` —— 这根腿不再永久红
* 契约词审计面复算：`n_candidates` **19 → 17**，`n_legs 392 / n_writer_legs 136 / n_permanent_red 0`，
  `--check ok:true`

## 边界（如实）

* `swap_toll` 现在只认「stack / trigger 的字节动没动」。如果两份面都没动而票面（`etf_book_order/
  latest.json`）换了，它仍然读不到——它的 `as_of` 取自 stack 面，这条链上票面是更上游的事。
* 其余 17 条结构风险腿未动（`results/chain_contract_word_audit.json` 逐条点名）。
* 本轮没有跑完整 S6 链与完整冒烟（同树另有执行体在飞，见 QA 文件的 S0 段）。
