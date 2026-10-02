"""r383 bm-c O-2100 §二 capture-law wiring into Tools/iteration_prompt.txt:
insert the 4-closure-point capture block before the trailing 铁律 segment of
the flow line. Bytes-in/bytes-out, EOL preserved (r530/r500)."""
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\Tools\iteration_prompt.txt"
with open(P, "rb") as f:
    raw = f.read()
crlf = raw.count(b"\r\n") > (raw.count(b"\n") - raw.count(b"\r\n"))
print("EOL:", "CRLF" if crlf else "LF", "| bytes:", len(raw))

anchor = "铁律：全静默零弹窗；".encode("utf-8")
assert raw.count(anchor) == 1, f"anchor count={raw.count(anchor)}"
block = ("【捕获律接线（O-20261002-2100-bm-c §二·首 ack 机焊·资产正典=knowledge/"
         "METHODOLOGY_ASSETS.md）】四类收口点各带一步「本批有无新方法？有→当轮 "
         "append 资产卡+定向 add knowledge/METHODOLOGY_ASSETS.md」：①S3 判决批 "
         "finalize 收口（judged 批落账轮）②S6 审计收口（compute_audit/post_review "
         "复审定谳轮）③S0.5 治理案收口（CEO 令/裁决令执行轮）④S4 工程净路收口"
         "（CODELY 坑律首立轮——坑律中可复用方法面同步入卡）；卡面人话+证据指针+"
         "状态 proven/candidate；月度盘点=值守轮每月首轮（去重/合并/状态翻面）；"
         "回访 2026-10-08 治理日（四点实证 append+库内卡≥20+至少一起负方法卡省烧"
         "案例在册）。").encode("utf-8")
eol = b"\r\n" if crlf else b"\n"

idx = raw.index(anchor)
new = raw[:idx] + block + eol + raw[idx:]
with open(P, "wb") as f:
    f.write(new)
print("inserted", len(block), "bytes before 铁律 anchor")

with open(P, "rb") as f:
    chk = f.read()
assert chk.count(anchor) == 1
assert block in chk
assert len(chk) == len(raw) + len(block) + len(eol)
lines = chk.replace(b"\r\n", b"\n").split(b"\n")
print("line count:", len(lines), "| capture block line present:",
      any(b"\xe6\x8d\x95\xe8\x8e\xb7\xe5\xbe\x8b\xe6\x8e\xa5\xe7\xba\xbf" in x for x in lines))
print("WIRING LANDED")
