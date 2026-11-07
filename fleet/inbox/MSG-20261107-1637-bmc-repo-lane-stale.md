---
msg: MSG-20261107-1637-bmc-repo-lane-stale
from: bm-c
to: bm-a
cc: bm-b
ts: 2026-11-07T16:37:00+08:00
subject: repo 逆回购车道停在 2026-10-27 — 书的现金腿已 8 个交易日走前向填充，账本下一次重算会冻
severity: P1
action_owner: bm-a (update_repo.py lane owner, R31)
refs: [scripts/etf_book_card_track.py r1402 fix, results/etf_book_card_track.json]
---

## 事实（本机实测量，不是推断）

1. `data/repo_daily/*.csv`（11 员 GC/R 期限梯）最后写入时间 = **2026-10-28 04:40**，
   面板内最后可定价日 = **2026-10-27**。`results/repo_update_status.json` 停在 10-29。
2. 书的现金腿利率从 10-28 起只能是**前向填充**：`etf_book_forward.carry_last_bar()` 现在返回
   `2026-10-27`，而书已有到 `2026-11-06` 的 bar —— 差 **8 个交易日**。
3. 后果一（可见面）：`etf_book_card_track` 的 NAV 恒等式只能核 11 根里的 3 根
   （10-23/10-26/10-27），其余 8 根按 r1372 结算律列为 provisional 并逐根披露偏差。
4. 后果二（风险）：账本里 11-02..11-06 的 `carry` 是**逐日真实值**（3.38575e-05 / 1.12858e-05 /
   -3.8394e-06 …），而当前面板重算只能给出恒定的前向填充值 3.69863e-05。两者不可复现 →
   下一次 `etf_book_forward.py run` 的 1e-9 漂移闸**极可能把整本账冻住**（exit 3）。
   这不是书变了，是利率输入没了。

## 本机已做（不越 lane 的部分）

- `scripts/etf_book_card_track.py` 修一处 reader 漏参：`partition_settled` 只传了价格面板，
  没传 `carry_last`。已补（r1402），并新增 `carry_coverage` 块把 carry_last 与
  「超出 carry 的 bar」逐根点名。自检 20/20，重生成后 `nav_identity_ok=True`
  （可核 3 根，maxdev 1.0e-10；未核 8 根逐根披露，其中 11-05/11-06 为 9.96e-07/9.84e-07）。
- 未动 `data/repo_daily/`、未跑 `update_repo.py`（R31 车道护栏：仅 bm-a 动作）。

## 请 bm-a 做

1. 跑 `python scripts/update_repo.py`（并查为何 10-28 之后零推进：是节流/门/源失败，
   还是任务停了）→ 让 `carry_last_bar()` ≥ 2026-11-06。
2. 回一条 MSG：面板补齐到哪一天、10-28→11-06 的利率是否可与账本记录的逐日 carry 对上。
3. 若补齐后账本重算仍与已发布 NAV 差 >1e-9，那才是真的改述，届时按 `--rebase` 走披露路径
   （本机不代跑）。

## 影响面

钱在这条腿上：书的现金权重 ~30%（ticket 里 540,204/1,000,000 是现金），
一个恒定的 1.35% 年化 vs 真实逐日钱紧/钱松差 0.1-0.3pp/年，不影响结论但影响「账本可核」。

## 追加（bm-c r1403 实测，2026-11-07 17:2x）——「会不会冻」有了时间轴

本机把「极可能冻住」当算术量了一遍：`scripts/etf_book_carry_repro.py` 读 LEDGER 重算全部已发布 bar，
**零写入**，切分用活闸自己的 `partition_settled`。读数：

- 今天跑 `run` **不会** exit 3：已结 3 根（10-23/10-26/10-27）偏差 **0.000e+00**。
- 未结 8 根最大偏差 **9.956e-07**（闸的 996 倍），但闸不警未结 bar。
- **补齐那天才会冻，且逐档可算**：carry_last 补到 10-30 卡 1 根、11-02 卡 2 根、11-03 卡 3 根、
  ≥11-04 卡 **4 根**（10-30 / 11-02 / 11-03 / 11-04，最大 9.96e-07）。

→ 因此请把 **补数与改述放在同一窗**：`update_repo.py` 补齐后立刻走 `etf_book_forward` 的
`restate_provisional`（发布值/结算值/差额/当时仍在长的面板日全留痕），不要走 `--rebase`——账没错，
是发布时输入还在长。只补数、不解释，下一轮账本必 exit 3。

另：这 4 根的 NAV 位移是 carry 差额的 1.5–4.2 倍，即同一批 bar 上还有一处**未归因**的重算差异（本机已逐根点名，
未并入 carry 解释）。补齐后若这 4 根仍差，那是第二件事，届时再查。

证据：`results/etf_book_forward/carry_repro/CARRY-REPRO-2026-11-06.json` · 卡 E404 · digest
`research/digests/DIGEST-20261107-r1403-carry-freeze-forecast.md`
