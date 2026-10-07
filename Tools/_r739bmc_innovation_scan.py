"""r739 bm-c innovation radar BigMoney domain slice scan (O-20261008-0650 ③
nine-company self-claim window). Live reads: GitHub official search API
(fresh + active + CN-market + LLM-agent four faces) + HN Algolia. Zero-install
probe; all candidates remain candidate-state (no adoption in this probe).
Evidence -> results/_r739bmc_innovation_scan.json. Zero-desktop-window:
pure urllib, no native exe spawned."""
import json
import os
import time
import urllib.parse
import urllib.request

REPO = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
OUT = os.path.join(REPO, "results", "_r739bmc_innovation_scan.json")
UA = {"Accept": "application/vnd.github+json",
      "User-Agent": "bigmoney-radar-bmc-r739"}


def gh_search(q, per_page=10):
    url = "https://api.github.com/search/repositories?" + urllib.parse.urlencode(
        {"q": q, "sort": "stars", "order": "desc", "per_page": per_page})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def slim(it):
    lic = (it.get("license") or {}).get("spdx_id")
    return {
        "full_name": it.get("full_name"),
        "stars": it.get("stargazers_count"),
        "created": (it.get("created_at") or "")[:10],
        "pushed": (it.get("pushed_at") or "")[:10],
        "license": lic,
        "lang": it.get("language"),
        "archived": it.get("archived"),
        "desc": (it.get("description") or "")[:220],
        "url": it.get("html_url"),
    }


def hn(query, hits=10):
    url = "https://hn.algolia.com/api/v1/search_by_date?" + urllib.parse.urlencode(
        {"query": query, "tags": "story", "hitsPerPage": hits})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return [{"title": h.get("title"), "points": h.get("points"),
             "created": (h.get("created_at") or "")[:10],
             "url": h.get("url")} for h in d.get("hits", [])]


QUERIES = [
    ("fresh_quant_finance", "quant finance created:>2026-08-01 stars:>100"),
    ("fresh_trading_strategy", "trading strategy created:>2026-08-01 stars:>150"),
    ("topic_qf_active", "topic:quantitative-finance stars:>300 pushed:>2026-09-15"),
    ("topic_backtest_active", "topic:backtesting stars:>600 pushed:>2026-09-15"),
    ("cn_market_tools", "akshare OR \"A-share\" OR \"chinese stock\" stars:>150 pushed:>2026-08-01"),
    ("llm_finance_agent", "finance LLM agent stars:>300 pushed:>2026-08-01"),
    ("factor_alpha_mining", "alpha factor stock stars:>250 pushed:>2026-08-01"),
]


def main():
    facts = {"round": 739, "probe": "innovation-radar-bigmoney-domain-slice",
             "order": "O-20261008-0650 ③", "faces": {}}
    for name, q in QUERIES:
        try:
            d = gh_search(q)
            facts["faces"][name] = {"q": q, "total": d.get("total_count"),
                                   "items": [slim(i) for i in d.get("items", [])]}
        except Exception as e:
            facts["faces"][name] = {"q": q, "error": repr(e)[:200]}
        time.sleep(8)  # unauth search rate discipline ~10/min
    try:
        facts["hn_trading"] = hn("trading")
        time.sleep(2)
        facts["hn_quant"] = hn("quant finance")
    except Exception as e:
        facts["hn_error"] = repr(e)[:200]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(facts, fh, indent=1, ensure_ascii=False)
    for name, face in facts["faces"].items():
        if "error" in face:
            print(name, "ERROR", face["error"])
            continue
        print(f"== {name} (total {face['total']})")
        for it in face["items"][:10]:
            print(f"  {it['stars']:>6}* {it['full_name']} [{it['license']}] "
                  f"{it['lang']} push {it['pushed']} :: {it['desc'][:100]}")
    for k in ("hn_trading", "hn_quant"):
        if k in facts:
            print(f"== {k}")
            for h in facts[k][:8]:
                print(f"  {h['points']:>4}p {h['created']} {h['title'][:90]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
