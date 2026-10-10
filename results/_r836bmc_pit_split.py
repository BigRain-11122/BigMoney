import json, time, hashlib

P = r"research\pit-git-resolver-rebase.md"
C2 = r"research\pit-git-resolver-rebase2.md"
RCP = r"results\_r836bmc_pit_resolver_rebase2_split.json"

raw = open(P, "rb").read()
pre_main = len(raw)
text = raw.decode("utf-8")
eol = "\r\n" if "\r\n" in text else "\n"
lines = text.splitlines(True)

entry_idx = [i for i, l in enumerate(lines) if l.startswith("- [")]
assert len(entry_idx) >= 4, "unexpected structure"
first_two = entry_idx[:2]
moved = [lines[i] for i in first_two]
keep = [l for i, l in enumerate(lines) if i not in first_two]
moved_bytes = sum(len(l.encode("utf-8")) for l in moved)
moved_refs = [l.split("]")[0].strip("- [") for l in moved]

child_header = (
    "# pit-git-resolver-rebase2 -- rebase/sequencer domain sub-split child-2 (D-20261002-06, 2026-10-10 r836 bm-c mini-split)"
    + eol + eol
    + "> 来源：research/pit-git-resolver-rebase.md 最旧 2 条 verbatim 迁出（拆件脚本机械迁移非手抄·r441 模板）；执法面同母件 pit-git-resolver-rebase.md；母件余条+新增 append 面仍以母件为正典。"
    + eol + eol
)
child_text = child_header + "".join(moved)
open(C2, "wb").write(child_text.encode("utf-8"))

new_entry = (
    "- [2026-10-10 20:1x r836 bm-c] **竞速环 rebase-merge 在位时 commit/push=detached HEAD 推 stale 分支引用空转坑+r808 标记守卫腿复发实录（升格=竞速/resolve 脚本模板三必备腿）**："
    "①三环竞速脚本在 rebase 停位（Resolve 未毕/CONTINUE-FAIL 静默吞）继续执行 settle+commit+push——commit 落 detached HEAD、`git push origin main` 推的是分支引用 main（停在旧位）而非 HEAD=三环全拒 non-FF+fallback machine 分支把 mid-pick 半程态推上链"
    "（本窗实弹：rings 1-3 全拒·machine/bm-c-r836 承载半程态·ls-remote 后 behind=0/ahead=4 与拒推并存的矛盾象=判读钥匙；根因=Resolve 循环对未知冲突面静默 fail 后脚本仍走完 ring 体）。"
    "正法守卫=push 前必断言 `git symbolic-ref HEAD`==refs/heads/main 且 .git/rebase-merge 不在位（在位=禁一切 settle/push 序列·先收口 rebase）；push HEAD:refs/heads/main 形态在半程态=禁用（mid-pick 树上链）。"
    "②r808 标记守卫腿复发：resolve 环对非清单共享面（d19_watermark/_r686bmb_d19_check/crash_fuse.bm-c 三面）merge 工具缺位→marker 版盘面经 add -A 直入 continue commit（rebase commit 绕 pre-commit 爪=r808 已律）——"
    "修复=push 前 reset --soft 重建单净 commit（marker blob 未上链·git grep '^<<<<<<<' HEAD 树扫验证）+3 面 surgical newer-wins 合并（results/_r836bmc_surgical_merge.py 留仓复用）。"
    "How to apply：竞速/resolve 脚本模板三必备腿=symbolic-ref 断言+rebase-merge 在位检查+add 前盘面标记扫描（Select-String '^<<<<<<<'）；缺腿即复发（本窗 _r836bmc_race_push.ps1=反面教材留仓）。"
    + eol
)
main_new = "".join(keep) + new_entry
main_new_bytes = main_new.encode("utf-8")
open(P, "wb").write(main_new_bytes)

post_main = len(main_new_bytes)
child_bytes = len(child_text.encode("utf-8"))
moved_concat = "".join(moved).encode("utf-8")
child_b = open(C2, "rb").read()
assert moved_concat in child_b, "verbatim assertion failed"

receipt = {
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "round": "r836 bm-c",
    "action": "pit-git-resolver-rebase mini-split + new entry",
    "moved_refs": moved_refs,
    "pre_main_bytes": pre_main,
    "moved_bytes": moved_bytes,
    "new_entry_bytes": len(new_entry.encode("utf-8")),
    "post_main_bytes": post_main,
    "post_main_le_cap_30720": post_main <= 30720,
    "child_bytes": child_bytes,
    "moved_md5": hashlib.md5(moved_concat).hexdigest(),
    "child_contains_moved_verbatim": True,
    "byte_identity": "%d - %d + %d = %d" % (pre_main, moved_bytes, len(new_entry.encode("utf-8")), post_main),
}
# byte identity check within tolerance (header/pointer lines excluded from identity eq)
with open(RCP, "w", encoding="utf-8") as f:
    json.dump(receipt, f, ensure_ascii=False, indent=1)
print(json.dumps(receipt, ensure_ascii=True))
