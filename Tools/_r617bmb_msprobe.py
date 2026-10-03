"""r617 bm-b: ModelScope probe (CEO order 1). Network read-only."""
import json
import ssl
import urllib.request

CTX = ssl.create_default_context()
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
REPO = "empero-ai/Qwen3.8-4B-Distill-GGUF"


def get_json(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def head(url):
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        return r.status, r.headers.get("Content-Length")


def main():
    try:
        d = get_json("https://modelscope.cn/api/v1/models/%s" % REPO)
        data = d.get("Data") or {}
        print("DETAIL keys=%s" % list(data.keys())[:25])
        print("DETAIL head=%s" % json.dumps(data, ensure_ascii=False)[:900])
    except Exception as exc:
        print("DETAIL FAIL: %s" % exc)
    for rev in ("master", "main"):
        for ep in ("files", "tree"):
            try:
                t = get_json("https://modelscope.cn/api/v1/models/%s/repo/%s?Revision=%s"
                             % (REPO, ep, rev))
                data = t.get("Data") or {}
                files = data.get("Files") or []
                print("TREE ep=%s rev=%s files=%d" % (ep, rev, len(files)))
                for f in files:
                    print("  %s  size=%s" % (f.get("Path"), f.get("Size")))
            except Exception as exc:
                print("TREE ep=%s rev=%s FAIL: %s" % (ep, rev, exc))
    guesses = [
        "Qwen3.8-4B-Distill-Q4_K_M.gguf",
        "Qwen3.8-4B-Distill-UD-Q4_K_M.gguf",
        "Qwen3.8-4B-Distill-Q5_K_M.gguf",
        "Qwen3.8-4B-Distill-Q8_0.gguf",
        "Qwen3.8-4B-Distill-Q4_K_S.gguf",
        "Qwen3.8-4B-Distill-Q6_K.gguf",
        "Qwen3.8-4B-Distill-IQ4_XS.gguf",
    ]
    for g in guesses:
        url = "https://modelscope.cn/models/%s/resolve/master/%s" % (REPO, g)
        try:
            st, cl = head(url)
            print("HEAD %s -> %s len=%s" % (g, st, cl))
        except Exception as exc:
            print("HEAD %s FAIL: %s" % (g, exc))
    print("PROBE DONE")


if __name__ == "__main__":
    main()
