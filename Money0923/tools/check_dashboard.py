import datetime as dt
import os
import re

h = open("dashboard.html", encoding="utf-8").read()
print("== 关键数值抽查 ==")
checks = [
    (r"模拟本金 ([\d,]+)", "本金"),
    (r"<b>([\d,]+)</b><span>累计", "账户权益"),
    (r"晋升尝试 (\d+)/(\d+)", "晋升配额"),
    (r"累计局数.*?<b>([\d,]+)</b>", "联赛局数"),
    (r"认证 <b>(\d+)</b>", "认证人数"),
    (r"链式 <b[^>]*>([+-][\d.]+%)", "WF链式"),
    (r"等权基准 <b[^>]*>([+-][\d.]+%)", "WF基准"),
    (r"精英池快照 · (\d+) 族", "GA族数"),
]
for pat, label in checks:
    m = re.search(pat, h, re.S)
    print("  %s: %s" % (label, m.group(1) if m else "缺失"))
for key in ["无未来函数抽查", "距下一开市", "本局Top10 家族构成", "王座空悬", "先声明后揭示"]:
    print("  %s: %s" % (key, "有" if key in h else "缺失"))
bad = re.findall(r">None<|>nan<|NaN", h)
print("null/nan泄漏:", len(bad))
print("生成时间:", dt.datetime.fromtimestamp(os.path.getmtime("dashboard.html")))
