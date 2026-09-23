"""联赛全族保底席测试（2026-09-21 参考设计"30种全谱上场"机制更新）。"""
import io
import os
import sys

sys.stdout.insert if False else sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import quant.arena as arena  # noqa: E402
import quant.state as state_mod  # noqa: E402
from quant.config import AppConfig  # noqa: E402
from quant.strategies import STRATEGIES  # noqa: E402

state_mod.save_state = lambda s: None
arena.save_state = lambda s: None  # 隔离


def _valid_gene(name: str, salt: int) -> dict:
    from quant.strategies import get_strategy
    sp = get_strategy(name).param_space
    params = {}
    for k, v in sp.items():
        if v[0] == "int":
            params[k] = (v[1] + v[2]) // 2 + (salt % 3)
        elif v[0] == "float":
            params[k] = round((v[1] + v[2]) / 2, 4)
        else:
            params[k] = list(v[1])[0]
    if name == "evolved":  # 基因组策略用随机基因组
        import random as _r
        params = get_strategy(name).random_genome(_r.Random(salt))
    return {"strategy": name, "params": params, "sizing": "equal", "sizing_params": {}}


def test_family_floor():
    cfg = AppConfig()
    st = {"arena": {"players": [], "roster_version": "test", "id_seq": 5000},
          "evolution": {"population": []},
          "team": [], "champion": None}
    # 构造 100 人阵容但只覆盖 3 个族（其余全缺）
    fams3 = ["momentum", "low_vol", "mean_rev"]
    st["arena"]["players"] = [
        {"id": f"P{i:03d}", **_valid_gene(fams3[i % 3], i),
         "style": ["极稳", "保守", "均衡", "进取", "激进"][i % 5],
         "capital": 1_000_000.0, "equity": 1_000_000.0, "track": [], "streak": 0,
         "rounds": 10, "score_last": 0.3, "top10_hist": []}
        for i in range(100)]
    feed = []
    for i in range(10):
        g = st["arena"]["players"][i]
        feed.append({"id": g["id"], "strategy": g["strategy"], "params": g["params"],
                     "sizing": "equal", "sizing_params": {}, "style": g["style"]})
    rows = feed + [
        {"id": st["arena"]["players"][i]["id"], "strategy": fams3[i % 3],
         "params": st["arena"]["players"][i]["params"], "sizing": "equal",
         "sizing_params": {}}
        for i in range(10, 40)]
    arena._respawn_from_top(cfg, st, feed, rows, persist=False)
    roster = st["arena"]["players"]
    fams = {p["strategy"] for p in roster}
    missing = [f for f in STRATEGIES if f not in fams]
    # evolved 族需要基因组参数，sample_individual 对它生成基因组 ✓ 也应上场
    print(f"阵容 {len(roster)} 人 | 族覆盖 {len(fams)}/{len(STRATEGIES)}"
          f" | 缺席: {missing if missing else '无'}")
    assert len(roster) == cfg.arena.size, "阵容规模必须保持"
    assert not missing, f"全族保底失效，缺席 {missing}"
    ids = [p["id"] for p in roster]
    assert len(ids) == len(set(ids)), "ID 唯一性"
    styles = {}
    for p in roster:
        styles[p.get("style") or "均衡"] = styles.get(p.get("style") or "均衡", 0) + 1
    print(f"风格席位: {styles}")
    assert set(styles) == set(arena.STYLE_ORDER), "五风格全在场"
    print("全族保底席 OK：所有策略族均有代表参赛")


if __name__ == "__main__":
    test_family_floor()
    print("test_family_floor 全部通过")
