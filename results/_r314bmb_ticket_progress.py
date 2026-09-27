"""r314 bm-b: ticket progress fields (T-89/T-90) -- pool-flip standing action."""
import json

FLIP_LAW = ("r314 bm-b: batch grind live (autofill ~1 shard/tick/machine). "
            "X2-LB done+pool-flipped (marker 1884/1884, commit 607354b2, "
            "r302 flip-first law) 1/9; X2-LA bm-a in-flight; X2-LC..DE + "
            "PROSPECT 9 pending. STANDING ACTION every bm-b round until "
            "9/9: rerun results/_r314bmb_pool_flip.py (idempotent, "
            "evidence-gated done-marker check, probe-subset markers "
            "refused) BEFORE the local autofill tick ages any "
            "locally-completed shard past FUSE_CONFIRM_MIN=25min "
            "(O-0947 false crash-fuse on fast <25min shards). All 9 "
            "X2 done -> harvest verdict face per prereg s10.")

PROS_LAW = ("r314 bm-b: 0/9 shards launched yet (pool grind: X2 batch "
            "entries sort first, same priority; autofill advances after). "
            "LA has probe 22 cells only (r313 real-fire). STANDING ACTION "
            "every bm-b round until 9/9: rerun results/_r314bmb_pool_flip.py "
            "after local shard completions (same O-0947 false-crash-fuse "
            "law as T-90, r302 flip-first; PROSPECT runners write done "
            "markers results/pros_segs/done_*). All 9 done -> harvest "
            "finalize face per prereg s6.")

for path, field, text in [
    ("fleet/tasks/T-2026-09-27-90-P1.json", "progress_r314_bmb", FLIP_LAW),
    ("fleet/tasks/T-2026-09-26-89-P1.json", "progress_r314_bmb", PROS_LAW),
]:
    raw = open(path, "rb").read()
    d = json.loads(raw.decode("utf-8-sig"))
    d[field] = text
    nl = "\r\n" if b"\r\n" in raw[:300] else "\n"
    bom = b"\xef\xbb\xbf" if raw[:3] == b"\xef\xbb\xbf" else b""
    with open(path, "wb") as fh:
        fh.write(bom + (json.dumps(d, ensure_ascii=False, indent=1) + nl)
                 .encode("utf-8"))
    chk = json.load(open(path, encoding="utf-8-sig"))
    assert field in chk and chk["status"] == "claimed"
    print(f"patched {path}: +{field} (status stays {chk['status']})")
