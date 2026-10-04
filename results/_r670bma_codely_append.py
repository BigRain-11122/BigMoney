# r670 bm-a S4: CODELY.md pit entry append (utf-8 binary-safe; entry gate: lesson-first, <=1.5KB)
entry = (
    "\n- [2026-10-04 10:2x r670 bm-a] runner 任务参数语义双轨坑+checkpoint 扫描器配对坑（T-167 "
    "THEME-JUDGE-P1 首烧实弹·判决批 runner 族通用）：①任务生成端与 worker 端对同一整型参数的语义"
    "不一致（生成端发 k 起点 offset {0,100..1900}，worker 按 chunk 序号算 ks=range(ci*CHUNK,(ci+1)*CHUNK)）"
    "→38/40 任务块静默产出空数组（ks=[]·零异常零日志）直通装配断言才炸——单跑 selftest 若只测「双跑字节"
    "恒等」测不出（两跑同错恒等）。律：参数双端约定必配「覆盖铺瓦守卫腿」（所有块 ks 并集==0..K-1 恰一次"
    "·r670 selftest 新腿本可拦此 bug）；空产出任务块=语义错位第一指征。②checkpoint 扫描器文件名模式"
    "与实际产物名不配对（startswith('chunk_') vs 实名 TJ-*_chunk_*.json）→断点续跑永不跳过；且修名后"
    "必再配非空 payload 守卫（row.get('ks') 非空才算 done）——空毒块被跳过=装配必二次炸（本例盘上 38 "
    "空块若被跳过即触发）。How to apply：判决批/池批 runner 开发时三件套=铺瓦守卫腿+扫描器实名配对+"
    "done 判定非空校验；崩溃后修复必走 fuse code_changed 自动清除正路（勿手删 fuse），断点复用前先按"
    "非空守卫清点健康块（本例 2/40 健康 chunk_00 可复用省 5%）。\n"
)
raw = open("CODELY.md", "rb").read()
assert raw.endswith(b"\n") or raw.endswith(b"\r\n")
with open("CODELY.md", "ab") as fh:
    fh.write(entry.encode("utf-8"))
chk = open("CODELY.md", "rb").read()
chk.decode("utf-8")
assert b"r670 bm-a" in chk[-2500:]
print("CODELY.md pit entry appended, utf-8 self-check PASS, size:", len(chk))
