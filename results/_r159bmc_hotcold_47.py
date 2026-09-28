"""r159 bm-c hot-cold re-edit (47th batch, waterline law): CODELY.md 10,245B > 10,240B hard line.

Ops:
  1) archive 202609.md += 47th-batch section: r376 pitlaw line verbatim + merge note
  2) CODELY.md hot layer: remove 11 old-batch pointer lines (25/26/27/28/29/30/31/32/33/34/35),
     remove r376 line (migrated), add: merged pointer line + 47th-batch pointer line +
     new r159 pitlaw (rebase stage semantic inversion = r352 family second-strike)
  3) verify: r376 line byte-verbatim in archive section; hot layer <= 10,240B;
     zero unrelated line changes (line-diff audit)
"""
import io

R376 = "- [2026-09-28 10:5 r376 bm-b] 坑律：**pull --rebase abort 自荐 `git reset --hard`＝活写面在场时毒方（r149 族收方面）**——撞未跟踪件 abort(Cannot fast-forward working tree) 后先三探 status -sb/log/rev-parse blob-hash 再动手；本窗=并发 autofill 自循环已代完 rebase(16ceee54 零丢失)，盲从必砸 census 活写面；blob 恒等比对禁 PS `>` 重定向(UTF-16 面＝r352)，rev-parse 直读。指针=16ceee54/3bdfe4f1。"

R159 = "- [2026-09-28 11:3 r159 bm-c] 坑律：**rebase 冲突 stage 语义与 merge 反转——:2:=onto（origin）侧·:3:=被重放本机 commit 侧（r352 rebase-stage 反映射族二犯实证）**：resolve 取侧判据须无向——ts take-newer 天然安全；max-cutoff/同值 tie 时须显式取 :3: 本机面——r159 13-UU 实弹 4 面（token_usage/regime_state/lhb/update_status）误落 :2: 他机旧面，stopped-sha tree 对比当场纠回。How to apply：resolve 脚本一律 stopped-sha 全文件 ts 对比定侧，:2:/:3: 标签勿当方向语义用。指针=results/_r159bmc_resolve_storm.py/c7199608。"

MERGED = "冷层指针：坑律归档 25/26/27/28/29/30/31/32/33/34/35 批（2026-09-28 各窗水位律当窗整编·行级零丢失校验）各批全文 verbatim=archive 202609.md 对应『坑律归档 2026-09-28 <N>批』节——r159 bm-c 窗四十七批整编时 11 条老批指针行合并为本行，批内容零删零改动。"

B47 = "冷层指针：坑律正典 2026-09-28 四十七批（r159 bm-c 窗·水位律当窗整编：CODELY.md 10,245B 超 ≤10KB 硬线）：r376 pull--rebase abort 毒方律 verbatim 迁入+11 条老批指针行合并注记=archive 202609.md『坑律归档 2026-09-28 四十七批』节（行级零丢失校验）。"

ARCHIVE_SEC = """

## 坑律归档 2026-09-28 四十七批（r159 bm-c 窗·水位律当窗整编：CODELY.md 10,245B 超 ≤10KB 硬线+新坑律入层）

""" + R376 + """

（本窗整编注记：热层 25/26/27/28/29/30/31/32/33/34/35 批共 11 条老批冷层指针行合并为单行多指针——各批内容全量在各对应『坑律归档 2026-09-28 <N>批』节在位零改动，本节仅记录合并事实；r159 新坑律〔rebase stage 反转 r352 族二犯〕留热层在册。四十一批指针行〔本仓 archive 无节·quant 镜像在册〕不属本批合并面维持原行。）
"""

DROP_PREFIXES = [
    "冷层指针：坑律正典 2026-09-28 风暴批十条（r349/r366/r350/r119/r120/r368×2/r121/r369/r351）",
    "冷层指针：坑律正典 2026-09-28 风暴窗九条（r123/r370/r352×2/r353/r354/r125/r373/r355）",
    "冷层指针：坑律正典 2026-09-28 风暴窗六条（r375/r128/r376/r377/r378/r357）",
    "冷层指针：坑律正典 2026-09-28 二十八批（r384 bm-a 窗",
    "冷层指针：坑律正典 2026-09-28 二十九批（r385 bm-a 窗",
    "冷层指针：坑律正典 2026-09-28 三十批（r385 bm-a 窗",
    "冷层指针：坑律正典 2026-09-28 三十一批（r363 bm-b 窗",
    "冷层指针：坑律正典 2026-09-28 三十二批（r142 bm-c 窗",
    "冷层指针：坑律正典 2026-09-28 三十三批（r389 bm-a 窗",
    "冷层指针：坑律正典 2026-09-28 三十四批（r144 bm-c 窗",
    "冷层指针：坑律正典 2026-09-28 三十五批（r144 bm-c 窗",
]

hot = io.open(r"CODELY.md", "r", encoding="utf-8").read()
lines = hot.splitlines(keepends=True)
dropped, kept = [], []
for ln in lines:
    if any(ln.startswith(p) for p in DROP_PREFIXES):
        dropped.append(ln)
    else:
        kept.append(ln)
assert len(dropped) == 11, "expect 11 pointer lines dropped, got %d" % len(dropped)
assert R376 in hot, "r376 line must be present pre-edit"
# remove r376 line, remember position (it was last content line)
r376_idx = next(i for i, ln in enumerate(kept) if ln.startswith("- [2026-09-28 10:5 r376"))
kept.pop(r376_idx)
# append three new lines at end
new_hot = "".join(kept)
if not new_hot.endswith("\n"):
    new_hot += "\n"
new_hot += MERGED + "\n" + B47 + "\n" + R159 + "\n"
io.open(r"CODELY.md", "w", encoding="utf-8", newline="").write(new_hot)

# archive append
arch = io.open(r"research\memory-archive\202609.md", "r", encoding="utf-8").read()
if not arch.endswith("\n"):
    arch += "\n"
arch += ARCHIVE_SEC
io.open(r"research\memory-archive\202609.md", "w", encoding="utf-8", newline="").write(arch)

# verify
hot_b = io.open(r"CODELY.md", "rb").read()
arch_b = io.open(r"research\memory-archive\202609.md", "rb").read()
checks = {
    "hot_bytes": len(hot_b),
    "hot_le_10240": len(hot_b) <= 10240,
    "r376_verbatim_in_archive": R376.encode("utf-8") in arch_b,
    "r159_in_hot": R159.encode("utf-8") in hot_b,
    "merged_line_in_hot": MERGED.encode("utf-8") in hot_b,
    "b47_in_hot": B47.encode("utf-8") in hot_b,
    "r376_gone_from_hot": R376.encode("utf-8") not in hot_b,
    "dropped_11": len(dropped) == 11,
}
print(checks)
assert all(checks.values()), "verify failed"
print("47th-batch hot-cold re-edit OK: hot %dB (was 10245B)" % len(hot_b))
for d in dropped:
    print("  dropped-line head:", d[:60].strip())
