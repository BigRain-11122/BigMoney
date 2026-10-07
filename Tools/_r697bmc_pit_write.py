"""r697 bm-c pit direct-write: long-round heartbeat lag -> false-dead
stale-takeover -> deterministic double burn (TRIAL-LABOR-W16-GENERATE/main
live case). r637 direct-write precedent (domain file, in-place append) +
byte-accounting receipt. EOL detected from host file, never assumed."""
import hashlib
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIT = os.path.join(ROOT, "research", "pit-pool.md")
OUT = os.path.join(ROOT, "results", "_r697bmc_pit_directwrite.json")

ENTRY = (
    "- [2026-10-07 19:1x r697 bm-c] 长轮心跳滞后=伪死接管双烧坑（TRIAL-LABOR-W16-GENERATE/main 实弹·r637 双烧止损窗姊妹面）："
    "bm-a 18:23:41 autofill launch-claim（d26fb33f）起烧在飞，其 r836 长轮进行中心跳文件停 17:58（滞后 49min·机活 commit 18:22-18:24 在案）"
    "→ bm-c pool_worker 18:47:01 按 STALE_MIN=20 合法接管（claim-stamp 23.4min+hb 49min 双 stale）→ 双机同烧确定性 generate"
    "（重复成本实测 ~0.16 核·字节恒等零数据风险 r637 律）。处置=后到保留不杀：杀无 keep-block 必再领 churn（r617 杀+释放≠防再领）"
    "+若先到 runner 实死则误杀唯一活烧=搁浅；确定性双烧自然收敛（先完成者 commit+harvest 翻 done，后到产物 union-safe）。"
    "根因=stale-takeover 活性信号面只取 heartbeat 文件+claim-stamp，均不反映 burn 活性；长轮心跳滞后 30-60min 三机常态（r696 bm-c 亦 16min）。"
    "How to apply：①stale-takeover 判活须加第三信号=origin 最近 commit 年龄（机最后 push <15min=活·本例 bm-a 18:24 push 在接管时点仅 23min）"
    "或 autofill 侧 burn-heartbeat（pool_worker HEARTBEAT_SEC=300 有·autofill 无对等物）；②同窗 4 lane_io derive 连锁 stale-takeover"
    "（t35/scorecard/dashboard host=bm-a 57-58min）——derive 幂等安全·burn 类才有双烧险，接管门按 face 类型分层；"
    "③确定性 runner 撞车正法=保留双烧自然收敛勿杀勿 churn，非确定性批=后到让路杀+keep-block 三面（r617）。（直写行 r697 bm-c·域内 direct-write r637 范式）\n"
)


def main():
    raw = open(PIT, "rb").read()
    crlf = raw.count(b"\r\n")
    lf_only = raw.count(b"\n") - crlf
    eol = b"\r\n" if crlf >= lf_only else b"\n"
    block = ENTRY.encode("utf-8")
    if eol == b"\r\n":
        block = block.replace(b"\n", b"\r\n")
    pre = len(raw)
    if not raw.endswith(eol):
        raw = raw + eol
    new = raw + block
    with open(PIT, "wb") as fh:
        fh.write(new)
    rec = {
        "round": "r697",
        "target": "research/pit-pool.md",
        "appended_bytes": len(block),
        "appended_md5": hashlib.md5(block).hexdigest(),
        "pre_bytes": pre,
        "post_bytes": len(new),
        "eol_used": eol.decode("utf-8"),
        "law": "r637 direct-write precedent + D-06 domain-file protocol",
    }
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, indent=1, ensure_ascii=False)
    print(json.dumps(rec, ensure_ascii=False))
    # verify: tail bytes contain the entry verbatim
    back = open(PIT, "rb").read()
    assert back.endswith(block), "post-write tail mismatch"
    print("tail-verify OK")


if __name__ == "__main__":
    main()
