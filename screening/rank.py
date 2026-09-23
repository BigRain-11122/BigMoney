"""Screen all backtest results, apply filters, rank by composite score."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import PATHS, SCREEN
from screening.overfit import detect_equity


def load_results() -> list[dict]:
    rows = []
    for f in glob.glob(os.path.join(PATHS.results_dir, "*.json")):
        try:
            with open(f) as fh:
                rows.append(json.load(fh))
        except Exception:
            continue
    return rows


def passes_filters(metrics: dict) -> bool:
    if metrics.get("num_trades", 0) < SCREEN.min_trades:
        return False
    if abs(metrics.get("max_drawdown", 0)) > SCREEN.max_drawdown_limit:
        return False
    if metrics.get("sharpe", 0) < SCREEN.min_sharpe:
        return False
    if metrics.get("annual_return", 0) <= 0:
        return False
    return True


def score(metrics: dict) -> float:
    """Exact formula per spec: ar*0.4 + sharpe*0.3 + (1-mdd)*0.2 + wr*0.1."""
    ar = metrics.get("annual_return", 0)
    sh = metrics.get("sharpe", 0)
    mdd = abs(metrics.get("max_drawdown", 0))
    wr = metrics.get("win_rate", 0)
    return ar * 0.4 + sh * 0.3 + (1 - mdd) * 0.2 + wr * 0.1


def rank(top_n: int = 10) -> list[dict]:
    rows = load_results()
    kept = [r for r in rows
            if r.get("status") == "ok" and passes_filters(r["metrics"])]
    for r in kept:
        r["score"] = round(score(r["metrics"]), 4)
        eq = r.get("equity_curve", [])
        if eq:
            r["overfit"] = detect_equity(eq)
        else:
            r["overfit"] = {"risk": "UNKNOWN",
                            "is_sharpe": 0, "oos_sharpe": 0, "drop_pct": 0}
    kept.sort(key=lambda x: x["score"], reverse=True)
    return kept[:top_n]


def write_report(top: list[dict], path: str = None) -> str:
    path = path or os.path.join(PATHS.results_dir, "ranking.csv")
    cols = ["rank", "hash", "score", "annual_return", "max_drawdown",
            "sharpe", "win_rate", "num_trades",
            "overfit_risk", "is_sharpe", "oos_sharpe", "params"]
    with open(path, "w", encoding="utf-8") as f:
        f.write(",".join(cols) + "\n")
        for i, r in enumerate(top, 1):
            m = r["metrics"]
            of = r.get("overfit", {})
            f.write(",".join(str(x) for x in [
                i, r["hash"], r["score"],
                m.get("annual_return", ""), m.get("max_drawdown", ""),
                m.get("sharpe", ""), m.get("win_rate", ""),
                m.get("num_trades", ""),
                of.get("risk", "?"), of.get("is_sharpe", ""),
                of.get("oos_sharpe", ""),
                json.dumps(r.get("params", {}), ensure_ascii=False),
            ]) + "\n")
    return path


if __name__ == "__main__":
    top = rank(10)
    p = write_report(top)
    print(f"wrote {p}, top {len(top)} strategies")
    for r in top[:5]:
        m = r["metrics"]
        of = r.get("overfit", {})
        print(f"  {r['hash']} score={r['score']:.3f} "
              f"ar={m['annual_return']:.2%} sh={m['sharpe']:.2f} "
              f"mdd={m['max_drawdown']:.2%} risk={of.get('risk','?')}")
