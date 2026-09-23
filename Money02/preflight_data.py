"""盘前数据备齐 (user order 2026-09-21: 需要的数据提前下好).

Run anytime before a session (e.g. pre-open or pre-week): pulls EVERYTHING
that already exists and verifies the paths that cannot be pre-pulled.

Steps:
  1. update_data(workers=4): fresh spot list (universe) + staleness audit of
     all bar files + gap-fill any straggler + index update.
  2. verify_data.py: source sanity (涨跌停越界/复权/市值 checks).
  3. test_refresh.py: incremental precision regression (trunc+refresh=真值).
  4. pull_live_snapshot(): realtime path pre-flight (qt.gtimg.cn + GBK +
     parquet write) so 09:15 hits a proven pipeline.

NOT pre-downloadable by design (auto-handled when they appear):
  - tonight's daily bars -> land ~17:30, tick detects new last_trade_date
    and launches the full cycle (incremental refresh + cache rebuild).
  - intraday snapshots -> auto every 10 minutes while the market is open.
"""
import subprocess
import sys
import time

import config as C
import data as D


def _step(n, label):
    print(f"\n===== [{n}] {label} =====", flush=True)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    t0 = time.time()
    _step(1, "增量审计+补漏 update_data(workers=4)")
    r = D.update_data(workers=4)
    ltd = D.last_trade_date()
    print(f"last_trade_date = {ltd}  refresh={r}", flush=True)
    if ltd is None:
        print("FATAL: no index data - run a full download first")
        sys.exit(1)
    if r.get("err", 0) > 0:
        print(f"WARN: {r['err']} stocks failed refresh - rerun preflight", flush=True)

    for script in ("verify_data.py", "test_refresh.py"):
        _step(2 if script == "verify_data.py" else 3, script)
        p = subprocess.run([sys.executable, str(C.ROOT / script)],
                           cwd=str(C.ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=600)
        print(p.stdout.strip())
        if p.returncode != 0:
            print(p.stderr.strip()[-500:])
            print(f"FATAL: {script} failed")
            sys.exit(1)

    _step(4, "实时链路预热 pull_live_snapshot")
    try:
        D.pull_live_snapshot(save=True)
        meta = __import__("json").loads(
            (D.LIVE_DIR / "latest.json").read_text(encoding="utf-8"))
        print(f"snapshot ok: {meta['stocks']}只 @ {meta['trade_date']} "
              f"成交 {meta['total_amount_yi']:.0f}亿 "
              f"涨{meta['up_count']}/平{meta['flat_count']}/跌{meta['down_count']}")
    except Exception as e:  # noqa: BLE001
        print(f"FATAL: live snapshot failed: {e}")
        sys.exit(1)

    print(f"\n=== preflight PASS {time.time() - t0:.0f}s === "
          f"| 数据就绪至 {ltd} | 今晚收盘后增量自动落地", flush=True)


if __name__ == "__main__":
    main()
