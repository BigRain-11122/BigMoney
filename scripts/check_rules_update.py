"""Check market rules update. Run monthly via Task Scheduler.

Hit official rule pages, compare last-modified, and warn if newer than our version.
"""
import os
import sys
import json
import urllib.request
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from knowledge.rules import RULES_VERSION, RULES_UPDATED

RULES = [
    ("SSE trading rules",
     "https://www.sse.com.cn/lawandrules/sselawsrules2025/trade/universal/c/c_20260424_10816492.shtml"),
    ("SSE ETF FAQ",
     "http://www.sse.com.cn/assortment/fund/etf/question/"),
    ("SZSE trading rules",
     "http://docs.static.szse.cn/www/lawrules/rule/repeal/rules/W020230217564423808793.pdf"),
    ("CSRC 2026-07-06 rule change",
     "https://www.csrc.gov.cn/shanghai/c105566/c7643909/content.shtml"),
]


def check():
    report = {
        "checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "local_version": RULES_VERSION,
        "local_updated": RULES_UPDATED,
        "sources": [],
    }
    for name, url in RULES:
        try:
            req = urllib.request.Request(url, method="HEAD",
                                         headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                lm = r.headers.get("Last-Modified", "unknown")
                report["sources"].append({"name": name, "url": url,
                                          "last_modified": lm,
                                          "status": "ok"})
        except Exception as e:
            report["sources"].append({"name": name, "url": url,
                                      "status": f"fail: {type(e).__name__}"})
    out = os.path.join(os.path.dirname(__file__), "..", "logs",
                       "rules_check.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nlocal rules: {RULES_VERSION} ({RULES_UPDATED})")


if __name__ == "__main__":
    check()
