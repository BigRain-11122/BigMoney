# -*- coding: utf-8 -*-
"""r843 bm-a CODELY mini-increment (D-20261002-06 main <=30,720B law):
migrate the r842 S5-ledger pit entry verbatim out to
research/pit-protocol-lane.md (append-only ledger machinery domain),
insert the new r843 ledger-tail-glue pit into main, byte-account both
faces, write receipt results/_r843bma_codely_increment.json.
Ceremony: r441/r703/r783 compact form (verbatim-in-target + main
under-line + zero-loss assertion)."""
import io
import json
import hashlib

MAIN = "CODELY.md"
TGT = "research/pit-protocol-lane.md"

main = io.open(MAIN, encoding="utf-8", newline="").read()
lines = main.splitlines(keepends=True)
idx = [i for i, ln in enumerate(lines)
       if ln.startswith("- [2026-10-07 20:5x r842 bm-a] **S5 轮账本行多轮连续丢失坑")]
assert len(idx) == 1, "r842 pit locate %d" % len(idx)
entry = lines[idx[0]]
print("r842 pit entry bytes:", len(entry.encode("utf-8")))

TSMARK = "- [2026-10-07 21:1x r843 bm-a] **S5 账本尾行无终结符粘连坑"
newpit = (
    "- [2026-10-07 21:1x r843 bm-a] **S5 账本尾行无终结符粘连坑（r842 坑姊妹面·当场自愈零 origin 伤害）**："
    "python append 落账本行前未探文件尾终结符——r842 rebase 手术窗留下的尾行无 CRLF 面上盲写「line+CRLF」="
    "新行粘连进尾行（splitlines 计数恒等 1634→1634 即粘连铁证；自检「tail 含 r843」假绿=粘连行同含该串）。"
    "治愈=正则定位新行 ts 头单点拆分插 CRLF（1635 行·r842 块完好实核·diff numstat 2+/1- 合规）。"
    "How to apply：①append 前必探 src.endswith((CRLF, LF))——缺终结符=先补 CRLF 再写新行；"
    "②追加后自检=行数+1 与尾行 startswith(ts) 双面（计数恒等=红旗）；"
    "③多写者台账追加一律 python 单件新鲜读-改-写（r10-06 律重申）+diff --numstat 非预期删行零容忍。\r\n"
)
newpit_b = newpit.encode("utf-8")
print("new pit bytes:", len(newpit_b))

before_b = len(main.encode("utf-8"))
proj = before_b - len(entry.encode("utf-8")) + len(newpit_b)
print("main bytes: before", before_b, "projected", proj,
      "under-line", proj <= 30720)
assert proj <= 30720, "projected over line"

# migrate out (probe target terminator first -- the r843 law applied live)
tgt = io.open(TGT, encoding="utf-8", newline="").read()
assert "S5 轮账本行多轮连续丢失坑" not in tgt, "target already carries entry"
glue = "" if tgt.endswith(("\r\n", "\n")) else "\r\n"
tgt_new = tgt + glue + entry
io.open(TGT, "w", encoding="utf-8", newline="").write(tgt_new)

# main: remove entry + insert new pit at the entry's former position
assert main.endswith("\r\n"), "main tail terminator missing"
main_new = main.replace(entry, newpit, 1)
assert "S5 轮账本行多轮连续丢失坑" not in main_new, "main removal failed"
assert TSMARK in main_new, "new pit not in main"
io.open(MAIN, "w", encoding="utf-8", newline="").write(main_new)

# zero-loss + under-line assertions
tgt_chk = io.open(TGT, encoding="utf-8", newline="").read()
main_chk = io.open(MAIN, encoding="utf-8", newline="").read()
assert entry in tgt_chk, "verbatim-in-target FAILED"
assert newpit in main_chk, "new-pit-in-main FAILED"
mb = len(main_chk.encode("utf-8"))
assert mb <= 30720, "main over line: %d" % mb
tb = len(tgt_chk.encode("utf-8"))
assert tb <= 30720, "target domain file over line: %d" % tb

receipt = {
    "window": "r843 bm-a",
    "law": "D-20261002-06 main <=30,720B increment (r441/r703/r783 ceremony compact form)",
    "migrated": {
        "entry_head": entry[:80],
        "bytes": len(entry.encode("utf-8")),
        "target": TGT,
        "verbatim_in_target": True,
    },
    "added": {
        "entry_head": newpit[:80],
        "bytes": len(newpit_b),
        "location": "main",
    },
    "main_bytes_before": before_b,
    "main_bytes_after": mb,
    "target_bytes_after": tb,
    "target_glue_crlf_applied": bool(glue),
    "zero_loss": "entry bytes verbatim in target; new pit verbatim in main; both files under line",
    "sha16_main_after": hashlib.sha256(main_chk.encode("utf-8")).hexdigest()[:16],
    "sha16_target_after": hashlib.sha256(tgt_chk.encode("utf-8")).hexdigest()[:16],
}
io.open("results/_r843bma_codely_increment.json", "w", encoding="utf-8").write(
    json.dumps(receipt, indent=1, ensure_ascii=False))
print("INCREMENT OK: main", before_b, "->", mb,
      "| target +", len(entry.encode("utf-8")), "B verbatim | receipt written")
