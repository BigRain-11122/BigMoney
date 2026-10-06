"""r643 bm-c CODELY main-file flow-sink batch (D-20261002-06 main <=30KB gate leg).
r444/r592/r639/r642 paradigm. Byte-exact surgery: binary read, block match
count==1 asserts, archive delta == removed bytes conservation, receipt JSON.
prescan rc3 recorded honestly per r441 treasure-migration ritual (both files
registered; legislated hot/cold reorganization mandate = authorization face).
"""
import hashlib
import json
import time

MAIN = r"CODELY.md"
ARC = r"research\memory-archive\202610.md"
RCPT = r"results\_r643bmc_codely_sink_receipt.json"
GATE = 30720

def b(s):
    return s.encode("utf-8")

data = open(MAIN, "rb").read()
arc = open(ARC, "rb").read()
main_before = len(data)
arc_before = len(arc)

# target blocks (verbatim from main, without line terminator)
needle_a = b("- [2026-10-06 23:2x r786 bm-b] O-20261006-2110/2250/2257 三 CEO 令同窗执行回执：让路律套件部署（C:\\Fluxgroup\\.codely-cli\\machine-state.ps1 本地化三处=$tasks 10 任务清单/qwen3.8:4b/MiniGameOllamaKeepWarm）+pause 实测 PASS（ollama 杀净 vram 4365→648MB·10 GPU 任务 Disabled·production-clean）+status 落档+2257 resume 复原 PASS（10 任务 Enabled·ollama serve 重启+qwen3.8:4b repin keep_alive=-1·vram 4357MB·MODE=mixed）；静默律双路通知闸设值+读回 0/0+任务自审=自建 23/23 全隐藏链（21 原生 wscript+Skyline 2 任务当窗改链·参数原样透传·machine 级 InvisibleRunner.vbs）+第三方 11 列报不代禁+触发词律/零窗律两行入全局 CODELY.md；回执节已填三令文件。")
needle_b = b("- [2026-10-06T23:18 r798 bm-a] O-20261006-2110/2250 双令 bm-a 执行记录（CEO 用机让路律+机队静默工作律·同窗合并回执 10-07 18:00 大限）：让路律=kit 双件部署 `C:\\Users\\sjs20\\Desktop\\FluxGroup\\.codely-cli\\machine-state.ps1`(v1.1)+pause 实测 OK（首跑揭 Ollama 托盘 app respawn 盲区→本机补 kill 面修复·VRAM 6748→1089MB·status MODE=pause·resume 固化未跑）；静默律=双路通知闸 0/0 读回+13 自建任务转 wscript 隐藏链（13/13 零败）+零窗律入用户级 CODELY.md；触发词「我要打游戏/我要工作=本机 pause·全面开工=resume+O 令广播」入记忆。正典=两令件 bm-a 回执节；坑=kit 模板托盘盲区建议回流上游。How to apply：听到触发词即进程内 `&` 执行开关勿再问。")

assert data.count(needle_a) == 1, "needle_a count != 1: %d" % data.count(needle_a)
assert data.count(needle_b) == 1, "needle_b count != 1: %d" % data.count(needle_b)

# line terminator style of main (r402 law: no double-count of line-boundary
# terminators; strip exactly ONE trailing terminator per removed block)
def span_with_terminator(buf, needle):
    i = buf.find(needle)
    j = i + len(needle)
    if buf[j:j+2] == b"\r\n":
        j += 2
    elif buf[j:j+1] in (b"\n", b"\r"):
        j += 1
    return i, j, buf[i:j]

ia, ja, block_a = span_with_terminator(data, needle_a)
ib, jb, block_b = span_with_terminator(data, needle_b)

# remove B first (higher index) to keep A indices valid
assert ib > ia or jb < ia or ib > ja  # overlap sanity: must not overlap
data2 = data[:ib] + data[jb:]
i2, j2, _ = span_with_terminator(data2, needle_a)
data2 = data2[:i2] + data2[j2:]

# compact pointer line appended at Reference tail (file end)
ptr = b("- 冷层指针（r643 合并·r444 范式）：r786 bm-b O-20261006-2110/2250/2257 三令执行回执+r798 bm-a O-20261006-2110/2250 双令执行记录（纯回执零新律·正典=各令件回执节）——两条全文 verbatim=archive 202610.md『热冷整编 2026-10-07 r643 bm-c 窗批』节。")
data2 = data2 + b"\n" + ptr + b"\n" if not data2.endswith(b"\n") else data2 + ptr + b"\n"

# archive append: section + two verbatim blocks
sec = b("\n## 热冷整编 2026-10-07 r643 bm-c 窗批（CODELY 主件流水下沉·r444/D-20260924-01 范式·receipt=results/_r643bmc_codely_sink_receipt.json）\n")
arc2 = arc + sec + block_a + block_b

# conservation asserts
assert len(block_a) + len(block_b) == (len(arc2) - len(arc) - len(sec)), "archive delta != removed bytes"
assert needle_a in arc2 and needle_b in arc2, "verbatim blocks missing in archive"
assert needle_a not in data2 and needle_b not in data2, "block residue in main"
main_after = len(data2)
assert main_after <= GATE, "main still over gate: %d" % main_after

open(MAIN, "wb").write(data2)
open(ARC, "wb").write(arc2)

rcpt = {
    "round": "r643 bm-c",
    "ts": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
    "batch": "CODELY main flow-sink (r786 bm-b receipt + r798 bm-a receipt -> archive 202610.md)",
    "law_refs": ["D-20261002-06 main<=30KB gate leg", "D-20260924-01 hot/cold reorg", "TREASURE_PROTECTION_LAW s2 prescan ritual r441"],
    "prescan": "rc3 registry-hit recorded honestly (CODELY.md + archive 202610.md both registered; legislated reorg mandate = authorization)",
    "main_before_bytes": main_before,
    "main_after_bytes": main_after,
    "gate": GATE,
    "gate_ok": main_after <= GATE,
    "removed_block_bytes": [len(block_a), len(block_b)],
    "removed_sha16": [hashlib.sha256(block_a).hexdigest()[:16], hashlib.sha256(block_b).hexdigest()[:16]],
    "pointer_line_sha16": hashlib.sha256(ptr).hexdigest()[:16],
    "archive_before_bytes": arc_before,
    "archive_after_bytes": len(arc2),
    "zero_loss": "archive_delta == sum(removed) ; both blocks verbatim in archive ; zero residue in main",
}
open(RCPT, "w", encoding="utf-8").write(json.dumps(rcpt, ensure_ascii=False, indent=1))
print("MAIN", main_before, "->", main_after, "gate_ok", main_after <= GATE)
print("BLOCKS", len(block_a), len(block_b), "archive_delta", len(arc2) - len(arc))
print("RECEIPT", RCPT)
