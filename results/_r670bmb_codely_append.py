# r670 bm-b: append one CODELY.md lesson line (bytes mode, append-only, entry-four-questions gate passed)
PATH_ = "CODELY.md"
ROW = ("- [2026-10-04 12:4x r670 bm-b] 集团派工行自领前先查既有实现律（D-20261004-02①②③ 反重复实弹）："
       "集团通告板派工行涉本司时，开工前必先双扫——①git log --all --grep <派工号> ②仓内 grep <派工号>（含 tools 脚本注释面）——"
       "确认零实现才开工。本窗 D-20261004-02①②③（池 data_deps 门+PREREG 种子选位律+S4U D-19 fallback）"
       "已由本机 r640 死会话收养窗全量落地（commit 9c38bd8ac·autofill/PREREG_TEMPLATE/README/iteration_prompt 四面），"
       "本窗差点按派工行字面重做三件——幸 grep 命中 Tools/_r439bmc_closeout_writes.py L75 指称+commit 搜索当场消融；"
       "正解=只补缺口面（F- 回执未呈=唯一缺口→F-20261004-02 补呈+autofill selftest 活体复验 ALL PASS 含 S4b×4/S17dd×2）。"
       "How to apply：撞通告板派工行先双扫；已有实现=只做回执呈证+活体复验增量，禁按行面重做。")

with open(PATH_, "rb") as f:
    data = f.read()
needle = b"[2026-10-04 12:1x r675 bm-a]"
cnt = data.count(needle)
assert cnt == 1, "anchor count %d != 1" % cnt
assert data.count(b"[2026-10-04 12:4x r670 bm-b]") == 0, "row already present"
had_nl = data.endswith(b"\n")
with open(PATH_, "ab") as f:
    if not had_nl:
        f.write(b"\n")
    f.write(ROW.encode("utf-8") + b"\n")
with open(PATH_, "rb") as f:
    after = f.read()
assert after.count(b"[2026-10-04 12:4x r670 bm-b]") == 1
assert after.count(needle) == 1
print("CODELY_APPEND_OK %d -> %d bytes" % (len(data), len(after)))
