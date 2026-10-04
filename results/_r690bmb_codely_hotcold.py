# r690 bm-b CODELY hot/cold: (1) append new pitlaw entry (inbox_guard sender
# line); (2) migrate pure-flow receipt r453 (O-0808 execution record, no law
# face, fully duplicated in fleet/orders + bm-c round report) to
# research/memory-archive/202610.md verbatim + leave cold pointer (r444
# ceremony: byte-exact, marker counts, zero-loss proof).
import io
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODELY = os.path.join(ROOT, "CODELY.md")
ARCHIVE = os.path.join(ROOT, "research", "memory-archive", "202610.md")

NEW_ENTRY = (
    "- [2026-10-04 19:5x r690 bm-b] inbox_guard 声明冻结的发件人解析判据坑（MSG 命名惯"
    "例×guard 双 PAT 均不匹配→本机自己的池声明被 parse 成 unknown=rival 冻结自己的 "
    "autofill submit rc2）：inbox_guard._machine_of=SENDER_PAT（正文「发件[:：]」行）"
    "or MSG_NAME_PAT（文件名 ^MSG-\\d{8}-\\d+-<机>-ALL- 带尾连字符）——现行 fleet MSG "
    "惯例（hyphen 日期「2026-10-04」+「→ ALL」标题+仅「收件」行）两 PAT 全 miss→"
    "sender=None→_norm(None)!=''≠本机 id→自声明=「rival declaration freeze from "
    "unknown」。修=声明 MSG 正文加一行「发件：bm-b」（SENDER_PAT 捕获·_norm 归一比"
    "较过）零改共享 guard；guard 语义无错（fail-closed 对未知发送者=设计态）。How to "
    "apply：写带池条目 id 的 fleet/inbox 声明 MSG 模板必含「发件：<本机>」行；见 "
    "REFUSED「rival declaration freeze ... from unknown」先查发件行缺失，勿怀疑 "
    "guard 勿绕闸。\n")

NEEDLE = b"- [2026-10-04 08:04x r453 bm-c] O-20261004-0808"
POINTER = (
    "- 冷层指针（r690 整编·r444 范式）：r453 bm-c O-20261004-0808-bm-a GM 双裁令执行"
    "记录（纯回执零律面·正典=fleet/orders/O-20261004-0808-bm-a.md+bm-c 轮报 r453）"
    "——全文 verbatim=research/memory-archive/202610.md『热冷整编 2026-10-04 r690 "
    "bm-b 窗批』节。\n").encode("utf-8")

# --- step 1: append new entry at CODELY end ---
raw = open(CODELY, "rb").read()
assert raw.count(NEW_ENTRY.split("\n")[0][:40].encode("utf-8")) == 0, "dup entry gate"
if not raw.endswith(b"\n"):
    raw += b"\n"
raw += NEW_ENTRY.encode("utf-8")

# --- step 2: migrate r453 receipt line verbatim ---
lines = raw.splitlines(keepends=True)
hits = [i for i, ln in enumerate(lines) if ln.startswith(NEEDLE)]
assert len(hits) == 1, "r453 needle hits=%d" % len(hits)
i = hits[0]
victim = lines[i]
assert victim.rstrip().endswith("。".encode("utf-8")), "victim line incomplete?"
section = ("## 热冷整编 2026-10-04 r690 bm-b 窗批\n\n").encode("utf-8")
if os.path.exists(ARCHIVE):
    a_raw = open(ARCHIVE, "rb").read()
    if not a_raw.endswith(b"\n"):
        a_raw += b"\n"
    a_new = a_raw + b"\n" + section + victim
else:
    a_new = section + victim
open(ARCHIVE, "wb").write(a_new)
# zero-loss proof: the archived copy is byte-identical to the removed line
a_chk = open(ARCHIVE, "rb").read()
assert a_chk.count(victim) == 1, "archive verbatim proof FAIL"
lines[i] = POINTER
out = b"".join(lines)
assert out.count(victim) == 0, "victim still present in CODELY"
assert out.count(POINTER) == 1, "pointer count != 1"
open(CODELY, "wb").write(out)

# --- verify ---
chk = open(CODELY, "rb").read()
assert chk.count(POINTER) == 1
assert chk.count(NEEDLE) == 0
assert chk.count(NEW_ENTRY.split("\n")[0][:40].encode("utf-8")) == 1
print("CODELY: new pitlaw appended + r453 receipt migrated verbatim + pointer in place")
print("sizes: CODELY=%d archive_202610=%d" % (len(chk), len(a_chk)))
