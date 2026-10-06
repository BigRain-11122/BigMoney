# -*- coding: utf-8 -*-
# r658 bm-c S4 memory + D-20261002-06 same-window increment batch.
# Step A (law: new pits enter the main file first): append the r658 pit entry.
# Step B (watermark law, main <=30,720B): migrate r808 (left over from r654
#   pending window) + the fresh r658 entry verbatim -> research/pit-git-resolver.md
#   (resolver/autostash family domain; 2,686B headroom pre-batch).
# Byte-exact extraction from source (zero transcription), byte+sha16
# accounting, zero-loss assertions, receipt per r441/r703/r783/r651/r654 rites.
import hashlib, json, datetime, os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
MAIN = os.path.join(ROOT, "CODELY.md")
TARGET = os.path.join(ROOT, "research", "pit-git-resolver.md")
RECEIPT = os.path.join(ROOT, "results", "_r658bmc_codely_increment.json")
LINE = 30 * 1024  # 30,720B watermark

R658_ENTRY = (
    "- [2026-10-07 06:1x r658 bm-c] **外科恢复面×pull --rebase --autostash EOL pop 冲突坑"
    "（文件集零重叠仍 pop 失败·载荷静默回滚吞回 stash·porcelain 无 UU=隐性失败）**：P0 冲突标记愈合窗"
    "（17 件共享面 parent-blob 二进制精确恢复=bypass git checkout 的 LF→CRLF 转换直写 LF 字节）后 "
    "S0 pull --rebase --autostash：新 origin 提交与恢复面零重叠仍报 applying resulted in conflicts，"
    "pop 半应用（daemon 面 staged 落盘）+17 件恢复面静默回滚污染态+载荷困 autostash。正法（实测治愈·"
    "r642 家族新变体）：①零独占载荷核对（恢复面=git blob 确定性可再生+daemon 面=live-wins+post_review 行"
    "=可复跑→全载荷可再生才许 drop）；②git reset --hard HEAD 净树+git stash drop 弃毒 autostash；"
    "③确定性重放愈合脚本（幂等）；④commit 消息含空格经 silent-git wrapper -m 必炸成 pathspec"
    "（Arguments 原生按空格切分）=一律 -F commitmsg 文件（根目录 _rNNNbmc_commitmsg.txt 既定范式）。"
    "How to apply：外科恢复批后禁 autostash pull（先 commit 再 pull 或 reset-重放）；pop 后必复查恢复面 "
    "marker 计数勿信 porcelain。"
)

def read_bytes(p):
    with open(p, "rb") as f:
        return f.read()

def write_bytes(p, b):
    with open(p, "wb") as f:
        f.write(b)

def eol_of(b):
    return b"\r\n" if b.count(b"\r\n") >= b.count(b"\n") - b.count(b"\r\n") else b"\n"

def sha16(b):
    return hashlib.sha256(b).hexdigest()[:16]

main_b = read_bytes(MAIN)
tgt_b = read_bytes(TARGET)
main_eol, tgt_eol = eol_of(main_b), eol_of(tgt_b)
receipt = {"asof": datetime.datetime.now().astimezone().isoformat(timespec="seconds"),
           "probe": "r658 bm-c S4+increment batch", "line_bytes": LINE,
           "main_before": len(main_b), "target_before": len(tgt_b)}

# --- Step A: append r658 to main (new-pit-first law; in-window transient) ---
main_a = main_b + (main_eol + R658_ENTRY.encode("utf-8") if not main_b.endswith(b"\n")
                  else R658_ENTRY.encode("utf-8") + main_eol)
receipt["stepA_main_after_append"] = len(main_a)

# --- Step B: extract r808 block + r658 block from main, migrate verbatim ---
main_txt = main_a.decode("utf-8")
sep = "\r\n" if main_eol == b"\r\n" else "\n"
mlines = main_txt.split(sep)
r808_idx = [i for i, l in enumerate(mlines) if l.startswith("- [2026-10-07 04:4x r808 bm-a]")]
r658_idx = [i for i, l in enumerate(mlines) if l.startswith("- [2026-10-07 06:1x r658 bm-c]")]
assert len(r808_idx) == 1 and len(r658_idx) == 1, "block locate failed"
r808_block, r658_block = mlines[r808_idx[0]], mlines[r658_idx[0]]
blocks = [("r808-bma-rebase-continue", r808_block.encode("utf-8")),
          ("r658-bmc-autostash-eol-pop", R658_ENTRY.encode("utf-8"))]
receipt["migrated"] = [{"id": i, "bytes": len(b), "sha16": sha16(b)} for i, b in blocks]

# main final = append-state minus both blocks (keep every other line verbatim)
keep = [l for i, l in enumerate(mlines) if i not in (r808_idx[0], r658_idx[0])]
while keep and keep[-1] == "":
    keep.pop()
main_final_b = (sep.join(keep) + sep).encode("utf-8")

# target final = target + both blocks (list-append style, target's own EOL)
tsep = "\r\n" if tgt_eol == b"\r\n" else "\n"
tgt_txt = tgt_b.decode("utf-8")
tlines = [l for l in tgt_txt.split(tsep) if l != ""]
tlines.append(r808_block.replace("\r\n", "").replace("\n", ""))
tlines.append(r658_block.replace("\r\n", "").replace("\n", ""))
tgt_final_b = (tsep.join(tlines) + tsep).encode("utf-8")

# --- zero-loss assertions ---
for i, b in blocks:
    assert b.decode("utf-8").replace("\r\n", "").replace("\n", "") in tgt_final_b.decode("utf-8"), \
        "verbatim-missing: " + i
retained = main_b.decode("utf-8")
for gone in (r808_block,):
    assert gone not in main_final_b.decode("utf-8"), "main still carries migrated block"
    assert gone.replace("\r\n", "").replace("\n", "") in tgt_final_b.decode("utf-8"), "r808 lost"
assert len(main_final_b) <= LINE, "main over line: %d" % len(main_final_b)
assert len(tgt_final_b) <= LINE, "target over line: %d" % len(tgt_final_b)

write_bytes(MAIN, main_final_b)
write_bytes(TARGET, tgt_final_b)
receipt["main_after"] = len(main_final_b)
receipt["target_after"] = len(tgt_final_b)
receipt["asserts"] = {"bytes_in_target_verbatim": True, "main_retained_face_no_migrated_blocks": True,
                       "main_le_line": True, "target_le_line": True}
with open(RECEIPT, "w", encoding="utf-8") as f:
    json.dump(receipt, f, indent=1, ensure_ascii=False)
print(json.dumps({k: receipt[k] for k in
                 ("main_before", "stepA_main_after_append", "main_after",
                  "target_before", "target_after", "migrated")}))
