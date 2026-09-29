# r424 bm-a waterline reorg: append pit-100 to hot CODELY.md, migrate pit-98/99 +
# r208 merge-note verbatim to archive 202609.md (zero-loss line-level surgery).
import io, sys

HOT = "CODELY.md"
ARC = "research/memory-archive/202609.md"

PIT100 = (
    "- [2026-09-29 10:2x r424 bm-a] 坑律一百批（merge 语境 merge_lane_views resolve 可直用律·「rebase 三 stage」文档字面≠禁用面）："
    "pit-93 merge-back 单 merge（非 rebase-replay）撞 UU 批时，merge_lane_views.py resolve 文档面写死「:2:=origin/:3:=本地」（r351 rebase 定向律）——"
    "merge 语境实际 :2:=ours=本地 HEAD/:3:=theirs=origin，但配方三面语境无关皆正典：①union 族对称；②take-new 族 ts 深探与侧号无关；"
    "③同秒 tie→:2: 在 rebase=origin/在 merge=ours=HEAD=r140「tie 取 HEAD」律两语境同一实现。r424 实弹：单 merge 6 UU 一次全绿"
    "（5 ALL_FACES resolve+1 snapshot deep-ts 取 ours 09:46:36>09:40:51），compute_audit history union 203=双侧超集零丢失+latest.ts 09:44:52 探针取侧复算验证。"
    "附坑：解后同窗 reconcile（r376）若报单面 drift，先查是否 origin 继承的车道未吸收行（共享面兼容窗无 sanctioned 写手）而非解错——"
    "r424 例=bm-c 车道 09:23 audit 行未入共享面（bm-c r208 merge 取 origin 侧丢弃自家 shared 写），合并视图消费不丢数据、池面=flip 证据面不受影响，如实记录勿手写 union。"
    "How to apply：pit-93 单 merge 撞 UU 直接 resolve 勿迟疑；取侧后照常 git add+同窗 reconcile；drift 归因先查继承面。"
)

ARC_HEADER = (
    "## 坑律归档 2026-09-29 r424 bm-a 窗批（水位律当窗整编：CODELY 热层 batch-100 追加即超 ≤10KB 硬线→九十八/九十九批+r208 merge 注 verbatim 迁此·行级零丢失校验）\n"
)
ARC_TAIL_NOTE = (
    "\n（以上三行=hot CODELY.md 2026-09-29 r424 迁移窗原样 verbatim：九十九批 r208 bm-c/九十八批 r207 bm-c/r208 merge-back 注；"
    "hot 层去向=batch-100 在册+冷层指针行；零删改零重排。）\n"
)
POINTER = (
    "冷层指针：坑律正典 2026-09-29 九十八/九十九批（r207/r208 bm-c）+r208 merge-back 注全文 verbatim=archive 202609.md"
    "『坑律归档 2026-09-29 r424 bm-a 窗批』节（r424 bm-a 窗水位律当窗整编·行级零丢失校验）。"
)

hot_raw = io.open(HOT, encoding="utf-8", newline="").read()
arc_raw = io.open(ARC, encoding="utf-8", newline="").read()
hot_crlf = "\r\n" in hot_raw
arc_crlf = "\r\n" in arc_raw

def split_keep(s):
    lines = s.splitlines(True)
    return lines

hot_lines = split_keep(hot_raw)
eol = "\r\n" if hot_crlf else "\n"

# locate migration targets by prefix (assert exact one each)
targets = {
    "pit99": "- [2026-09-29 09:5x r208 bm-c] 坑律九十九批",
    "pit98": "- [2026-09-29 09:3x r207 bm-c] 坑律九十八批",
    "mnote": "〔r208 bm-c merge-back 注",
}
idx = {}
for key, pre in targets.items():
    hits = [i for i, l in enumerate(hot_lines) if l.startswith(pre)]
    assert len(hits) == 1, (key, hits)
    idx[key] = hits[0]
assert idx["pit99"] < idx["pit98"] < idx["mnote"], idx

ref_hits = [i for i, l in enumerate(hot_lines) if l.strip() == "### Reference"]
assert len(ref_hits) == 1
ref_i = ref_hits[0]
assert idx["mnote"] < ref_i, (idx, ref_i)

mig = [hot_lines[idx[k]] for k in ("pit99", "pit98", "mnote")]
mig_bytes = sum(len(l.encode("utf-8")) for l in mig)

# build new hot: Project section keeps pit-100 only; Reference gains pointer line
new_hot = (
    hot_lines[: idx["pit99"]]
    + [PIT100 + eol]
    + hot_lines[idx["mnote"] + 1 : ref_i + 1]
    + [POINTER + eol]
    + hot_lines[ref_i + 1 :]
)
new_hot_s = "".join(new_hot)

# build new archive: append section at end
arc_eol = "\r\n" if arc_crlf else "\n"
sec = ARC_HEADER
for l in mig:
    # normalize migration line endings to archive's
    sec += l.rstrip("\r\n") + arc_eol
sec += ARC_TAIL_NOTE
if not arc_raw.endswith("\n") and not arc_raw.endswith("\r\n"):
    arc_raw += arc_eol
new_arc_s = arc_raw + sec

# write
io.open(HOT, "w", encoding="utf-8", newline="").write(new_hot_s)
io.open(ARC, "a", encoding="utf-8", newline="").write(sec)

# verify: verbatim presence in archive, absence in hot, byte accounting
arc_now = io.open(ARC, encoding="utf-8", newline="").read()
hot_now = io.open(HOT, encoding="utf-8", newline="").read()
for l in mig:
    body = l.rstrip("\r\n")
    assert body in arc_now, "verbatim missing in archive"
    assert body not in hot_now, "still present in hot"
assert PIT100 in hot_now and POINTER in hot_now
hot_b = len(hot_now.encode("utf-8"))
arc_b = len(arc_now.encode("utf-8"))
print("hot:", hot_b, "B (limit 10240)", "OK" if hot_b <= 10240 else "OVER")
print("archive:", arc_b, "B (+%d)" % (arc_b - len(arc_raw.encode('utf-8'))))
print("migrated verbatim lines:", len(mig), "bytes:", mig_bytes)
print("zero-loss verified: verbatim-in-archive=%d, hot-absence=%d"
      % (sum(1 for l in mig if l.rstrip('\r\n') in arc_now),
         sum(1 for l in mig if l.rstrip('\r\n') not in hot_now)))
