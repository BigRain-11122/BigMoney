"""GPU 海选引擎校验：近似分 vs CPU精确适应度的秩相关 + 产出有效性。

运行: python tests/test_gpu_screen.py（无 CUDA 自动跳过）
"""
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")   # GBK控制台打印✅会崩（audit.py同款教训）
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant.config import load_config  # noqa: E402
from quant import data as qd  # noqa: E402
from quant.gpu_screen import gpu_available, gpu_screen, inject_to_population  # noqa: E402
from quant.evolve import Evolver  # noqa: E402
from quant.state import load_state  # noqa: E402

# 隔离铁律（2026-09-21 实测教训）：full_panel 无条件调用 update_daily/update_universe
# ——测试每跑一次就对真实宇宙做一遍增量更新（曾一晚 27 只全量重拉×4 次测试
# =真实数据重写+数据纪元连跳 4 级+无谓网络重拉）。本测试需要真实面板数据
# （近似分 vs CPU 精确分对照），但数据获取必须只读：更新路径打桩为缓存加载。
qd.update_daily = lambda cfg, codes=None: []
qd.update_universe = lambda cfg, force=False: qd.load_universe()


def _spearman(a: np.ndarray, b: np.ndarray) -> float:
    """Spearman 秩相关（无 scipy 依赖）。"""
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    if ra.std() < 1e-12 or rb.std() < 1e-12:
        return 0.0
    return float(np.corrcoef(ra, rb)[0, 1])


def main() -> None:
    if not gpu_available():
        print("无 CUDA：GPU 海选测试跳过 ✅（主流程不受影响）")
        return
    cfg = load_config()
    _, panel = qd.full_panel(cfg)

    # 海选必须与 GA 目标函数同窗（训练期，不含样本外）——
    # 否则"全期最优"候选在训练切片上可能系统性反向（实测 ρ=-0.6 的教训）
    state = load_state()
    ev = Evolver(cfg, panel, state)
    train_panel = ev.train_panel

    t0 = time.time()
    cands = gpu_screen(cfg, train_panel, per_family=400, top_k_out=6, progress=False)
    dt = time.time() - t0
    assert cands, "海选应产出候选"
    fams = {c["strategy"] for c in cands}
    n_screened = 400 * len(fams)
    print(f"海选: {len(cands)} 候选 / {len(fams)} 族 / {dt:.1f}s（≈{int(n_screened / max(dt, 0.01))}组/秒）")

    # —— 产出有效性：候选必须是精确引擎可执行的合法个体 ——
    gpu_s, exact_s = [], []
    for c in cands:
        f, _ = ev.fitness({"strategy": c["strategy"], "params": c["params"]})  # 精确3片适应度
        assert f >= -1.0, "精确引擎必须能评估所有海选候选"
        gpu_s.append(c["gpu_score"])
        exact_s.append(f)
    gpu_s, exact_s = np.array(gpu_s), np.array(exact_s)
    rho = _spearman(gpu_s, exact_s)
    print(f"近似分 vs 精确适应度 Spearman ρ = {rho:.3f}")
    print(f"精确分分布: 均值 {exact_s.mean():.3f} / 最高 {exact_s.max():.3f} / "
          f"过0.45门槛 {(exact_s >= 0.45).sum()}/{len(exact_s)}")
    # 海选的意义 = 找到高精确分的候选：Top10 的精确分均值应显著高于全体候选均值
    top10 = np.argsort(-gpu_s)[:10]
    print(f"GPU Top10 的精确分均值 {exact_s[top10].mean():.3f} vs 全体 {exact_s.mean():.3f}")

    # —— 注入无副作用 ——
    n_before = len(state["evolution"].get("population") or [])
    added = inject_to_population(state, cands)
    assert added > 0, "应注入新基因"
    # cap 缺省跟随 config.evolve.population（96）：GPU 注入不得把种群截回旧 48
    # （2026-09-21 科学审计：硬编码 48 曾每夜悄悄撤销"样本要大"的 96 扩容）
    from quant.config import AppConfig as _AC
    pop_cap = int(_AC().evolve.population)
    assert len(state["evolution"]["population"]) <= pop_cap, \
        f"注入后种群不得超过配置上限 {pop_cap}"
    print(f"注入 GA 种群: +{added}（种群 {n_before} → {len(state['evolution']['population'])}，"
          f"上限跟随 config={pop_cap}）")

    # 断言底线：秩相关应为正（近似模型方向正确），Top10 精确分应不低于全体均值
    assert rho > 0.0, "近似分与精确分应正相关"
    assert exact_s[top10].mean() >= exact_s.mean() - 0.05, "GPU Top10 不应系统性差于随机候选"
    print("GPU 海选校验通过 ✅")


if __name__ == "__main__":
    main()
