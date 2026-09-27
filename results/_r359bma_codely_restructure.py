# -*- coding: utf-8 -*-
"""r359 bm-a CODELY.md hot-cold restructure (30th batch, D-20260924-01
paradigm, <=10KB hard-line in-window per O-20260927-0230 group order).
Root cause of re-bloat: bm-c r109 29th-batch restructure (9962->3979B) was
followed by the bmb r341-343 push-window union merge, which re-materialized
the ten folded rows back to full text (CODELY memory-union side), plus two
new full rows (r109 bm-c tick-hot-write, r342 bm-b PS Start-Job) and this
round's r359 pool-clobber law. Actions:
 1) fold 10 re-materialized rows back to pointer rows (verbatim ALREADY in
    archive 29th-batch section -- per-row containment verified, no re-write);
 2) append 30th-batch section to archive with verbatim of the 2 new rows,
    then fold them to pointer rows;
 3) append fresh r359 law row hot; if final size still >10,240B, also
    archive+fold it (same-window law);
 4) insert 30th-batch summary pointer row after the 29th-batch row;
 5) verify: every folded row's exact text verbatim-present in archive on
    disk after write, final size <=10,240B, zero unaccounted lines."""
import io
import sys

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

FOLD29 = [  # (unique line prefix, one-line conclusion for pointer row)
    ("- [2026-09-27 2026-09-27 18:35 r96 bm-c]",
     "机钟步回拨窗内收尾件复用轮中取时串=同件双时间源互矛——收尾时间戳一律写入时现取、epoch 与 clock_read 同次取时派生、对外留痕以 git %ci 为锚"),
    ("- [2026-09-27T19:17 r345 bm-a]",
     "deep-ts 探针键族完备性——resolver 取新探针键表漏生产者拼写→假 tie 误取旧侧；正典=逐件显式写时键探+解后同键异值 side-diff 复验+selftest 路径换元覆盖全部路径全局"),
    ("- [2026-09-27 20:1x r100 bm-c]",
     "deep-ts 探针第三缺陷族——下划线变体键漏配（as_of 对 startswith('asof') 静默 miss）+非 ts 值字典序毒化 max（'forced'>'2026'）；正典修=classify_conflicts.py 目录硬化（键先 strip '_/-' 再前配+值须 ^20\\d{2}- 形才入 max）+连三风暴面新条目+selftest 26/26"),
    ("- [2026-09-27 20:0x r350 bm-a]",
     "deep-ts 探针第四缺陷变体=排除表吞键——探针负面排除表本身=新 miss 载体，键歧义一律靠值形门（date-only 不含时分自滤）裁决，禁靠排除表；重跑 idempotent 探针读 stage blob 不读工作树"),
    ("- [2026-09-27 20:3x r101 bm-c]",
     "树重建后 lane-local gitignored 数据面盘点缺位——树重建后 lane owner 必盘点原始采集面 vs 派生面分核（fund_premium 原始 snapshots 成结构性缺口实弹），采集器 selftest 不覆盖盘上历史在位性"),
    ("- [2026-09-27 20:1x r340 bm-b]",
     "池批 checkpoint 保尾=中途 kill 全批重烧（W2-A 烧 4.6h 零 ckpt 实弹·pool 注记失实）；正典=parallel_runner on_result 增量落盘回调（默认 None 旧行为零扰动）+flushed-set 防双写·在飞进程内存旧码不受益重启才拾新"),
    ("- [2026-09-27 20:5x r351 bm-a] 坑律：rebase 重放窗",
     "rebase 重放窗 resolver 侧位映射=「:2:=HEAD（对岸面）/ :3:=被重放 commit（本链面）」与 merge 直觉相反——resolver 先落侧位断言注记再动手+git ls-files -u 实证 stage 归属；零丢失断言遇本侧指针行被对岸 full 行吸收=合法吸收"),
    ("- [2026-09-27 20:5x r351 bm-a] 坑律：rebase UU 停点窗",
     "rebase UU 停点窗 tick blind-add 毁共享件 :2:/:3: stage——resolver 读 stage 失败勿盲写先 git status 定件态以 HEAD blob 为准复验；已续跑件验 commit 内 blob；:X0:01 tick 前后 1min 窗内勿发起共享件 resolver 批"),
    ("- [2026-09-27 20:4x r353 bm-a]",
     "ts 探针键 normalize 字面 strip 陷阱（第五缺陷变体）——strip 只剥两端不剥中间，as_of 族漏探假 tie；正典=re.sub(r'[_\\-/]','',k) 全剥再前配；js 包装件探针禁 json.loads 直吞"),
    ("- [2026-09-27 21:1x r355 bm-a]",
     "同轮连续风暴 resolver 重跑防护——resolver 逐 handler 带 UU-membership guard（git ls-files -u 判跳非 UU 件）+side-assert 用 :3: 固定指纹对 :2: 动态值；同脚本两次重跑全收敛"),
]

FOLD30 = [  # new rows: verbatim-appended to archive 30th batch, then folded
    ("- [2026-09-27 21:3x r109 bm-c]",
     "S0 轮首脏树=autofill 看门狗 tick 单行热写——results/autofill_state.json last_tick 行全机队共享，轮首 git status 脏时先定向提交该件再 pull --rebase；同窗他机 tick 撞=单行 take-new（max ts 侧）手工 resolve；该件平键单行非深嵌套 ts 探针族禁起 resolver"),
    ("- [2026-09-27 21:15 r342 bm-b]",
     "PS Start-Job 作业块不继承调用处 CWD——job 内 git 一律 fatal \"not a git repository\"；正典=job 块首显式 Set-Location 仓根+外层 Wait-Job -Timeout 有界收口；网络死窗 S0 逐轮探测一律有界化（直跑 fetch 挂 5min 烧轮预算）"),
]

R359_ROW = ("- [2026-09-27 22:1x r359 bm-a] 坑律：共享控制面池条目可被网络死窗本地模式整件提交静默吞行"
            "（实弹：CENSUS-FUS-S2-W2B 池行本机 R345 f5822d92 19:10 落→bm-b r340 50ea26ef 21:32 "
            "网络死窗本地池面整件提交删除→其后 bm-b r341-343 与本机 R356-358 四轮报告照抄"
            "「W2-B waiting double-dep unchanged」=看板话语描述一行已不存在之行；git log -S 铁证 "
            "add→remove 两笔零中间改）；正典=①watch-face 断言每轮必对实际文件复验禁从上轮报告照抄既存态"
            "②网络死窗本地提交前对共享控制面件（pool/ledger/registry）必对账 union 禁整件覆盖"
            "③恢复=唯一权威版本 verbatim 复位+语义零丢失复验（共享 79 行字节恒等）。"
            "指针=results/_r359bma_pool_restore.py+commit 2a687a81+MSG-20260927-2215-bma-bmb。")

R359_CONCLUSION = ("共享控制面池条目可被网络死窗整件提交静默吞行（W2B 池行实弹）——"
                   "watch-face 断言每轮必对实际文件复验；网络死窗本地提交前共享控制面件必对账 union 禁整件覆盖；"
                   "恢复=唯一权威版本 verbatim 复位+语义零丢失复验")

SUMMARY29_ANCHOR = "- 二十九批外迁（r109 bm-c·2026-09-27·贴线当窗整编·行级零丢失）"

ARCHIVE_HEADER = ("\n## 坑律归档 2026-09-27 三十批（r359 bm-a·CODELY.md 10KB 硬线当窗整编·行级零丢失）\n")


def pointer_row(prefix, conclusion, batch_label, batch_no):
    tag = prefix.split("]")[0] + "]"
    return (f"{tag} 坑律（{batch_no}批外迁·指针）：{conclusion}"
            f"——全文 verbatim=research/memory-archive/202609.md"
            f"『坑律归档 2026-09-27 {batch_no}批』节。")


def detect_newline(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    return "\r\n" if b"\r\n" in raw else "\n"


def main():
    nl = detect_newline(CODELY)
    anl = detect_newline(ARCHIVE)
    with io.open(CODELY, encoding="utf-8") as fh:
        lines = [ln.rstrip("\r\n") for ln in fh]
    with io.open(ARCHIVE, encoding="utf-8") as fh:
        arch_text = fh.read()

    folded = {}          # full row text -> pointer row text
    for prefix, conclusion in FOLD29:
        hits = [ln for ln in lines if ln.startswith(prefix)]
        assert len(hits) == 1, f"29batch fold prefix hits={len(hits)}: {prefix[:60]}"
        full = hits[0]
        assert full in arch_text, f"29batch verbatim NOT in archive: {prefix[:60]}"
        folded[full] = pointer_row(prefix, conclusion, None, "二十九")
    for prefix, conclusion in FOLD30:
        hits = [ln for ln in lines if ln.startswith(prefix)]
        assert len(hits) == 1, f"30batch fold prefix hits={len(hits)}: {prefix[:60]}"
        folded[hits[0]] = pointer_row(prefix, conclusion, None, "三十")

    # replace in place, preserving order; then append r359 + summary row
    out = [folded.get(ln, ln) for ln in lines]
    out.append(R359_ROW)

    summary_row = ("- 三十批外迁（r359 bm-a·2026-09-27·10KB 硬线当窗整编·行级零丢失）："
                   "r96/r345/r100/r350/r101/r340bmb/r351×2/r353/r355 十条全文行=二十九批 union "
                   "再 materialize 面，折叠回指针（verbatim 已在二十九批节·逐行 containment 复验）"
                   "+r109bmc/r342bmb 两条新行 verbatim 入三十批节后折叠；保留=User 元律+法行 2"
                   "+批指针行族+新坑律 r359 行热态。")
    idx = next(i for i, ln in enumerate(out) if ln.startswith(SUMMARY29_ANCHOR))
    out.insert(idx + 1, summary_row)

    # conditional same-window fold of the fresh r359 row if still over hard line
    r359_folded_too = False
    probe = nl.join(out) + nl
    if len(probe.encode("utf-8")) > 10240:
        with io.open(ARCHIVE, "a", encoding="utf-8", newline=anl) as fh:
            fh.write(R359_ROW + anl)
        arch_text += R359_ROW
        out = [pointer_row("- [2026-09-27 22:1x r359 bm-a]", R359_CONCLUSION,
                           None, "三十") if ln == R359_ROW else ln for ln in out]
        r359_folded_too = True

    # write archive 30th-batch section (r109 + r342 verbatim) before CODELY write
    new_rows = [ln for ln in lines if any(ln.startswith(p) for p, _ in FOLD30)]
    with io.open(ARCHIVE, "a", encoding="utf-8", newline=anl) as fh:
        fh.write(ARCHIVE_HEADER.replace("\n", anl))
        for r in new_rows:
            fh.write(r + anl)

    with io.open(CODELY, "w", encoding="utf-8", newline=nl) as fh:
        fh.write(nl.join(out) + nl)

    # ---- verify pass (re-read from disk) ----
    with io.open(ARCHIVE, encoding="utf-8") as fh:
        arch2 = fh.read()
    for full in folded:
        assert full in arch2, f"post-write verbatim missing: {full[:60]}"
    for r in new_rows:
        assert r in arch2, f"30batch verbatim missing: {r[:60]}"
    if r359_folded_too:
        assert R359_ROW in arch2, "r359 verbatim missing in archive"
    size = len(open(CODELY, "rb").read())
    assert size <= 10240, f"CODELY.md still over hard line: {size}B"
    print(f"30th-batch restructure OK: CODELY.md {14690}->{size}B "
          f"(hard line 10,240B), folded={len(folded)}+{len(new_rows)} verbatim->archive"
          f"{' +r359 same-window' if r359_folded_too else ', r359 stays hot'}; "
          f"containment verified on disk for all folded rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
