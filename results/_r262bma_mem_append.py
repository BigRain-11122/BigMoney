# _r262bma_mem_append.py -- R262 S4: append one pit-law memory line to repo root
# CODELY.md (Reference section, line-level append-only). Byte-safe: probes CRLF
# face and appends with matching EOL. Four-question gate passed: recurring S7
# writer family (R170/R178 third variant), pit > conclusion, one line < 1.5KB.
import sys

P = "CODELY.md"
raw = open(P, "rb").read()
crlf = b"\r\n" in raw
entry = (
    "- [2026-09-26 18:1x] 坑律（bm-a R262·S7 心跳写手 clock_read 分隔符面·R170/R178 家族第三参·E1 轮首 smoke F7 自捕零外泄）："
    "**心跳 clock_read 规格只写「ISO 含 UTC 偏移」未钉分隔符=写手产空格分隔（2026-09-26 17:53:59+08:00），"
    "smoke F7 判据=`\"T\" in clock_read` 判红——正律①写手一律 datetime.now().astimezone().isoformat()（T 分隔）"
    "②正典提示/规格文里探测类字段若含格式歧义必须钉示例值（本轮已在 Tools/iteration_prompt.txt 钉死）"
    "③该族红项修复=值+类型+格式三面同修并按 smoke 判据原文自证，勿只改值**。"
    "指针=results/_r262bma_hb_fix.py+results/_r262bma_prompt_fix.py+smoke_test.py L174-L188"
)
if entry[:30] in raw.decode("utf-8-sig"):
    print("FAIL: entry already present")
    sys.exit(1)
if not raw.endswith(b"\n"):
    raw += b"\r\n" if crlf else b"\n"
data = raw + entry.encode("utf-8") + (b"\r\n" if crlf else b"\n")
with open(P, "wb") as fh:
    fh.write(data)
chk = open(P, "rb").read()
assert entry.encode("utf-8") in chk
import os
print(f"appended; crlf={crlf}; size={os.path.getsize(P)}B (<50KB gate)")
