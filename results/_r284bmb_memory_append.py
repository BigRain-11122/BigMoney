"""r284 bm-b S4: CODELY.md one-line lesson append (four-question gate passed).

Byte faces probed: no BOM, CRLF EOL, trailing newline present. Append mirrors
CRLF + keeps tail newline (R255/R257 mirror law). Line-level append only.
"""
import io

P = "CODELY.md"
raw = open(P, "rb").read()
assert raw[:3] != b"\xef\xbb\xbf", "BOM face drifted"
assert b"\r\n" in raw, "expected CRLF face"
assert raw.endswith(b"\n"), "tail newline missing"
assert b"\x00" not in raw

LINE = (
    " - [2026-09-27 00:4x] 坑律（bm-b r284·Optuna 解封门在册计数面·E1 轮内自捕零外泄）"
    "：**firm/traders/ 目录 glob 计「在册 validated」两面陷阱——_template.json 示例 "
    "id 字段=\"TREND-001\"（按 id 字段读=模板占位被计作交易员）+ PROS-* 前瞻袖文件"
    "同目录混放（按文件数计=29 假读数）**；正律=validated 计数面=排除 _template.json"
    " 与 PROS-* 前缀后的文件集（真实面=6：COMPOSITE-CE-01/02、DROUGHT-CE-01、"
    "ENGULF-CE-01、NEEDLE-DE-01、VOLATILITY-CE-01），Optuna 解封判据"
    "（O-20260924-1120 冻结 ≥8）按此口径复核；连带=假读数（\"TREND-001 瞬态文件\"）"
    "引发的三探针异常调查全为读面错误、零真实缺陷——目录枚举消费面遇模板件/示例"
    "字段必须显式排除，勿按内容 id 字段计实体。指针=results/_r284bmb_watch.py 修正段"
    "+results/_r284bmb_watch_faces.json optuna_unlock 面\r\n"
)

with io.open(P, "ab") as f:
    f.write(LINE.encode("utf-8"))

raw2 = open(P, "rb").read()
assert raw2.endswith(b"\r\n")
assert raw2[:3] != b"\xef\xbb\xbf"
assert len(raw2) - len(raw) == len(LINE.encode("utf-8"))
print("CODELY.md appended:", len(raw), "->", len(raw2), "bytes (delta", len(raw2)-len(raw), ")")
