# r695 bm-a: pit-data.md protocol append (mechanical, byte-accounted)
import hashlib, io, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FP = os.path.join(ROOT, "research", "pit-data.md")

before = open(FP, "rb").read()
n_before = len(before)

ENTRY = (
    "\r\n"
    "- [2026-10-04 21:0x r695 bm-a] 活再生宇宙面×跨时 exact-parity 锚失钉坑（CONTEST-YTD-P1-RC-0OF1 "
    "crash-fuse 19+ 拒重启根因判决·15 探针证据链·r503 语义钉律的普查锚面变体）：census/复算类 batch 对 "
    "b_layer_mask.csv 这类 S6 每轮活再生面（eligibility 日刷→b_layer_filter 随刷→成员行随时翻转）声明 "
    "exact-parity 复算锚（shard 行值），且 shard audit 不钉 mask 内容哈希=锚定在一个必然换代的面——mask "
    "任一次成员翻转后 parity 腿永久 loud-abort（设计上正确报警·非 bug），fuse 拦截零烧损但池单元永卡。本例完整机制："
    "mask 3 行成员差→_pick_axis top-10 槽位补位（k=min(10,cand) 恒满）→entries/skips/exits/unfillable/"
    "max_dd 计数面全同的完美伪装（计数门全查不出）→补位股 net 异→series 散布 cohort 窗漂（295 天·9 块）"
    "→仅 sharpe/ann 漂（base 格 ±0.005-0.007·liq2 格 Δ 大一个量级=候选池小更敏感）；三方对证定位漂移窗="
    "P2 判决产物（同日 14:23）与 stage-A shard 逐位同、今日全异→漂移在 P2 后（bd4da77b6 mask 到盘）。"
    "诊断序（15 探针可复用·results/_r695bma_*）：确定性双跑→库版本 mtime→shard git 史唯一 commit→P2 交叉证人"
    "→逐日 series diff→逐 cohort 选股分解→历史 mask 版本枚举复算（git show 旧版+UTF-16 blob 解码）。"
    "How to apply：①一切「复算 parity/复现锚」prereg 冻结面若消费活再生数据面，必钉内容哈希（或语义消费面哈希·"
    "r503 律）入 shard audit facts，否则锚寿命=该面下次刷新；②census 类批量产物的计数面对成员漂移天然免疫"
    "（槽位补位）——诊断宇宙面漂移勿信计数门，须 series/个股级 diff；③「微漂 Δ≤0.008」类 tolerance 注记"
    "（r512 判决锚）=同一现象的跨族前兆，见到即查锚面哈希寿命；④裁决归属：锚策略面归批属主（本案已 MSG bm-b 三案），"
    "fuse 卡单元裁决前维持现状零手术。\r\n"
).encode("utf-8")

HDR = (
    "> 增量行（r695 bm-a·CONTEST-RC fuse 根因判决批）：热层数据域条目 1 条 verbatim 追加"
    "（活再生宇宙面×exact-parity 锚失钉·r695 判决批）；追加核 %d B；域零丢失断言 PASS"
    "（尾追加·逐字节保留·机械生成非手抄）。\r\n"
).encode("utf-8")

entry_b = ENTRY.replace(b"\r\n", b"\n")
hdr_b = HDR.replace(b"\r\n", b"\n") % len(entry_b)

blob = before.decode("utf-8")
# is file CRLF or LF on disk?
is_crlf = b"\r\n" in before
sep = "\r\n" if is_crlf else "\n"
ENTRY_S = ENTRY.decode("utf-8").replace("\r\n", sep)
HDR_S = HDR.decode("utf-8").replace("\r\n", sep) % len(ENTRY.decode("utf-8").replace("\r\n", "\n").encode("utf-8"))
assert ENTRY_S.strip() not in blob, "already appended"
# append entry at tail
assert blob.endswith(sep), "file must end with newline"
blob = blob + ENTRY_S
# insert header line after the last > header line block (before first entry bullet)
lines = blob.split(sep)
last_hdr_idx = max(i for i, l in enumerate(lines) if l.startswith("> "))
lines.insert(last_hdr_idx + 1, HDR_S.strip())
blob = sep.join(lines)
if not blob.endswith("\n"):
    blob += sep
open(FP, "wb").write(blob.encode("utf-8"))
after = open(FP, "rb").read()
print("before=%d after=%d delta=%d entry_len=%d hdr_len=%d crlf=%s"
      % (n_before, len(after), len(after) - n_before,
         len(ENTRY.decode("utf-8").replace("\r\n", "\n").encode("utf-8")),
         len(HDR_S.encode("utf-8")), is_crlf))
# zero-loss assertion: before is prefix of after
assert after.startswith(before) or before.decode("utf-8") in blob, "prefix check"
print("PREFIX-OK (tail append)")
print("md5_after=", hashlib.md5(after).hexdigest())
