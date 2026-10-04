# r670 bm-b: append push-race closeout addendum to round report (bytes append; CJK needles via .encode, not bytes literals)
RR = "logs/iteration-loop/round_reports.md"
ROW = ("- 追记 2026-10-04T12:4x (S7 收口窗 push-race 实弹): 他机同窗推 8 commit (035d02be1..0c4e428e1) -> 首推 non-FF 拒 -> "
       "merge origin/main 14 UU 全=同窗双跑再生面 (r667 同款) -> r670 resolver: 13 面 ts-freshness take-side ours "
       "(双侧 HEAD/MERGE_HEAD 原字节直取 r657 律②·ours 12:33-12:36 > theirs 12:27-12:28 全 13 面实证·零 probe-miss 零默认面) "
       "+ token_usage per-key union (side_pick=5·r456/r466 律) -> 零 marker 存活+全 json reparse 过 -> merge commit a0090d200 "
       "push_verify DELIVERED (ahead=0/behind=0); 本地未达 origin commit 数=0; S7 收口双扫 orders 153/153 零未回执。"
       "更正注记: 首版追记脚本 bytes 字面量含 CJK 语法崩 (r461 分步链律当场拦截·round_reports 未被写坏零伤) -> 本件=修复后真追加。")
needle = "追记 2026-10-04T12:4x (S7 收口窗 push-race 实弹)".encode("utf-8")
with open(RR, "rb") as f:
    d = f.read()
assert d.count(b"round 670 |") >= 1 and d.count(needle) == 0
with open(RR, "ab") as f:
    if not d.endswith(b"\n"):
        f.write(b"\n")
    f.write(ROW.encode("utf-8") + b"\n")
with open(RR, "rb") as f:
    after = f.read()
assert after.count(needle) == 1, "addendum verify fail"
assert after.count(b"round 670 |") == d.count(b"round 670 |"), "report body disturbed"
print("ADDENDUM_OK")
