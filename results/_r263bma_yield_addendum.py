# -*- coding: utf-8 -*-
"""R263 bm-a yield addendum: round report line + heartbeat verdict refresh."""
import json

NOW = "2026-09-26 18:5x"


def faces(path):
    raw = open(path, "rb").read()
    return {"bom": raw[:3] == b"\xef\xbb\xbf", "crlf": b"\r\n" in raw,
            "trail_nl": raw.endswith(b"\n")}


def mirror_append(path, text):
    f = faces(path)
    raw = open(path, "rb").read()
    sep = b"\r\n" if f["crlf"] else b"\n"
    add = text.encode("utf-8")
    body = raw + add + sep if f["trail_nl"] else raw + sep + add + sep
    open(path, "wb").write(body)


def mirror_write_json(path, obj, f):
    body = json.dumps(obj, ensure_ascii=False, indent=1)
    if f["bom"]:
        body = "\ufeff" + body
    if f["crlf"]:
        body = body.replace("\n", "\r\n")
    if f["trail_nl"] and not body.endswith("\r\n" if f["crlf"] else "\n"):
        body += "\r\n" if f["crlf"] else "\n"
    open(path, "wb").write(body.encode("utf-8"))


# 1. round report yield addendum
P = "logs/iteration-loop/round_reports-bm-a.md"
rr = ("2026-09-26 18:5x | R263 bm-a ADDENDUM | T-83 same-window claim collision resolved per fleet/README.md s4 commit-time ordering: "
      "bm-b 18:46:30 (r267, s1 nine-layer inventory + s2 mechanical detection, s3 GM reserved, s4 open) EARLIER = canonical claim kept verbatim; "
      "bm-a 18:47:11 later -> YIELDED: bm-a claim fields dropped from ticket, yield_note_bm_a injected (L9 orders-index artifact DONATED to s1/s2 owner: "
      "results/orders_index.json 83 orders / 33 real cross-refs, deterministic re-runnable results/_r263bma_orders_index.py, supersession adjudication reserved GM s3); "
      "commit message amended claim->yield in pre-push window (r239 law); resolver=results/_r263bma_resolve.py (parse-verified before write-back); "
      "s4 quarterly wiring confirmation open for future bm-a rounds")
mirror_append(P, rr)

# 2. heartbeat verdict/current_task refresh (single-writer file)
P = "fleet/machines/bm-a.json"
hb = json.loads(open(P, encoding="utf-8-sig").read())
hb["current_task"] = "R263 closed: CN-CORE-DDCTL residue arc landed+harvested (judged negative honest); T-83 claim YIELDED to bm-b (s1/s2 owner) with orders-index artifact donated via yield_note"
hb["verdict"] = hb.get("verdict", "").split("; O-1355")[0] + ("; O-1355 caught by S7 double-scan -> T-83 same-window claim collision YIELDED to bm-b 18:46:30 "
                                                             "(bm-a 18:47:11 later, s4 law), L9 orders index 83/33 donated via ticket yield_note; smoke 25/25; S6 24 legs exit 0")
mirror_write_json(P, hb, faces(P))
chk = json.loads(open(P, encoding="utf-8-sig").read())
assert isinstance(chk["heartbeat_epoch_utc"], int)
print("addendum + heartbeat refresh complete, epoch int ok")
