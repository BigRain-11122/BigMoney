# r237 (bm-a): byte-precise single-line insert into Tools/iteration_prompt.txt
# update_moneyflow leg (R236 _r236_prompt_insert.py family pattern: no BOM,
# CRLF-preserving, idempotent guard). Mirrors the sina leg's R236 amendment
# wording: stale face -> refresh-repull done-reset semantics.
import io

PATH = "Tools/iteration_prompt.txt"
raw = open(PATH, "rb").read()
assert b"\xef\xbb\xbf" != raw[:3], "unexpected BOM"
assert raw.count(b"\r\n") == raw.count(b"\n") == 1, "single-line CRLF shape expected"

OLD = "首拉/未完成/过期=分离后台全宇宙刷新（5222 股 2.5s 限速 checkpoint 断点续拉，锁+30min spawn 节流+连接级 3 连失败源阻断停发=阻断解除后自愈，".encode("utf-8")
NEW = ("首拉/未完成=分离后台全宇宙刷新（5222 股 2.5s 限速 checkpoint 断点续拉，锁+30min spawn 节流+连接级 3 连失败源阻断停发=阻断解除后自愈；"
       "过期（complete 面板 cutoff 落后 20td）=refresh-repull done-reset 全宇宙复拉+零符号轮终态 cutoff 面板字节 derive（R237 修正案·R236 族移植），").encode("utf-8")
assert "R237 修正案".encode("utf-8") not in raw, "already inserted (idempotent guard)"
assert raw.count(OLD) == 1, "anchor not unique: %d" % raw.count(OLD)
patched = raw.replace(OLD, NEW)
open(PATH, "wb").write(patched)

raw2 = open(PATH, "rb").read()
assert raw2.count(b"\r\n") == raw2.count(b"\n") == 1, "line shape preserved"
assert "R237 修正案·R236 族移植".encode("utf-8") in raw2
text = raw2.decode("utf-8")
i = text.find("R237 修正案")
print("insert OK; context: ...%s..." % text[i-80:i+60])
