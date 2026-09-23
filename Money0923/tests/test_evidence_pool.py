"""选人与认证池科学性测试（2026-09-21 用户红线"所有都要基于科学"）。

验证两处证据分级修复：
① 认证池淘汰=证据制（认证分最低先出、各族唯一代表保护、时间序保留）
   ——旧尾部截断在 0.75秒/局流速下 200池40分钟全换血=证据失忆；
② 仓选人证据分级：≥30局累积实战盈稳分 > 单局认证分（单局快照运气
   成分大），证据不足回退认证分，回退链完整。
运行: python tests/test_evidence_pool.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant import sleeves as qsl  # noqa: E402
from quant.arena import _ind_key, _trim_qualified  # noqa: E402


def _cert(i: int, fam: str, score: float, at: str) -> dict:
    return {"id": f"Q{i}", "strategy": fam, "params": {"k": i},
            "sizing": "equal", "sizing_params": {}, "score": score,
            "streak": 3, "qualified_at": at}


def test_trim_qualified_evidence_based():
    a = {"qualified": [_cert(1, "rare_fam", 0.10, "2026-09-21 01:00:00")]}
    # 204 个 hot_fam 认证，分数唯一递增（i 越小分越低）
    for i in range(2, 206):
        a["qualified"].append(_cert(i, "hot_fam", 0.20 + i * 0.001,
                                    f"2026-09-21 0{i % 10}:{i % 60:02d}:00"))
    _trim_qualified(a, 200)
    q = a["qualified"]
    assert len(q) == 200, f"应保留200，实际{len(q)}"
    assert any(x["id"] == "Q1" for x in q), "各族唯一代表必须受保护（哪怕分数全场最低）"
    kept = {x["id"] for x in q}
    evicted = [i for i in range(2, 206) if f"Q{i}" not in kept]
    assert evicted == [2, 3, 4, 5, 6], f"应淘汰 hot_fam 分数最低的5人，实际{evicted}"
    ats = [x.get("qualified_at") or "" for x in q]
    assert ats == sorted(ats), "保留后必须恢复时间序（展示端 qualified[-5:] 依赖）"
    print(f"认证池证据淘汰 OK: 205→200，淘汰Q2-Q6（最低分），唯一族代表Q1(0.10分)保住")


def test_pick_member_evidence_hierarchy():
    qA = {"id": "QA", "strategy": "etf_trend", "params": {"ma": 5}, "sizing": "equal",
          "sizing_params": {}, "score": 0.90, "streak": 3,
          "qualified_at": "2026-09-21 20:00:00"}
    qB = {"id": "QB", "strategy": "etf_trend", "params": {"ma": 9}, "sizing": "equal",
          "sizing_params": {}, "score": 0.40, "streak": 3,
          "qualified_at": "2026-09-21 21:00:00"}
    state = {"arena": {"qualified": [qA, qB],
                       "pstats": {_ind_key(qB): {"n": 50, "ps_sum": 15.0}}}}
    m = qsl.pick_member(state, prefer_family="etf_trend")
    assert m["_src"]["id"] == "QB", "50局累积盈稳分0.30必须压过单局认证分0.90"
    assert "50局" in m["_src"]["basis"] and "盈稳分" in m["_src"]["basis"]
    print(f"证据分级 OK: 选QB（{m['_src']['basis']}）> QA（单局0.90快照）")

    # 样本不足（<30局）→ 回退认证分：QA 胜出
    state["arena"]["pstats"] = {_ind_key(qB): {"n": 5, "ps_sum": 1.0}}
    m = qsl.pick_member(state, prefer_family="etf_trend")
    assert m["_src"]["id"] == "QA" and "认证分" in m["_src"]["basis"]
    print(f"回退链 OK: QB实战仅5局不足30 → 按认证分选QA（{m['_src']['basis']}）")

    # 排除语义不回归：QA 被排除 → 选 QB（证据分级照常工作）
    m = qsl.pick_member(state, prefer_family="etf_trend", exclude_ids={"QA"})
    assert m is not None and m["_src"]["id"] == "QB"
    print("排除语义 OK: exclude_ids 仍生效")


if __name__ == "__main__":
    test_trim_qualified_evidence_based()
    test_pick_member_evidence_hierarchy()
    print("ALL PASS")
