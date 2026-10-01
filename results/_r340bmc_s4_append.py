"""r340 bm-c S4: append one memory entry to CODELY.md (UTF-8, no console transcoding face)."""
ENTRY = (
    "\n- [2026-10-01 23:5x r340 bm-c] 采集器挂死面诊断律（T-131 fund_history refresh 实弹）："
    "进程活≠在干活——网络拉取器三面活性判定=进程在册/日志新鲜度/产物增长面；本例 pid 活但日志+产物双停滞 30.8min"
    "（pace 12.9s/sym 应每 ~13s 落件、_refresh.log 止于 tqdm 中段且无 FAIL 行=连 fuse 都不触发）=socket 级无超时挂死。"
    "正法=杀挂进程+断点续拉重生（per-face per-symbol checkpoint 只丢在飞单员）+8s 活性验证+产物增长面复核"
    "（r325 产物增长律的采集器变体；2803→2845 增长恢复=治愈证据）；锁含 pid 活性判定故 refresh 直调无锁闸可重生。"
    "How to apply：一切长跑采集器/守护的轮间监控以「日志 mtime+产物计数增长」为准——进程活而双停滞=杀+续拉勿等 fuse 勿等轮；"
    "与 r522 burn 记录单点持久化同族（遥测单点故障面）。\n"
)

p = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\CODELY.md"
with open(p, "ab") as f:
    f.write(ENTRY.encode("utf-8"))
with open(p, "rb") as f:
    tail = f.read()[-260:].decode("utf-8", "replace")
ok = "采集器挂死面诊断律" in tail and "r340 bm-c" in tail
print("APPEND_OK", ok)
import os
print("size_kb", round(os.path.getsize(p) / 1024, 1))
