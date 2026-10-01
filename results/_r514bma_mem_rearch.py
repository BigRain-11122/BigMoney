"""r514 bm-a: hot-cold re-archivation (D-20260925-01 4th / D-20260924-01
paradigm). CODELY.md crossed the 50KB waterline (50,415B) -- mandated
this-window re-archivation of flow-type entries into
research/memory-archive/202610.md with line-level zero-loss verification.
Also appends two NEW pitfall entries (hot layer, E1-grade)."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCH = os.path.join(ROOT, "research", "memory-archive", "202610.md")

src = open(CODELY, encoding="utf-8", newline="").read()
orig_size = os.path.getsize(CODELY)
lines = src.splitlines(keepends=True)

# --- the 5 flow/receipt lines to migrate (matched by unique prefix) ------
PREFIXES = [
    "- [2026-09-30 23:4x r483 bm-b] LOWAMP-P1 s1 冻结交付",
    "- [2026-09-30 23:5x r484 bm-b] T-133 s2 常供面切片认领与开工同轮",
    "- [2026-10-01 04:5x r492 bm-b] LOWAMP-P1 判负收口+E1 完整性旗标",
    "- [2026-10-01 r496 bm-a] O-2026-09-30-2355 多核强制令回执",
    "- [2026-10-01 11:2x r511 bm-a] O-2026-10-01-1035 CEO 直令回执",
]

migrated = []
for pre in PREFIXES:
    hits = [l for l in lines if l.startswith(pre)]
    assert len(hits) == 1, f"prefix match {len(hits)}: {pre[:40]}"
    migrated.append(hits[0])

eol = "\r\n" if src.count("\r\n") > src.count("\n") - src.count("\r\n") else "\n"
if lines and not lines[-1].endswith(("\n", "\r\n")):
    tail_nonl = True
else:
    tail_nonl = False

# --- two new pitfall entries (hot layer) --------------------------------
NEW1 = (
    "- [2026-10-01 12:5x r514 bm-a] merge_lane_views resolve/settle 缩进探针双坑"
    "（池 21k 行整翻面实弹·当场修复+验）：resolve 写出面硬编码 indent=1——池真形状="
    "flat-0-key+CRLF（r509 载面），一用即整文件翻面（本窗 rebase 撞池实弹：resolver 落 "
    "indent1→按父 blob 格式重排+amend 治愈；重排后与父字节恒等=本地池改面已被 origin "
    "外科版吸收的 AA 收敛证据）；姊妹坑=settle 路径探针测「首个非空行」=开括号 { 恒列 0"
    "→恒抹一切缩进（r499 既有探针的盲区）。修法=首 KEY 行缩进探针 _probe_key_indent"
    "（resolve+settle 双路径接入）+写出面 indent=probe；selftest 0 FAIL+真跑双例（池面 "
    "indent0/CRLF/parse 过+探针 ind0/1/2 三态直测）。How to apply：一切共享 JSON 的 "
    "resolve/settle 写出禁硬编码 indent，一律探 base 侧首 KEY 行缩进镜像；冲突解后必 "
    "git diff --stat 外科断言（超百行=格式翻面红旗，即回滚重走文本路）。"
)
NEW2 = (
    "- [2026-10-01 12:4x r514 bm-a] 池登记 id 镜像 _entry_of 核验律（r494 键漂移的"
    "池登记面·推送前抓回）：P2 池登记初稿用 cell 原文 LA-REP 带连字符，runner _entry_of "
    "计算=LAREP（replace('-','')）——登记面与 runner 计算面不同源即握手错 entry=幽灵面族"
    "（r488）。How to apply：新批池登记 id/shard_key 一律 import runner._entry_of 程序化 "
    "derive+逐位断言后落池，禁手拼字符串。"
)

POINTER = (
    "- 冷层指针（r514 合并·指针合并归档 r444 范式）：r483 bm-b LOWAMP-P1 s1 冻结交付行"
    "+r484 bm-b T-133 s2 认领开工行+r492 bm-b LOWAMP-P1 判负收口+E1 旗标行+r496 bm-a "
    "O-2355 多核强制令回执行+r511 bm-a O-1035 CEO 股票炉令回执行——五条全文 verbatim="
    "archive 202610.md『热冷整编 2026-10-01 r514 bm-a 窗批』节。"
)

# --- build archive content (verbatim migration) -------------------------
arch_header = (
    "# BigMoney 记忆冷层归档 2026-10（research/memory-archive/202610.md）\n\n"
    "## 热冷整编 2026-10-01 r514 bm-a 窗批\n\n"
    "（D-20260925-01④ 50KB 水位触发·D-20260924-01 范式·行级零丢失校验；"
    "流水/回执五行自 CODELY.md 热层 verbatim 迁入，坑律/细则全留热层）\n\n"
)
arch_body = arch_header + "".join(
    l if l.endswith(("\n", "\r\n")) else l + "\n" for l in migrated)
if os.path.exists(ARCH):
    prev = open(ARCH, encoding="utf-8").read()
    marker = "热冷整编 2026-10-01 r514 bm-a 窗批"
    if marker in prev:
        print("archive section already written (first-run residue) -- skip append")
    else:
        arch_body = prev + "\n" + arch_body
open(ARCH, "w", encoding="utf-8", newline="").write(arch_body)

# zero-loss check A: every migrated line byte-verbatim in archive
arch_text = open(ARCH, encoding="utf-8", newline="").read()
for l in migrated:
    core = l.rstrip("\r\n")
    assert core in arch_text, f"archive missing: {core[:50]}"

# --- rewrite CODELY.md: drop migrated, insert pointer, append new -------
out_lines = []
inserted = False
for l in lines:
    if any(l is m for m in migrated):
        if not inserted:
            out_lines.append(POINTER + eol)
            inserted = True
        continue
    out_lines.append(l)
assert inserted, "pointer insertion failed"
if out_lines and not out_lines[-1].endswith(("\n", "\r\n")):
    out_lines[-1] = out_lines[-1] + eol
if out_lines[-1].strip():
    out_lines.append(eol if out_lines else "")
out_lines.append(NEW1 + eol)
out_lines.append(NEW2 + eol)
new_src = "".join(out_lines)
open(CODELY, "w", encoding="utf-8", newline="").write(new_src)

# --- verification -------------------------------------------------------
new_size = os.path.getsize(CODELY)
migrated_bytes = sum(len(m.encode("utf-8")) for m in migrated)
zero_loss = all(
    m.rstrip("\r\n") in new_src.replace("\r\n", "\n") for m in []
)  # migrated lines must be GONE from hot (they are), present in archive (checked A)
hot_removed = all(m.rstrip("\r\n") not in new_src for m in migrated)
print(f"orig={orig_size}B migrated={migrated_bytes}B new={new_size}B")
print(f"migrated lines in archive: 5/5 verbatim OK")
print(f"migrated lines gone from hot: {hot_removed}")
print(f"under 50KB waterline: {new_size < 50 * 1024}")
nl_hot = len(new_src.splitlines())
print(f"lines: {len(lines)} -> {nl_hot}")
assert hot_removed and new_size < 50 * 1024
print("RE-ARCHIVATION OK")
