# R236 bm-a: post_review registry T-72 row append (R223 closure-pairing law:
# checks encode spec pre-frozen verification lines only, zero invented).
# Text-level insert before items-array close; CRLF/indent=2 preserved.
import json

P = "results/post_review_criteria.json"
b = open(P, "rb").read()
t = b.decode("utf-8")
orig = t
assert "T-72-SINA-MF-COLLECTOR" not in t, "row already present"

ANCHOR = '\r\n  ],\r\n  "_reconciled":'
assert t.count(ANCHOR) == 1, f"anchor {t.count(ANCHOR)}"

ROW = ''',
    {
      "id": "T-72-SINA-MF-COLLECTOR",
      "claim": "T-72 sina \u56db\u6863\u8d44\u91d1\u6d41\u91c7\u96c6\u5668\u4e09\u5207\u7247\u4ea4\u4ed8\uff1as1 \u91c7\u96c6\u5668+\u79bb\u7ebf selftest \u7eff\uff1bs2 \u5168\u5b87\u5b99\u9996\u62c9\u9a8c\u6536\u4e94\u7ebf PASS\uff08fresh 5222\u22655000\u00b7\u5199\u76d8\u9762\u96f6\u8fdd\u4f8b worst 9.33e-10\u00b7\u5b8c\u6574\u6027\u96f6\u7f3a\u9677\u00b7\u9884\u7b97<10456\u00b7selftest \u7eff\uff09+\u00a74.3 \u540c\u65e5\u5e42\u7b49 spot 8/8 sha256 \u5b57\u8282\u6052\u7b49\uff1bs3 S6 \u94fe\u63a5\u7ebf\uff08update_moneyflow \u540e update_sina_mf gate \u817f\uff09+R236 \u4fee\u6b63\u6848\uff08refresh-repull done-reset \u590d\u62c9\u8bed\u4e49+\u7ec8\u6001 cutoff \u9762\u677f\u5b57\u8282 derive\uff09\u95ed R235 \u4e24\u6f5c\u4f0f\u7f3a\u9677",
      "claim_source": "T-2026-09-26-72 spec (slices s1/s2/s3 + verification lines) + research/shortline/SINA_MF_PREREG.md sec4/sec5 (R221-R236)",
      "status": "closed",
      "checks": [
        {
          "kind": "file_exists",
          "args": [
            "scripts/update_sina_mf.py"
          ]
        },
        {
          "kind": "json_field",
          "args": [
            "results/sina_mf_accept.json",
            "verdict",
            "PASS"
          ]
        },
        {
          "kind": "json_gte",
          "args": [
            "results/sina_mf_accept.json",
            "counts.fresh_covered",
            "5000"
          ]
        },
        {
          "kind": "file_contains",
          "args": [
            "Tools/iteration_prompt.txt",
            "update_sina_mf"
          ]
        },
        {
          "kind": "file_contains",
          "args": [
            "scripts/update_sina_mf.py",
            "_panel_cutoff_from_bytes"
          ]
        }
      ]
    }
  ],
  "_reconciled":'''

t = t.replace(ANCHOR, ROW)

# reconcile log line (R223 pattern: append to _reconciled string)
RECON_ADD = (' | 2026-09-26 09:1x r236 bm-a: T-72-SINA-MF-COLLECTOR row added at '
             'ticket closure (s3 wired same round per CEO immediate-law; ticket '
             'flipped done same round); checks encode spec-frozen verification '
             'lines only (s2 accept verdict=PASS, sec4 fresh coverage >=5000, s1 '
             'collector script, s3 prompt leg, R236 amendment helper pre-frozen '
             'in sec5 R235 note), zero invented')
i = t.rfind('"\r\n}')
assert i > 0, "reconciled tail anchor absent"
t = t[:i] + RECON_ADD + t[i:]

open(P, "wb").write(t.encode("utf-8"))
d = json.load(open(P, encoding="utf-8-sig"))
ids = [it["id"] for it in d["items"]]
print("items:", len(ids), "| T-72 row:", "T-72-SINA-MF-COLLECTOR" in ids)
print("reconciled tail:", d["_reconciled"][-120:])
