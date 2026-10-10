"""r830 bm-c: append pit-git-parse entry (group-tree git log local-HEAD stale
history trap) + receipt with bytes/sha16 (r819 direct-write pattern)."""
import hashlib, json, os, time

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
PIT = os.path.join(ROOT, "research", "pit-git-parse.md")
ENTRY = (
    "- [2026-10-10 12:2x r830 bm-c] **集团树 git log 查本地 HEAD 假史坑（D-20260930-13「禁直读工作树」的 log 延伸面）**："
    "K:\\Fluxgroup\\FluxGroup 本地分支常态落后 origin 多 commit——`git log -- <path>` 无 ref 参数=查的是**本地 HEAD 可达史**，"
    "origin 已进提交全不可见（r830 实弹：查 docs/decisions.md 近期提交只见 00:17 883be31，漏 12:11 693ce04 午班拍板批——"
    "水位 sweep 的 blob 读（git show origin/main:path）与 log 查询两结果矛盾即此根因；归因面险些误判「无新 commit=假 delta」）。"
    "正法=集团树历史查询一律显式 `git log origin/main -- <path>`。How to apply：S0.5 delta 归因、orders/decisions 新行定位、"
    "跨机台账考古，凡在集团树上跑 git log 必带 origin/main ref；「blob 有 delta 但 log 查无新 commit」=先想到此坑勿疑机制。\n"
)

with open(PIT, "r", encoding="utf-8") as f:
    before = f.read()
assert ENTRY not in before, "already appended"
with open(PIT, "a", encoding="utf-8", newline="") as f:
    f.write("\n" + ENTRY if not before.endswith("\n") else ENTRY)
with open(PIT, "r", encoding="utf-8") as f:
    after = f.read()

receipt = {
    "round": "r830",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "pit_file": "research/pit-git-parse.md",
    "appended_bytes": len(ENTRY.encode("utf-8")),
    "sha16": hashlib.sha256(ENTRY.encode("utf-8")).hexdigest()[:16],
    "file_bytes_before": len(before.encode("utf-8")),
    "file_bytes_after": len(after.encode("utf-8")),
    "verbatim_in_file": ENTRY.strip() in after,
}
out = os.path.join(ROOT, "results", "_r830bmc_pit_append.json")
with open(out, "w", encoding="utf-8", newline="\n") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps(receipt, ensure_ascii=False))
