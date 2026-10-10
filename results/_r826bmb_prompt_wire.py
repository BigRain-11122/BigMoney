# r826 bm-b T-18 prompt wiring: insert advisory queue-head collision guard leg into
# Tools/iteration_prompt.txt S3 self-drive face (r931 anchor-surgery pattern: leg present
# once, byte-precise, size delta reported). ASCII-only source and insertion (r823 law).
import io

P = "Tools/iteration_prompt.txt"
GUARD = ("before claiming any P2/P3 queue head run python scripts\\queue_head_collision_probe.py "
         "(T-18 advisory guard, wired r826 bm-b: verdict COLLISION_RISK/DECLARED_INTENT_RISK = "
         "another machine in-flight or has declared that head -> yield it, take next row or "
         "standing agenda; STALE_LOCAL_QUEUE = pull first, local queue face behind origin; "
         "CLEAR = claimable; law: E3 dual-consume r823/r947 + E4 r825/r948 live-fire); ")
ANCHOR = "\u677f\u7a7a\u4e14 smoke \u5168\u7eff\u65f6\u5148\u81ea\u52a8\u62bd"  # ASCII-escaped anchor

b = io.open(P, "rb").read()
assert b.count(ANCHOR.encode("utf-8")) == 1, "anchor count != 1"
assert b.count(GUARD.encode("ascii")) == 0, "guard already present"
crlf_before = b.count(b"\r\n")
new = b.replace(ANCHOR.encode("utf-8"), GUARD.encode("ascii") + ANCHOR.encode("utf-8"), 1)
assert new.count(GUARD.encode("ascii")) == 1, "leg not present once after surgery"
assert new.count(ANCHOR.encode("utf-8")) == 1, "anchor lost"
assert new.count(b"\r\n") == crlf_before, "CRLF count changed"
assert b"<<<<<<<" not in new and b">>>>>>>" not in new
io.open(P, "wb").write(new)
print("PROMPT WIRED: %d -> %d bytes (+%d), CRLF preserved, leg x1, anchor x1"
      % (len(b), len(new), len(new) - len(b)))
