# r700 bm-b: CODELY.md main-file rebound hot/cold re-archival batch 1 (D-20261002-06 open leg)
# 87 dated Reference-section pit entries -> domain files, verbatim, zero-loss asserted.
import hashlib, json, os, re

MAIN = "CODELY.md"
raw = open(MAIN, "rb").read()
crlf_main = b"\r\n" in raw
EOL = b"\r\n" if crlf_main else b"\n"
text = raw.decode("utf-8")
if crlf_main:
    text = text.replace("\r\n", "\n")
lines = text.split("\n")
if lines and lines[-1] == "":
    lines = lines[:-1]
n = len(lines)
assert n >= 137, f"unexpected line count {n}"

DOM = {
 36:"pool", 38:"tooling", 39:"pool", 40:"engine", 41:"git-netpath", 42:"protocol",
 43:"data", 44:"tooling", 46:"pool", 47:"protocol", 48:"git-parse", 49:"git-netpath",
 50:"git-parse", 51:"ps", 52:"protocol", 53:"git-netpath", 54:"protocol", 55:"protocol",
 56:"ps", 57:"git-surgery", 58:"protocol", 60:"engine", 61:"ps", 64:"tooling", 65:"ps",
 66:"git-parse", 69:"git-surgery", 70:"git-netpath", 71:"git-parse", 72:"tooling",
 73:"pool", 74:"protocol", 75:"tooling", 76:"engine", 78:"protocol", 80:"engine",
 82:"git-netpath", 83:"git-parse", 85:"data", 87:"protocol", 88:"ps", 90:"pool",
 92:"git-parse", 93:"engine", 94:"engine", 95:"git-surgery", 96:"protocol", 97:"pool",
 98:"pool", 99:"git-staged", 100:"protocol", 101:"data", 102:"spawn", 103:"tooling",
 104:"tooling", 105:"git-surgery", 106:"engine", 107:"protocol", 108:"tooling",
 109:"engine", 110:"protocol", 111:"pool", 112:"protocol", 113:"engine", 114:"spawn",
 115:"engine", 116:"engine", 117:"tooling", 118:"engine", 119:"pool", 120:"pool",
 121:"git-netpath", 122:"tooling", 123:"ps", 124:"engine", 125:"protocol", 126:"ps",
 127:"pool", 128:"spawn", 129:"pool", 130:"ps", 131:"pool", 132:"tooling", 133:"git-parse",
 134:"git-netpath", 136:"ps", 137:"git-parse",
}
FILE = {"git-netpath":"research/pit-git-netpath.md","git-parse":"research/pit-git-parse.md",
        "git-surgery":"research/pit-git-surgery.md","git-staged":"research/pit-git-staged.md",
        "engine":"research/pit-engine.md","pool":"research/pit-pool.md",
        "protocol":"research/pit-protocol.md","data":"research/pit-data.md",
        "ps":"research/pit-ps.md","tooling":"research/pit-tooling.md",
        "spawn":"research/pit-spawn.md","encoding":"research/pit-encoding.md"}

entry_re = re.compile(r"^- \[")
ptr_re = re.compile(r"^- (?:冷层指针|域指针|坑律正典)")

blocks, keeps = [], []
dropped_blank_lines = 0
i = 35
while i < n:
    ln = lines[i]
    if entry_re.match(ln):
        j = i + 1
        while j < n and not (entry_re.match(lines[j]) or ptr_re.match(lines[j])):
            j += 1
        block = lines[i:j]
        while block and block[-1].strip() == "":
            block.pop()
        blocks.append({"line": i + 1, "dom": DOM[i + 1], "lines": block})
        # count dropped blanks between this block end and next bullet (or EOF)
        k = i + len(block)
        while k < n and lines[k].strip() == "":
            dropped_blank_lines += 1
            k += 1
        i = j
    elif ptr_re.match(ln):
        keeps.append(ln)
        i += 1
    else:
        dropped_blank_lines += 1
        i += 1

missing = [b["line"] for b in blocks if b["line"] not in DOM]
assert not missing, f"missing DOM: {missing}"
assert len(blocks) == 87, f"expected 87 blocks, got {len(blocks)}"
assert len(keeps) == 2, f"expected 2 keeps, got {len(keeps)}: {[k[:24] for k in keeps]}"

dom_before = {p: os.path.getsize(p) for p in FILE.values() if os.path.exists(p)}
receipt_entries = []
for b in blocks:
    path = FILE[b["dom"]]
    praw = open(path, "rb").read()
    teol = b"\r\n" if b"\r\n" in praw else b"\n"
    bt = "\n".join(b["lines"])
    if teol == b"\r\n":
        bb = bt.replace("\n", "\r\n").encode("utf-8")
    else:
        bb = bt.encode("utf-8")
    hdr = praw[:-1] if praw.endswith(b"\n") else praw
    open(path, "wb").write(hdr + teol + teol + bb + teol)
    after = open(path, "rb").read()
    assert after.count(bb) >= 1, f"zero-loss FAIL block {b['line']}"
    receipt_entries.append({"line": b["line"], "dom": b["dom"], "bytes": len(bb),
                            "sha16": hashlib.sha256(bb).hexdigest()[:16],
                            "hdr": b["lines"][0][:70]})
dom_after = {p: os.path.getsize(p) for p in FILE.values() if os.path.exists(p)}

PTR_ROW = ("- 域指针·r700 bm-b CODELY 主件回弹热冷整编批（D-20261002-06 主件回弹处置腿·2026-10-04 r700 bm-b）："
           "Reference 节 10-03~10-04 增量坑律 87 条 verbatim 分域迁入各 pit 件"
           "（git 族=netpath/parse/surgery/staged·engine/pool/protocol/data/ps/tooling/spawn）——"
           "主件回弹处置收口；逐条字节+sha16 对账=receipt results/_r700bmb_d06_batch1_receipt.json"
           "（零丢失断言=逐块 bytes in target verbatim+主件字节恒等式+保留面恒等）；"
           "域件 ≤30KB 再平衡（流水下沉腿）=D-06 收口窗 10-07 维持；新坑律仍先入本件后回扫。")
new_lines = lines[:35] + [PTR_ROW] + keeps
new_text = "\n".join(new_lines) + "\n"
new_bytes = (new_text.replace("\n", "\r\n").encode("utf-8") if crlf_main
             else new_text.encode("utf-8"))
open(MAIN, "wb").write(new_bytes)

# byte identity equation: raw - moved_block_bytes(with main eol) - dropped_blanks + ptr_row == new
eol_len = len(EOL)
moved_main = sum(len("\n".join(b["lines"]).encode("utf-8")) + eol_len * (len(b["lines"]) - 1) + eol_len
                 for b in blocks)  # block lines + intra eols + 1 trailing eol
ptr_b = len(PTR_ROW.encode("utf-8")) + eol_len
expected_new = len(raw) - moved_main - dropped_blank_lines * eol_len + ptr_b
new_len = os.path.getsize(MAIN)
assert new_len == expected_new, f"byte identity FAIL: new={new_len} expected={expected_new}"

nt = open(MAIN, "rb").read().decode("utf-8").replace("\r\n", "\n")
assert lines[9] in nt, "s4 pin row 1 lost"
assert lines[13] in nt, "s4 pin row 2 lost"
for k in keeps:
    assert k in nt, "pointer row lost"
head_ok = nt.startswith("\n".join(lines[:35]))

res = {
  "batch": "r700bmb CODELY main-file rebound re-archival batch-1",
  "decision_ref": "D-20261002-06 main<=30KB + pit laws to domain files; D-20261004-05 rebound-handling leg",
  "main_bytes_before": len(raw), "main_bytes_after": new_len,
  "byte_identity": "PASS" if new_len == expected_new else "FAIL",
  "entries_moved": len(blocks), "moved_bytes_sum": sum(e["bytes"] for e in receipt_entries),
  "dropped_blank_lines": dropped_blank_lines, "main_eol_crlf": crlf_main,
  "dom_growth": {p: dom_after[p] - dom_before[p] for p in dom_before if p in dom_after},
  "dom_sizes_after": dom_after,
  "head_region_identical": head_ok, "s4_pin_rows_kept": True,
  "inrange_pointer_rows_kept": len(keeps),
  "per_entry": receipt_entries,
}
rp = "results/_r700bmb_d06_batch1_receipt.json"
open(rp, "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print(f"main {len(raw)} -> {new_len} B | moved {len(blocks)} entries {sum(e['bytes'] for e in receipt_entries)}B | blanks dropped {dropped_blank_lines}")
print("dom growth:", {k.split('/')[-1]: v for k, v in res["dom_growth"].items()})
print("head identical:", head_ok, "| identity:", res["byte_identity"])
print("receipt:", rp)
