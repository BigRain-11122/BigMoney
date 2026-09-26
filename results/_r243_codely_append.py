"""r243: append CODELY.md pitfall line (python UTF-8 writer per r230 law)."""
import io

P = "CODELY.md"
LINE = (
    "- [2026-09-26 11:4x] 坑律（bm-a R243·T-77 slice-4 GPU lane·torch 核首"
    "实弹·r223 条件性机件族 GPU 维·E1 自捕）：**无 GPU 主机交付的 torch 核"
    "必须视为「从未验证」——bm-b r238 诚实 SKIP 的 torch 腿在 bm-a 首跑连爆"
    "双病：①排名核无效条目消费全行排序位（须改有效子集内定序 cum_before"
    "+(cnt_valid+1)/2）；②组轴 (T,G) 张量未经 gather(1,gidl) 回位轴直喂 "
    "scatter_(1,si,(T,N)) = 形状不匹配 CUDA 静默执行为垃圾（tie 组名次读成"
    "NaN 组槽位 21.5-vs-20.0 签名）**；判读面=co_names/inspect.getsource "
    "确认装载源后仍矛盾时查算子形状契约勿疑 pyc。指针="
    "scripts/gpu_factor_matrix.py avg_ranks+results/_r243_gpu_rank_probe4.py"
    "+results/_r243_resolve.py\n")
txt = io.open(P, encoding="utf-8").read()
assert LINE[:40] not in txt, "already appended"
if not txt.endswith("\n"):
    txt += "\n"
io.open(P, "w", encoding="utf-8", newline="").write(txt + LINE)
import os
print("appended; size now:", os.path.getsize(P), "bytes | >50KB:",
      os.path.getsize(P) > 50 * 1024)
