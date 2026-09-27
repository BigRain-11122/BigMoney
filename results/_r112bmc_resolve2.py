# r112 bm-c rebase storm pass-2 resolver (2 UU: CODELY.md + archive 202609.md)
# same-window batch-number collision: bma r360 batch-32 landed origin-first (d60676fb)
# -> r176 yield law: bmc batch renumbered 32->33; union = bma base + bmc deltas
import json, subprocess, io, sys

def gs(stage, path):
    r = subprocess.run(["git", "show", ":%d:%s" % (stage, path)], capture_output=True)
    if r.returncode != 0 or not r.stdout.strip():
        raise RuntimeError("probe gate FAIL stage=%d path=%s" % (stage, path))
    return r.stdout.decode("utf-8")

def no_real_markers(text):
    # r176/r235 canon: line-START anchored scan -- substring `in` false-positives on
    # legitimate verbatim quotes of markers inside historical pitlaw rows (10 in archive)
    for ln in text.splitlines():
        s = ln.lstrip()
        if s.startswith("<<<<<<<") or s.startswith(">>>>>>>") or s == "=======":
            return False
    return True

# ---- CODELY.md: base = s2 (bma r360 restructure), apply bmc deltas ----
s2, s3 = gs(2, "CODELY.md"), gs(3, "CODELY.md")
lines2 = s2.splitlines()
bma_r360_row = None
bma_r110_ptr = None
for ln in lines2:
    if ln.startswith("- [2026-09-27 22:3x r360 bm-a]"):
        bma_r360_row = ln
    if ln.startswith("- [2026-09-27 22:1x r110 bm-c]") and "三十二批外迁·指针" in ln:
        bma_r110_ptr = ln
assert bma_r360_row, "r360 row not found in s2"
assert bma_r110_ptr, "r110 pointer row not found in s2"

r344_full_1 = [ln for ln in lines2 if ln.startswith("- [2026-09-27 22:3x r344 bm-b] 坑律：autofill claim")]
r344_full_2 = [ln for ln in lines2 if ln.startswith("- [2026-09-27 22:3x r344 bm-b] 坑律：rebase 重放窗内")]
assert len(r344_full_1) == 1 and len(r344_full_2) == 1, "r344 full rows not unique in s2"
r344_full_1, r344_full_2 = r344_full_1[0], r344_full_2[0]

p_344_1 = ("- [2026-09-27 22:3x r344 bm-b] 坑律（三十三批外迁·指针）：autofill claim 恢复腿盲 rebase --abort 杀会话在飞 rebase"
           "（abort 腿新面·r345 已修）——全文=archive 202609.md『坑律归档 2026-09-27 三十三批』节。指针=results/_r344bmb_fold_drive.py")
p_344_2 = ("- [2026-09-27 22:3x r344 bm-b] 坑律（三十三批外迁·指针）：rebase 重放窗 pool take-new 时戳面丢远端新增行"
           "（条目集 carry 对账律）——全文=archive 202609.md『坑律归档 2026-09-27 三十三批』节。指针=results/_r344bmb_close.py")
batch_note = ("- 三十三批外迁（r112 bm-c·2026-09-27·超线 10,254B>10,000B 当窗整编·行级零丢失·同窗撞批号让号 r176 律："
              "三十二批号让 origin d60676fb bm-a r360 批）：r344 bm-b 两行 verbatim=archive 202609.md『坑律归档 2026-09-27 三十三批』节；"
              "保留=User 元律+法行+批指针行族+r360 律。")

c = s2.replace(r344_full_1, p_344_1).replace(r344_full_2, p_344_2)
if not c.endswith("\n"): c += "\n"
c += batch_note + "\n"
for probe in (bma_r360_row, bma_r110_ptr, p_344_1, p_344_2, batch_note):
    assert probe in c, "CODELY union missing element"
assert r344_full_1 not in c and r344_full_2 not in c, "r344 full rows must be replaced"
assert no_real_markers(c)
sz = len(c.encode("utf-8"))
assert sz < 10000, "CODELY over hard line: %d" % sz

# ---- archive 202609.md: base = s2 (ends with bma batch-32), append bmc batch-33 ----
a2, a3 = gs(2, "research/memory-archive/202609.md"), gs(3, "research/memory-archive/202609.md")
marker = "## 坑律归档 2026-09-27 三十二批（r112 bm-c"
idx = a3.find(marker)
assert idx >= 0, "bmc batch section not found in s3 archive"
mine_rows_blob = a3[idx + len(marker):]
row_start = mine_rows_blob.find("- [2026-09-27 22:3x r344 bm-b]")
assert row_start >= 0, "r344 rows not found in s3 archive tail"
rows_txt = mine_rows_blob[row_start:].rstrip("\n")
r1 = "- [2026-09-27 22:3x r344 bm-b] 坑律：autofill claim 恢复腿（_claim_shard r282 fail-safe）"
r2 = "- [2026-09-27 22:3x r344 bm-b] 坑律：rebase 重放窗内 runnable_pool.json take-new(updated_at)"
assert rows_txt.count(r1) == 1 and rows_txt.count(r2) == 1, "r344 verbatim rows incomplete in s3 tail"

sec = ("\n## 坑律归档 2026-09-27 三十三批（r112 bm-c·超线 10,254B>10,000B 当窗整编·行级零丢失·"
       "同窗撞批号让号 r176 律：三十二批号让 origin bm-a r360 批）\n\n" + rows_txt + "\n")
if not a2.endswith("\n"): a2 += "\n"
a = a2 + sec
for probe in (r344_full_1, r344_full_2):
    assert probe in a, "archive zero-loss FAIL"
assert "## 坑律归档 2026-09-27 三十二批（r360 bm-a" in a, "bma batch-32 section missing"
assert "## 坑律归档 2026-09-27 三十三批（r112 bm-c" in a
assert no_real_markers(a)

io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md", "w", encoding="utf-8", newline="").write(c)
io.open(r"K:\Fluxgroup\FluxGroup\quant\bigmoney\research\memory-archive\202609.md", "w", encoding="utf-8", newline="").write(a)

# ---- round report + state note: renumber references (pre-push window = sole fix window) ----
rp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\logs\iteration-loop\round_reports-bm-c.md"
t = io.open(rp, "r", encoding="utf-8").read()
assert t.count("三十二批节") == 1, "report renumber anchor not unique: %d" % t.count("三十二批节")
t = t.replace("batch-32 in-window hot-cold archival per O-0230",
              "batch-33 (renumbered from 32 per r176 yield: same-window collision with bma r360 batch-32 landed origin-first) in-window hot-cold archival per O-0230")
t = t.replace("archive 202609.md 三十二批节", "archive 202609.md 三十三批节")
t = t.replace("batch-32 zero-loss", "batch-33 zero-loss")
io.open(rp, "w", encoding="utf-8", newline="").write(t)

sp = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\state-bm-c.json"
st = json.load(io.open(sp, "r", encoding="utf-8"))
n = st["note"]
n = n.replace("batch-32 in-window archival: 2x r344 bm-b verbatim -> archive 32nd batch section + pointer backfill",
              "batch-33 in-window archival (renumber per r176 collision with bma r360 batch-32): 2x r344 bm-b verbatim -> archive 33rd batch section + pointer backfill")
assert "batch-33" in n and "32nd batch" not in n
st["note"] = n
io.open(sp, "w", encoding="utf-8", newline="").write(json.dumps(st, ensure_ascii=False, indent=1) + "\n")
json.load(io.open(sp, "r", encoding="utf-8"))  # parse-verify

print("pass-2 OK: CODELY %dB (bma-base union, r360+r110ptr kept, r344 ptrs renumbered 33), archive bma-32 + bmc-33 sections, report/state renumbered" % sz)
