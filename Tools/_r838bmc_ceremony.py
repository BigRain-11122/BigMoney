# r838 bm-c: CODELY.md ceremony surgery (LF-primary main file)
# (1) insert r836 mini-split pointer row (r836 session debt, discloses rebase2 child file)
# (2) re-scan 4 cold entries verbatim out to domain pit files (main stays <=30,720B)
# (3) receipt with byte accounting + verbatim assertions
import json, hashlib, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def p(rel): return os.path.join(ROOT, rel)

MAIN = p('CODELY.md')
CAP = 30720

PTR_ROW = ("- 域指针·r836 bm-c 域件 sub-split（10-10 19:4x 执行·20:5x r838 补登记=r836 会话欠账销账·仪式 r731/r791/r833 同款）："
"pit-git-resolver-rebase.md 母件 30,652B>30,720B 越帽当窗即办——r516 bm-c（rebase resolver no-ts fallback 盲取 mine 回退坑+daemon-treadmill continue 抢窗法）"
"与 r782 bm-a（rebase 31-UU 窗 host-ours 宿主面取侧=重放件 ref 非 stage-2）两最旧条合计 2,521B verbatim 迁出→**research/pit-git-resolver-rebase2.md**"
"（新子件·rebase/sequencer 域 child-2·执法面同母件·母件余条+新增 append 面仍以母件为正典）"
"+r836 新律（竞速环 rebase-merge 在位时 commit/push=detached HEAD 推 stale 分支引用空转坑+r808 标记守卫腿复发实录·"
"竞速/resolve 脚本模板三必备腿=HEAD symbolic-ref 断言+rebase-merge 在位检查+add 前盘面标记扫描）1,671B 直接入母件尾——"
"逐条字节对账=receipt results/_r836bmc_pit_resolver_rebase2_split.json（零丢失断言=逐块 bytes in target verbatim+母件 30,652-2,521+1,671=29,802B <=30KB）；"
"新坑律仍先入母件后回扫。")

MIGRATE = [
    ("- [2026-10-10 05:5x r818 bm-b] **心跳大列表字段禁全文件手写重录", p('research/pit-protocol-lane.md')),
    ("- [2026-10-10 06:2x r819 bm-b] **D-19 水位写步正典化", p('research/pit-protocol-d19.md')),
    ("- [2026-10-10] bm-a 坑律：Money02/data/lhb/lhb_detail.parquet", p('research/pit-data.md')),
    ("- [2026-10-10 08:4x r824 bm-b] **多环 push 爪竞速判例", p('research/pit-git-staged.md')),
]

INSERT_AFTER_ANCHOR = "- 域指针·r833 bm-c mini-split"

def main():
    b = open(MAIN, 'rb').read()
    pre_main = len(b)
    assert b.endswith(b'\n')
    lines = b.split(b'\n')
    assert lines[-1] == b''
    lines = lines[:-1]  # each element = line content, possibly ending with \r

    receipt = {"ts_round": "r838 bm-c", "action": "CODELY main pointer-row insert + 4-entry re-scan migration",
               "pre_main_bytes": pre_main, "main_eol": "LF-primary (2 CRLF at tail r838 bm-b append zone preserved)",
               "moved": [], "prescan": "treasure_guard prescan rc3 HITs (CODELY.md/pit-git-resolver-rebase.md/rebase2.md) same-round, D-20261002-06 authorized ceremony"}

    removed = []
    for anchor, target in MIGRATE:
        a = anchor.encode('utf-8')
        hits = [i for i, ln in enumerate(lines) if ln.rstrip(b'\r').startswith(a)]
        assert len(hits) == 1, f"anchor not unique/found: {anchor[:40]} hits={hits}"
        removed.append((hits[0], lines[hits[0]], anchor, target))
    for i, entry, anchor, target in sorted(removed, key=lambda x: -x[0]):
        lines.pop(i)

    ia = [i for i, ln in enumerate(lines) if ln.rstrip(b'\r').startswith(INSERT_AFTER_ANCHOR.encode('utf-8'))]
    assert len(ia) == 1, f"insert anchor not unique: {ia}"
    lines.insert(ia[0] + 1, PTR_ROW.encode('utf-8'))

    new_main = b'\n'.join(lines) + b'\n'
    open(MAIN, 'wb').write(new_main)
    post_main = len(new_main)

    for i, entry, anchor, target in removed:
        content = entry.rstrip(b'\r')  # pure content bytes
        tb = open(target, 'rb').read()
        t_crlf = b'\r\n' in tb
        eol = b'\r\n' if t_crlf else b'\n'
        if not tb.endswith(eol):
            tb = tb + eol
        pre_t = len(tb)
        tb = tb + content + eol
        open(target, 'wb').write(tb)
        chk = open(target, 'rb').read()
        assert content in chk, f"verbatim-in-target FAIL: {anchor[:40]}"
        assert content not in new_main, f"still-in-main FAIL: {anchor[:40]}"
        receipt["moved"].append({
            "anchor": anchor[:60], "entry_bytes": len(content), "target": os.path.relpath(target, ROOT),
            "target_eol": "CRLF" if t_crlf else "LF",
            "target_pre_bytes": pre_t, "target_post_bytes": len(tb),
            "entry_md5": hashlib.md5(content).hexdigest(),
        })

    ptr_bytes = len(PTR_ROW.encode('utf-8'))
    removed_join = sum(len(e) + 1 for _, e, _, _ in removed)
    expect = pre_main - removed_join + (ptr_bytes + 1)
    assert expect == post_main, f"byte identity FAIL: expect={expect} post={post_main}"
    assert post_main <= CAP, f"main over cap: {post_main}"
    for m in receipt["moved"]:
        assert m["target_post_bytes"] <= CAP, f"target over cap: {m['target']}"

    receipt.update({"ptr_row_bytes": ptr_bytes, "removed_join_bytes": removed_join,
                    "post_main_bytes": post_main,
                    "byte_identity": f"{pre_main} - {removed_join} + {ptr_bytes + 1} = {post_main}",
                    "post_main_le_cap": True})
    out = p('results/_r838bmc_codely_ceremony.json')
    json.dump(receipt, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(json.dumps({k: receipt[k] for k in ("pre_main_bytes", "removed_join_bytes", "ptr_row_bytes", "post_main_bytes", "byte_identity")}, ensure_ascii=False))
    for m in receipt["moved"]:
        print(f"  -> {m['target']} +{m['entry_bytes']}B now {m['target_post_bytes']}B ({m['target_eol']})")
    print("receipt:", os.path.relpath(out, ROOT))

if __name__ == '__main__':
    main()
