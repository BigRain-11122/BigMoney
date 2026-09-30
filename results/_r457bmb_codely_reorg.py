"""_r457bmb_codely_reorg.py -- S4 water-line hot-cold reorg (r444/r448/r455
paradigm). CODELY.md at 9,597B; appending the r457 EM-yjbb boundary lesson
(~900B) would cross the 10KB hard line -> this window, not next month.

Moves the two coldest hot entries (r454 S6-reconfigure, r455 futures-gate)
verbatim into research/memory-archive/202609.md section
"热冷整编 2026-09-30 r457 bm-b 窗批", replaces them in CODELY.md with ONE
combined cold-pointer line (r444 pointer-merge paradigm), then appends the
new r457 entry at file end (physical convention: hot entries at bottom).

Zero-loss contract: archived lines byte-identical to the pre-cut hot layer;
removed lines absent from post-edit CODELY.md; final size < 10,240B.
"""
import io
import os

CODELY = "CODELY.md"
ARCHIVE = "research/memory-archive/202609.md"

E454 = ('- [2026-09-30 r454 bm-b] S6 分离链驱动=reconfigure 律漏网面（r236 族）：'
        '驱动 stdout 重定向文件仍 GBK 写，腿输出含 U+FFFD 即 print 当场炸整链——'
        '链驱动模板必带 sys.stdout.reconfigure(utf-8)；断链续跑=cont 驱动自断腿重放幂等安全。')
E455 = ('- [2026-09-30 r455 bm-b] update_futures 门 no-op≠全腿新鲜读坑：'
        'local_data_cutoff()=VARIETIES（9 员）MAX 聚合——任一员新鲜即门闭，'
        '单员滞后被掩蔽永不重拉（本窗实读 9/9 员齐 09-29 健康·零事故·掩蔽面=latent）；'
        'TS=一次性腿不在 VARIETIES（bm-a T-65 s2 专拉止 09-24·hold 列≠oi 已由 '
        'CTA_WAVE1 冻结件裁定 OHLCV-only）——读期货面板禁以「cutoff covered no-op」'
        '推 10/10 新鲜；修面（min 门/逐员 stale-leg 重拉）=bm-a R48/R51 车道观察件 '
        'results/_r455bmb_futures_gate_probe.json 承载。')
POINTER = ('- 冷层指针（r457 合并·指针合并归档 r444 范式）：r454 S6 分离链驱动 '
           'reconfigure 律漏网面+r455 update_futures 门 no-op 掩蔽坑'
           '（修面=bm-a R48/R51 车道观察件·探针 _r455bmb_futures_gate_probe.json '
           '承载）两条全文 verbatim=archive 202609.md'
           '『热冷整编 2026-09-30 r457 bm-b 窗批』节。')
NEW457 = ('- [2026-09-30 r457 bm-b] EM yjbb 零披露期坑（季末首实弹）：akshare '
          'stock_yjbb_em 对零披露期 EM 回 result:null→TypeError-NoneType=源端'
          '「未发布」信号非传输故障；update_fundamental 原归传输败→rc2 每轮红至'
          '季报披露、eligibility 冻结。修=fetch_yjbb _unpublished_null 栅栏'
          '（type is TypeError+消息匹配→empty 落次候选·与短df 同语义）；真传输='
          '同端点 SSLError 族异类实证；防误标双保险=pick_annual 硬败+within_18m '
          '门禁拦截写；判别法=未发布 1s 页循环前即死 vs 传输败页中死。证据='
          'results/_r457bmb_fundamental_period_probe.json+修后 rc0'
          '（interim 回落 20260630 正确）。')
ARCH_SECTION = (
    "\n## 热冷整编 2026-09-30 r457 bm-b 窗批（CODELY ≤10KB 硬线·追加 EM-yjbb "
    "季末边界坑前·2 条冷指针 verbatim 迁入·行级零丢失）\n\n"
    + E454 + "\n" + E455 + "\n"
    "\n（热冷整编零丢失校验：本节两行与迁移前 CODELY.md 热层逐字节恒等；"
    "整编者=bm-b r457 S4 水位律当窗动作。）\n")


def main():
    with io.open(CODELY, "r", encoding="utf-8", newline="") as fh:
        src = fh.read()
    assert src.count(E454) == 1, "E454 not unique in CODELY.md"
    assert src.count(E455) == 1, "E455 not unique in CODELY.md"

    out = src.replace(E455, POINTER)          # r455 entry -> combined pointer
    out = out.replace(E454 + "\n", "")        # r454 entry dropped (pointer covers)
    out = out.rstrip("\n") + "\n" + NEW457 + "\n"

    with io.open(ARCHIVE, "a", encoding="utf-8", newline="") as fh:
        fh.write(ARCH_SECTION)

    with io.open(CODELY, "w", encoding="utf-8", newline="") as fh:
        fh.write(out)

    # ---- zero-loss verification ----
    with io.open(ARCHIVE, "r", encoding="utf-8") as fh:
        arc = fh.read()
    with io.open(CODELY, "r", encoding="utf-8") as fh:
        cod = fh.read()
    checks = {
        "E454_in_archive": E454 in arc,
        "E455_in_archive": E455 in arc,
        "E454_absent_hot": E454 not in cod,
        "E455_absent_hot": E455 not in cod,
        "pointer_present": POINTER in cod,
        "new457_present": NEW457 in cod,
        "hot_under_10KB": os.path.getsize(CODELY) < 10240,
    }
    print("size before:", len(src.encode('utf-8')), "-> after:",
          os.path.getsize(CODELY))
    print(json.dumps(checks))
    assert all(checks.values()), "ZERO-LOSS CONTRACT VIOLATED"


if __name__ == "__main__":
    import json
    main()
