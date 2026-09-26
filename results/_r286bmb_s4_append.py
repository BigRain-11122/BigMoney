# -*- coding: utf-8 -*-
"""r286 bm-b S4: CODELY.md law-line append (byte-face append-only,
tail-newline probe first per r281 law; raw-binary write)."""
import io

CM = r"C:\Users\Administrator\Desktop\Bigmoney\CODELY.md"

LAW = (
    "\n[2026-09-27 01:2x] 坑律（bm-b r286·CN-TREND-ETF-P1 池首烧 int64 崩·r259 自测桩家族新参·E1 首烧自捕零外泄）：**runner 的 collect-only 字段（transitions_head 的 'leg'=np.flatnonzero 产物 np.int64）只在 judged face 采集——synthetic 自测夹具与非 judged face 全走原生类型，selftest 21/21+bm-a real-gate probe 双绿仍掩住真数据 x2 首烧 json.dump 即崩（finalize 携带同一 payload=修单点必再崩）**；正律=①跑面 dump 站点一律 _jsonable 全量 native 强转（p4_batch2_screen idiom·三站点=_attr_row/finalize/每 cell checkpoint 全改）②自测加「非原生类型注入」腿（leg [13] np.int64/np.float32/np.bool_ 强转+json.dumps 断言）③真数据单 cell 灾面探针先于池重发（6.4s 验 x2 dump+checkpoint 供池幂等续跑+sharpe 0.4516 与 bm-a 注册探针值恒等=确定性跨机实证）。指针=scripts/cn_trend_etf_p1.py r286 AMENDMENT+results/_r286bmb_cntrend_probe.py\n"
)

raw = open(CM, "rb").read()
if not raw.endswith(b"\n"):
    LAW = "\n" + LAW.lstrip("\n")
    with io.open(CM, "ab") as f:
        f.write(LAW.encode("utf-8"))
else:
    with io.open(CM, "ab") as f:
        f.write(LAW.lstrip("\n").encode("utf-8"))
raw2 = open(CM, "rb").read()
assert raw2.endswith(b"\n") and len(raw2) > len(raw) and len(raw2) - len(raw) < 2000
print(f"CODELY.md {len(raw)} -> {len(raw2)} (+{len(raw2)-len(raw)}); "
      f"50KB watermark: {'OVER' if len(raw2) > 51200 else 'under'}")
