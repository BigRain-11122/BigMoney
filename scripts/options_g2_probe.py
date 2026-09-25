"""G2 probe: locate SSE official fee pages for ETF options (R169 no-blind-guess,
R171 parent-page href extraction via direct urllib + ProxyHandler({}) recipe).
Read-only research probe; writes nothing."""
import re
import sys
import urllib.request

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
           "Accept-Language": "zh-CN,zh;q=0.9"}


def fetch(url: str, timeout: int = 20) -> str:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    req = urllib.request.Request(url, headers=HEADERS)
    with opener.open(req, timeout=timeout) as r:
        raw = r.read()
    for enc in ("utf-8", "gbk", "gb18030"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", "ignore")


def hrefs(html: str, base: str) -> list:
    out = []
    for m in re.finditer(r'href="([^"]+)"[^>]*>([^<]{0,60})', html):
        u, text = m.group(1), m.group(2).strip()
        if any(k in u or k in text for k in ("option", "期权", "qiquan")) or \
           any(k in text for k in ("费", "收费", "期权")):
            if u.startswith("//"):
                u = "https:" + u
            elif u.startswith("/"):
                u = base.rstrip("/") + u
            out.append((u, text))
    return out


def main() -> int:
    pages = sys.argv[1:]
    if not pages:
        pages = ["http://www.sse.com.cn/"]
    for url in pages:
        print(f"== {url}")
        try:
            html = fetch(url)
        except Exception as exc:  # noqa: BLE001
            print(f"  FETCH FAIL: {exc}")
            continue
        print(f"  len={len(html)}")
        seen = set()
        for u, text in hrefs(html, "http://www.sse.com.cn"):
            if u in seen:
                continue
            seen.add(u)
            print(f"  {text[:40]!r} -> {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
