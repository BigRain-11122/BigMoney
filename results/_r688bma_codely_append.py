"""r688 bm-a S4: append one pit line to CODELY.md (marker-count gate per r679)."""
line = (
    "- [2026-10-04 17:3x r688 bm-a] 池翻面守卫的 lane-mirror 家族检查域坑（W3 SHARD-2 two-layer flip 实弹·r485 bm-c 范式镜像首撞）："
    "r485 范式 flip 脚本的 gate-3 家族预检（SHARD-0 done+siblings ready）对共享 pool 面合法，镜像到本机 lane mirror（runnable_pool.bm-a.json）即恒假红——"
    "lane mirror 对他机分片天然陈旧（bm-c SHARD-0 done-flip 只落共享面+其自家 lane，他机 lane 不更新），fam[SHARD-0].status 在本机 lane='ready'≠共享面'done'。"
    "正法=flip 守卫带 strict_family 参（共享面 strict=True·lane mirror 只检本 entry 面勿做家族断言）；另：字节手术读面必 open(newline='') 否则 text-mode 翻译 CRLF→split('\\r\\n') 恒 1 行假读。"
    "How to apply：未来两文件翻面脚本照 _r688bma_shard2_flip_full.py 带 strict_family 分档；lane mirror 的他机面=陈旧视图禁当断言依据（同步归 merge_lane_views settle 面）。\n"
)
p = r"C:\Users\sjs20\Desktop\FluxGroup\quant\bigmoney\CODELY.md"
b = open(p, "rb").read()
assert b.count(b"[2026-10-04 17:3x r688 bm-a]") == 0, "marker already present (r679 idempotence)"
if not b.endswith(b"\n"):
    b += b"\n"
open(p, "ab").write(line.encode("utf-8"))
nb = open(p, "rb").read()
assert nb.count(b"[2026-10-04 17:3x r688 bm-a]") == 1, "append not unique"
print("CODELY appended, size:", len(nb))
