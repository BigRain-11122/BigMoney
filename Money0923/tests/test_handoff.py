# HANDOFF 周期交接文档回归测试（用户指令2026-09-22：每周期落盘、新AI会话可随时接手）
# 隔离：HANDOFF/DEV_NOTES/SYSTEM_AUDIT 全部指向临时文件，不碰真实文档。
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from quant.config import AppConfig                    # noqa: E402
from quant import handoff as qh                      # noqa: E402


def _mk_state() -> dict:
    return {
        "account": {"cash": 20_000.0, "positions": {"000651": {"shares": 300}}},
        "paper_track": [{"date": "2026-09-21", "equity": 99_965.0, "n_positions": 5},
                        {"date": "2026-09-22", "equity": 100_100.0, "n_positions": 9}],
        "champion": {"strategy": "multifactor", "promoted_at": "2026-09-22T01:36:26",
                     "holdout": {"score": 0.5794, "metrics": {}}},
        "arena": {"round": 26275, "players": [{"id": "P1"}] * 200,
                  "qualified": [{"id": "Q1"}] * 200,
                  "game": {"qualify_floor": 0.48, "recent_bias": 0.15},
                  "data_epoch_stock": 9, "data_epoch_futures": 1},
        "regime": {"snapshot": {"trend": "震荡", "factor_style": "反转有效",
                                "exposure_scale": 0.6, "best_family_now": {"family": "evolved"}}},
        "sleeves": [{"id": "S1", "label": "稳健仓", "members": [{"strategy": "multifactor"}],
                     "cash": 500.0, "capital_start": 59_697.0, "halt_line": 0.10,
                     "rotations": 0, "risk": {}}],
        "auto": {"code_files": {}, "code_loaded_at": "2026-09-21T20:33:14",
                 "session_date": "20260922"},
        "trade_log": [{"date": "2026-09-22", "sleeve": "S2", "code": "512800",
                       "side": "buy", "shares": 8000, "price": 0.834}],
        "stress_history": [{"date": "2026-09-22", "mean": 0.4158, "std": 0.27,
                            "beat_cash_pct": 0.75, "beat_bench_pct": 0.46,
                            "worst": 0.0122, "best": 0.85, "windows": 24}],
        "risk_events": [], "repo_open": [], "repo_log": [],
    }


def test_handoff_sections_and_content():
    cfg = AppConfig()
    with tempfile.TemporaryDirectory() as tmp:
        qh.HANDOFF_FILE = os.path.join(tmp, "HANDOFF.md")
        qh.DEV_NOTES_FILE = os.path.join(tmp, "DEV_NOTES.md")
        qh.AUDIT_DOC = os.path.join(tmp, "SYSTEM_AUDIT.md")   # 不存在→红线段走fallback
        with open(qh.DEV_NOTES_FILE, "w", encoding="utf-8") as f:
            f.write("## 进行中\n- 测试条目XYZ\n")
        text = qh.write_handoff(cfg, _mk_state(), reason="单测")
        assert os.path.exists(qh.HANDOFF_FILE)
        for sec in ["## 0.", "## 1.", "## 2.", "## 3.", "## 4.",
                    "## 5.", "## 6.", "## 7.", "## 8."]:
            assert sec in text, f"缺节 {sec}"
        assert "multifactor" in text and "26,275" in text
        assert "[S2] 512800" in text, "成交sleeve标签分隔"
        assert "测试条目XYZ" in text, "DEV_NOTES 必须被嵌入"
        assert "stock s9" in text
        assert "✅ 通过" in text, "体检结论（mean0.4158≥0.25且75%≥50%）"
        assert "paper --replay" in text, "命令速查"


def test_handoff_code_drift_detection():
    """auto启动快照 vs 磁盘现值：篡改一个文件哈希→必须报drift。"""
    snap = {"quant/zzz_fake.py": "deadbeef", "run.py": "whatever"}
    cur = dict(snap)
    cur["run.py"] = "changed"                    # 模拟 run.py 被改
    cur["quant/new_file.py"] = "aaa"             # 模拟新增文件
    qh.code_fingerprint = lambda: cur
    drift = qh._code_drift({"auto": {"code_files": snap}})
    assert "run.py" in drift
    assert any("新增" in d for d in drift), "新增文件也要报"
    assert "quant/zzz_fake.py" not in drift
    assert qh._code_drift({"auto": {"code_files": {}}}) is None, "空快照=未知（勿误报已同步）"


def main():
    test_handoff_sections_and_content()
    test_handoff_code_drift_detection()
    print("test_handoff 全部通过：八节齐全/内容断言/代码drift检测")


if __name__ == "__main__":
    main()
