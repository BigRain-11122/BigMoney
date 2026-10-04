# r692 bm-b: CODELY.md append (bytes mode, one compact entry, marker idempotency)
import io

ENTRY = "- [2026-10-04 20:3x r692 bm-b] 池面 claim 真值键位=entries[].shards[].owner 层（r675bmb 结构键位律的 owner 字段姊妹面）：N2-W15 双认领定谳窗首版探针读 entry 顶层 owner=null，差点立「trio 活烧+无主」假警报（实读 shard 层=owner=bm-b keepalive 20:14 鲜活）——池 claim 类探针/看板一律读 entries[].shards[] 的 owner/owner_since，禁消费 entry 层 owner=null 假象。附带（fleet 流水面，详见 MSG-2026-10-04-2025）：bm-a daemon 让渡后再认领裸分片 generate-0of1=r694① 认领盲窗复发；双烧危害=零（generate seeded 确定性+refuse-if-exists rc2 后落者诚实拒绝）；裁定=清创请求+产品优先豁免（谁先落=canonical per r486）。\n"

path = "CODELY.md"
with io.open(path, "rb") as f:
    blob = f.read()
marker = b"[2026-10-04 20:3x r692 bm-b]"
assert blob.count(marker) == 0, "marker already present (idempotency)"
if blob and not blob.endswith(b"\n"):
    blob += b"\n"
with io.open(path, "ab") as f:
    f.write(ENTRY.encode("utf-8"))
with io.open(path, "rb") as f:
    blob2 = f.read()
assert blob2.count(marker) == 1
print("CODELY APPEND OK size:", len(blob2))
