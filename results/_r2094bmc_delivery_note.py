p = "round_reports-bm-c.md"
row = ("2026-11-25T17:3x+08:00 | r2094-delivered | bm-c | 送达补记：commit **8c516d2712** 已直推 "
       "origin/main（5fa7014352..8c516d2712，无 non-FF）；fetch 后 `git rev-list --left-right --count "
       "origin/main...HEAD` = **0/0**；`git ls-tree -r --name-only origin/main` 五件新增面全在位"
       "（scripts/idx_fut_carry_always_on_price.py、results/idx_fut_carry_always_on_price.json、"
       "research/IDX_FUT_CARRY_ALWAYS_ON_PRICE.md、qa/always-on-price-r2094.md、负控 "
       "results/_r2094bmc_always_on_price_negative.py）→ 本地未达 origin commit 数=0。"
       " | 记账：本行 1 处（累计 2；state/心跳由对端宿主在写，本窗未碰）\n")
raw = open(p, "rb").read()
assert raw.endswith(b"\n"), "ledger tail lacks newline"
with open(p, "a", encoding="utf-8", newline="") as fh:
    fh.write(row)
print("appended")
