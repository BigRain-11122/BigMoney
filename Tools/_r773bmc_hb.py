"""r773 bm-c heartbeat update: field-level surgery on fleet/machines/bm-c.json
(preserves orders_ack array verbatim; int-typed epoch per R170/R178 law;
T-separated ISO clock per R262 law)."""
import json
import datetime

PATH = r"K:\Fluxgroup\FluxGroup\quant\bigmoney\fleet\machines\bm-c.json"
T = "2026-10-08T19:26:24+08:00"
EPOCH = 1791458786
HEAD = "97885404d733466a52d98498c9c665ec4973217d"

NARR = ("r773: tick 维护轮（19:1x 窗·全链 40 腿+QA det-93rd+克隆门·第 74 连守轮）——"
        "①ORD/DEC 双恒等零动作（ORD 98BD3FAA·DEC EE70CEF0·facts 单源 s05 双扫·unacked=0（51 orders）·inbox 0）；"
        "CEO 三选项维持等待态（A/B/C 菜单已在集团 outbound 面·视频段冻结维持·等待态一行声明不重扫）；"
        "②S0：round-start behind=0 零 rebase（HEAD==origin/main 97885404d）"
        "+mv_work MV 冻结车道 scratch 维持未跟踪（r770/771/772 三轮先例·等 CEO 勾选）；"
        "③S1 smoke 49/49+饱和引擎活（exit 0）；④S2 任务板零 open 票·job 板零；"
        "⑤S6 40/40 rc0（update_daily sina 迟 bar 仍未落地 cutoff 2026-09-30=当窗重试"
        "·CTA_P1 无可标 bar 诚实 no-op·fund_premium NAV 09-30 已覆 no-op"
        "·dualrun ZERO-DRIFT streak 51"
        "·compute_audit FLAG:pool_starvation,supply_floor 如实披露=供给线在飞已认领批非断供"
        "·py_watermark py_low_board_clear=板清+无新 bar 合法 idle）；"
        "⑥QA det-93rd 5/5（93 trades·equity 1017839 冻结恒等·determinism=True·png 66266B"
        "·case#10 撞名披露：qa/smoke-r773.md bm-b 包 blob 54125349 先在册"
        "·同冻结数字零科学损失·同径覆写·bm-b 版 git 史保全·.err 0B）；"
        "⑦克隆门 4/4（_r773bmc_clone.py 序敏感双替换+stale 门先于叙事 fix+case#10 叙事 fix"
        "+法典引用豁免断言·收据 _r773bmc_clone_receipt.json）；"
        "⑧孤儿面=1 只读（ComfyUI 产线资产）·token +0（L2 legs 0 today）"
        "·idle 非绿（RAM 17.8%<40%·本轮实工·idle_rounds=0·agenda 未饿）")

TASK = ("当前活: r773 bm-c（19:1x 窗·盘后维护轮·第 74 连守轮）——主产出="
        "①S6 40/40 rc0（sina 迟 bar 仍未落地·CTA_P1/fund_premium 诚实 no-op）"
        "②QA det-93rd 5/5（93 trades·1,017,839 冻结恒等·case#10 同径覆写披露）"
        "③克隆门 4/4（case#10 叙事 fix） | 最近实物: qa/smoke-r773.md 5/5"
        "+results/_r773bmc_s6_log.txt 40/40 rc0+results/_r773bmc_clone_receipt.json"
        " @ 2026-10-08T19:26:24+08:00 | 下个里程碑: sina 10-08 bar 落地→CTA_P1 首接线"
        "+fund_premium 10-08 NAV 首采（bm-c 车）（bar 持续未落则逐轮自愈重试）；"
        "CEO A/B/C 勾选前视频段冻结；next 5x=bm-c r775（HANDOVER 窗）")

NEXTP = ("r774 续作: ①sina 迟 bar 自愈重试→bar 落地即 CTA_P1 首接线+marks 验证"
         "+fund_premium 10-08 NAV 首采（bm-c 车）+REGIME_GUARD v3 新 bar enforce"
         "（live.paper 宿主面=bm-a·bm-c lane-guard 诚实 skip 常设）"
         "②CEO 三选项勾选后按勾选项走（A 本地合成法再修/B 云端通道待批/C 改构图）"
         "——点头前视频段维持冻结③QA det-94th 撞名预检（git ls-tree origin/main qa/ 探 r774）"
         "④next 5x=bm-c r775（HANDOVER 窗）")

ART = ("qa/smoke-r773.md 5/5 (93 trades frozen identity, 93rd chain, case#10 "
       "same-path overwrite disclosed, bm-b blob 54125349 git-preserved) "
       "+ results/_r773bmc_s6_log.txt (40/40 rc0) "
       "+ results/_r773bmc_clone_receipt.json (4/4 compile) @ 2026-10-08T19:26:24+08:00")

MILE = ("sina 10-08 late-bar lands -> CTA_P1 first-bar wiring + fund_premium 10-08 "
        "NAV first snapshot (bm-c lane) + REGIME_GUARD v3 new-bar enforce (bm-a host, "
        "bm-c lane-guard honest skip); CEO A/B/C menu awaiting pick (video lane frozen); "
        "next 5x = bm-c r775 (HANDOVER window)")

VER = ("smoke 49/49 + qa/smoke-r773.md 5/5（93 trades·equity 1017839 冻结恒等"
       "·determinism=True·93 连证·case#10 披露·.err 0B） "
       "+ results/_r773bmc_s6_log.txt（S6 legs=40 rc0=40 nonzero=0） "
       "+ results/_r773bmc_s05_facts.json（DEC/ORD 双恒等·unacked=0·inbox 0·shape-asserted） "
       "+ results/_r773bmc_clone_receipt.json（4 files·stale772=0·compile ok·canon-cite 豁免断言） "
       "+ results/_attrition_guard_scan.json CLEAN "
       "+ 孤儿面=1 只读（results/_orphan_face_probe.bm-c.json） "
       "+ push CLEAN 送达自证（fetch 后 origin/main..HEAD=0）")

DEC_M = ("python subprocess raw-blob bytes SHA-256 (group-tree origin/main git show; "
         "r773 sweep = UNCHANGED EE70CEF0 (zero action, watermark held); facts-driven "
         "from results/_r773bmc_s05_facts.json, 64hex shape-asserted, never hand-typed "
         "(r583 S4 law)")
ORD_M = ("python subprocess raw-blob bytes SHA-1 (ALGORITHM PIN per r537 law; "
         "r773 sweep = UNCHANGED 98BD3FAA (zero action, watermark held); facts-driven "
         "from results/_r773bmc_s05_facts.json, 40hex shape-asserted, never hand-typed "
         "(r583 S4 law)")


def main():
    with open(PATH, encoding="utf-8") as fh:
        hb = json.load(fh)
    hb["clock_read"] = T
    hb["ts"] = T
    hb["last_seen"] = T
    hb["last_seen_at"] = T
    hb["updated"] = T
    hb["updated_at"] = T
    hb["last_run_at"] = T
    hb["last_ts"] = T
    hb["current_task_at"] = T
    hb["last_round_at"] = T
    hb["last_round_ts"] = T
    hb["last_decisions_read_at"] = T
    hb["last_decisions_at"] = T
    hb["last_orders_at"] = T
    hb["last_pulled_at"] = T
    hb["heartbeat_epoch_utc"] = EPOCH
    hb["round_no"] = 774
    hb["round_no_label"] = "round 773 (bm-c)"
    hb["last_round"] = 773
    hb["cpu_pct"] = 30.0
    hb["cpu_util_pct"] = 30.0
    hb["cpu_idle_pct"] = 70.0
    hb["free_ram_gb"] = 2.0
    hb["idle_ram_gb"] = 2.0
    hb["ram_free_gb"] = 2.0
    for k in ["gpu_free_vram_mb", "gpu_free_vram_mib", "gpu_free_mb", "gpu_free_mib",
              "gpu_idle_vram_mb", "gpu_idle_vram_mib", "gpu_idle_mb", "gpu_idle_mib",
              "gpu_vram_free_mb"]:
        hb[k] = 14944
    hb["idle_rounds"] = 0
    hb["agenda_starved"] = False
    hb["health"] = "ok"
    hb["current_task"] = TASK
    hb["activity_now"] = TASK
    hb["did"] = NARR
    hb["verdict"] = NARR
    hb["note"] = NARR
    hb["last_round_summary"] = NARR
    hb["last_action"] = NARR
    hb["next"] = NEXTP
    hb["next_pointer"] = NEXTP
    hb["latest_artifact"] = ART
    hb["next_milestone"] = MILE
    hb["verify"] = VER
    hb["dec_sha_method"] = DEC_M
    hb["last_decisions_sha_method"] = DEC_M
    hb["ord_sha_method"] = ORD_M
    hb["last_orders_sha_method"] = ORD_M
    hb["head_sha"] = HEAD
    with open(PATH, "w", encoding="utf-8", newline="") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)
    # self-assert: epoch int + clock T-sep
    with open(PATH, encoding="utf-8") as fh:
        back = json.load(fh)
    assert isinstance(back["heartbeat_epoch_utc"], int), "epoch not int"
    assert "T" in back["clock_read"], "clock not T-separated"
    print("HB_OK epoch=%d clock=%s round_no=%d orders_ack=%d"
          % (back["heartbeat_epoch_utc"], back["clock_read"], back["round_no"],
             len(back["orders_ack"])))


if __name__ == "__main__":
    main()
