"""r860 bm-a: append 3 pit entries to research/pit-pool-edit.md
(fresh-read-modify-write per multi-writer ledger law; r859 append pattern)."""
import io

PITS = [
    "- [2026-10-08 03:5x r860 bm-a] **入池 runner_args 逗号串坑（submit 存 1 元素 list -> launcher 单 argv -> argparse 即退 -> fuse 假崩链）**：--runner-args 传逗号连写串时 submit 存成单元素 list（W16-SCREEN 先例=5 元素 list），launcher 把整串当一个 argv 传 runner -> argparse invalid choice 即退（诚实零烧 checkpoint 零行）；sig=runner|逗号join(args) —— args 修好后 join 恰同串=fuse 拒不随 args 修解除。How to apply：入池 --runner-args 一律传 JSON 数组串（如 '[\"judge\",\"--shard\",\"0\",\"--shards\",\"1\"]'，与 --data-deps 同律）；入池回执必断言 runner_args == 期望 split list；此类假崩 fuse 解除=r824 W14-screen manual tombstone 范式（reason 记 root-cause+old sha+零烧实证；r860 W16-JUDGE 实弹复刻）。\n",
    "- [2026-10-08 03:5x r860 bm-a] **trial-labor runner 无 worker-claim 件=daemon 收割够不着 -> 25min 窗完成烧误记 crash（W13 shard 注明坑的 W16 再实证+正典收口三件套）**：screen/judge 烧录成功退出但池面 shard 停 ready（trial-labor 独立 runner 不写 pool_claims 握手件=收割缺半），25min confirm 把完成烧记 crash 入 fuse。正典收口三件套=①tombstone 假崩 sig（reason=完成实证+gap 出处）②观察轮写 worker-claim 件（W14-SCREEN bm-c 格式：machine_id/state=closed/pid/started/closed_at/outcome/exit_code/result_ref）③tick 收割翻面 entry+shard done+harvest flip 自提交。How to apply：trial-labor 单分片烧完后观察轮主动做 claim 件三件套勿等 25min 假崩窗；W16-SCREEN 实证 373/373 03:37 完成 -> 03:58 翻面。\n",
    "- [2026-10-08 03:4x r860 bm-a] **claim 提交后 4 秒 compact 覆写丢 owner_since（陈旧合并视图快照二次写=r605/r608 族新面）**：claim-write（multi-line+owner_since）-> tick 自提交 -> 03:32:12 同 tick 第二写（merged-view 序列化 compact 形态）用 claim 前快照覆写 shared+lane 两面 = owner_since 静默回退 owner=null（r859 轮首已见同窗脏面未定位）。How to apply：轮首见池面脏且 diff=纯 claim 字段回退+格式重排（零新信息判据=diff --stat 插删行数与字段回退一致）-> origin-verbatim checkout 恢复两文件再续做；本例恢复后 JUDGE 入池 +17/-1 零损，下轮 daemon 并源（lane 一致+兄弟 lane 无该条目）不再回退。\n",
]

path = r"research\pit-pool-edit.md"
raw = io.open(path, encoding="utf-8", newline="").read()
assert "r860 bm-a" not in raw, "r860 pits already appended"
sep = "\r\n" if "\r\n" in raw else "\n"
add = sep.join(p.strip("\n") for p in PITS)
if not raw.endswith("\n"):
    raw += sep
new = raw + add + sep
io.open(path, "w", encoding="utf-8", newline="").write(new)

chk = io.open(path, encoding="utf-8", newline="").read()
for probe in ("runner_args 逗号串坑", "worker-claim 件=daemon 收割够不着",
              "compact 覆写丢 owner_since"):
    assert probe in chk, probe
print("3 pits appended to pit-pool-edit.md |", len(raw), "->", len(chk), "bytes")
