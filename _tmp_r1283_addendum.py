import json, os
from datetime import datetime

ROOT = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney"
os.chdir(ROOT)
now = datetime.now().astimezone()
iso = now.strftime("%Y-%m-%dT%H:%M:%S%z")
iso = iso[:-2] + ":" + iso[-2:]

# What origin already did while this window was working: bm-c r1518 "the executed book stops being
# overwritten by the pre-trade mark" touched scripts/etf_book_positions.py (+74) and the positions face.
# This window's face was computed on the LOCAL (pre-r1518) positions face, so its numbers must be
# re-derived on the merged tree before the finding can be called new. Say it in the report, not later.
add = (
    "\n| {ts} | r1283 addendum | **撞车披露（诚实）**：本窗开工时本地落后 origin 6 个 commit，"
    "bm-c 的 **r1518「one bar, one account fact —— 执行账不再被换手前估值覆盖」**（c95b74e092，"
    "`scripts/etf_book_positions.py` +74 行 + `results/etf_book_positions*` 重写 + 一张方法论卡）"
    "动的正是本窗这张面的同一块地。所以本窗 `etf_book_base_basis_audit` 的两个 k（0.397063 / 0.392405）"
    "是**在本地旧版 positions 面上算出来的**：结论（差的是分母不是仓位）方向仍成立且已写成 E518，"
    "但**必须在合并后的树上重 derive 之后才可当新发现报**——本窗不宣称那部分为原创。"
    "**送达**：工作树有 ~500 个继承链产物未提交，rebase 风险高于收益，按纪律推回退分支 "
    "`machine/bm-a-r1283`（禁 force-push），下一轮先 rebase 再重 derive；本机未达 origin commit 数=7（含本提交），"
    "跨两轮即红旗，已入下轮首查。\n"
).replace("{ts}", iso)

with open("round_reports-bm-a.md", "a", encoding="utf-8") as fh:
    fh.write(add)

sp = "state-bm-a.json"
with open(sp, "r", encoding="utf-8") as fh:
    st = json.load(fh)
st["updated"] = iso
st["r1283_collision"] = ("origin r1518 (c95b74e092, bm-c) fixed the same face: 'the executed book stops being "
                         "overwritten by the pre-trade mark' (+74 lines in scripts/etf_book_positions.py). This "
                         "window's audit numbers were computed on the LOCAL pre-r1518 positions face -> the "
                         "verdict direction (denominator, not position) stands and is carded E518, but it may "
                         "not be claimed as new until re-derived on the merged tree. Delivered on fallback "
                         "branch machine/bm-a-r1283 because ~500 inherited chain artifacts are uncommitted.")
with open(sp, "w", encoding="utf-8") as fh:
    json.dump(st, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
print("ok", iso)
