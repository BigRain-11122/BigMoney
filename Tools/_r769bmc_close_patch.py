# -*- coding: utf-8 -*-
"""r769 bm-c close patch: fold the O-1820 three-law-gate verdict + v2 regen
spawn into the state/heartbeat living faces and append the r769 addendum row
to the canonical round report. Runs AFTER _r769bmc_close.py (gate happened
post-close-write; honest addendum per r768 addendum precedent)."""
import datetime
import json
import os

ROOT = r"K:\Fluxgroup\FluxGroup\quant\bigmoney"
NOW = datetime.datetime.now().astimezone()
TS = NOW.isoformat(timespec="seconds")

ADD = ("r769 addendum: O-1820 风格样图批 7/7 完成（17:51:10 ok=True）→三律人眼门 8 盲评落判"
       "（analyze_multimedia 面）：4 PASS=st3_goddess_a（filmic 7/comp 9/world 6·人形分明·teal 顶格"
       "+十字尖顶 flag）+st3_goddess_b（7/8/7·mist smudge 小 flag·择优）+st4_glass_a（7/7/7·青板过大 flag·择优）"
       "+st4_glass_b（6/8/7·mild 水彩 bleed flag）；4 FAIL=st1_library_a（filmic 2·平面向量感·双影完全缺席·"
       "codex 书非泥板）+st1_library_b（filmic 3·双影缺席·水墨漏 YES）+st2_carve_b（filmic 9 但灰阶非暖橙+"
       "圣书体非楔形+无刻写动作）+kf1_carve（金属笔穿帮+灰阶+楔形不可读）——核心三张两张未过=禁呈 CEO；"
       "v2 重生成 4 张 spawn（st1_library_c/d+st2_carve_c/d·photographic 实拍语汇前置+暖橙 grade 前置+"
       "扩展负面词〔flat illustration/vector/水墨族/hieroglyphs/metal pen/codex 族〕·seed 20011016-19·"
       "_r769bmc_style_regen.py detached）")

ACT = ("当前活: r769 bm-c（17:37-18:1x 窗·O-1820 顺序改判令 P0 执行轮·收尾）——主产出=①违令面即刻收口"
       "（i2v 视频驱动 31384 击杀·令前 seg1/2 冻结非交付物）②O-1820 风格样图批 7/7 全完成+三律人眼门 8 盲评"
       "（4 PASS=女神 a/b+玻璃 a/b·4 FAIL=书库双影 a/b+刻字双候选）→v2 重生成 4 张在烧（photographic 修正+"
       "扩展负面词）③QA det-89th 5/5 无撞名首注册 ④S6 40/40 rc0 ⑤静默三件 group 新正本同步 | 最近实物: "
       "results/mv_work/kf/st*.png 7 张 v1 全落+v2 4 张在烧+qa/smoke-r769.md 5/5 @ " + TS +
       " | 下个里程碑: v2 过门→四景择优（书库双影/刻字/女神=择优/玻璃=择优）+分镜表（R-craft-deep 落点A/B="
       "results/_r768bmc_mv_craftdeep.md）→outbound 呈 CEO 过目（今晚）——CEO 合格前禁视频; next 5x=bm-c r770"
       "（HANDOVER 窗）")

NEXTP = ("r770 续作（5x HANDOVER 窗·r765-r769 产物清单核对）: ①O-1820 主线=查 results/mv_work/style_gen.log "
         "v2 四张（st1_library_c/d+st2_carve_c/d·落点=results/mv_work/kf/）→三律门盲评→全过则与 v1 已过门择优"
         "（goddess=st3_goddess_b·glass=st4_glass_a）合成核心三景+玻璃共 4 张呈审包；仍有 FAIL 再修正重生成"
         "（修正方向已录：photographic 实拍语汇/负面词扩展/暖橙 grade 前置/双影必须可读/芦苇笔非金属）"
         "②分镜表呈审件=R-craft-deep（results/_r768bmc_mv_craftdeep.md）落点A 十场镜头规格表+落点B 234s 逐段"
         "剪辑图整理成呈审文件+SP 规格随包③outbound=cph4/fleet/mv0001-handover/outbound/（group 仓·CAS 直投律"
         "·样图转 jpg）→bm-a 查看→呈 CEO 过目；CEO 合格前禁任何视频段（i2v 已杀·O-1715/1755 视频目标冻结）"
         "④sina 迟 bar 自愈重试→bar 落地即 CTA_P1 首接线+marks 验证（fund_premium 今日首采已落 fresh<24h）"
         "⑤QA 点火律 S6→qa_ignite→poll 终态⑥撞名预检 r770：git ls-tree origin/main qa/ 探 bm-b r770 包"
         "⑦轮报行写正典 logs/iteration-loop/round_reports-bm-c.md（r750 律）⑧风格样图批收尾校验（style_gen.log "
         "done ok=True 面）")


def main():
    sp = os.path.join(ROOT, "state-bm-c.json")
    state = json.load(open(sp, encoding="utf-8"))
    state["did"] = ADD + " || " + state.get("did", "")
    state["note"] = state["did"]
    state["last_round_summary"] = state["did"]
    state["last_action"] = state["did"]
    state["verdict"] = state["did"]
    state["current_task"] = ACT
    state["activity_now"] = ACT
    state["current_task_at"] = TS
    state["next"] = NEXTP
    state["next_pointer"] = NEXTP
    state["latest_artifact"] = (
        "results/mv_work/kf/st*.png O-1820 style-sample batch v1 7/7 + v2 regen "
        "4 in-flight (gate: 4 PASS / 4 FAIL disclosed) + qa/smoke-r769.md 5/5 "
        "(93 trades frozen identity) + results/_r769bmc_s6_log.txt 40/40 rc0 @ " + TS)
    state["next_milestone"] = (
        "O-1820 gate: v2 regen -> gate -> 4-scene package (core three + glass) + "
        "storyboard -> outbound -> CEO review TONIGHT; video lane frozen until "
        "CEO approval; sina late-bar self-heal per round; next 5x = bm-c r770 "
        "HANDOVER window")
    state["ts"] = TS
    state["last_seen"] = TS
    state["updated"] = TS
    with open(sp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(state, fh, indent=1, ensure_ascii=False)

    hp = os.path.join(ROOT, "fleet", "machines", "bm-c.json")
    hb = json.load(open(hp, encoding="utf-8"))
    hb["did"] = state["did"]
    hb["note"] = state["did"]
    hb["last_round_summary"] = state["did"]
    hb["last_action"] = state["did"]
    hb["verdict"] = state["did"]
    hb["current_task"] = ACT
    hb["activity_now"] = ACT
    hb["current_task_at"] = TS
    hb["next"] = NEXTP
    hb["next_pointer"] = NEXTP
    hb["latest_artifact"] = state["latest_artifact"]
    hb["next_milestone"] = state["next_milestone"]
    hb["ts"] = TS
    hb["last_seen"] = TS
    hb["updated"] = TS
    with open(hp, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(hb, fh, indent=1, ensure_ascii=False)

    rpt = os.path.join(ROOT, "logs", "iteration-loop", "round_reports-bm-c.md")
    row = ("{ts} | r769 addendum | {add} | verify: 盲评 8 件逐件 verdict 行在案（analyze_multimedia "
           "面·PASS 四件均 filmic>=6+comp>=7+world>=6·FAIL 四件=场景要件缺席/风格违例/文明错配三类）+ "
           "v2 regen spawn 收据=style_gen.log v2 start 行 | next: {nextp} [via bm-c r769]\n"
           ).format(ts=TS, add=ADD, nextp=NEXTP)
    with open(rpt, "a", encoding="utf-8", newline="\n") as fh:
        fh.write(row)

    for f in (sp, hp):
        d = json.load(open(f, encoding="utf-8"))
        assert isinstance(d["heartbeat_epoch_utc"], int), f
    print(json.dumps({"ts": TS, "patched": ["state", "heartbeat", "rpt-addendum"],
                      "epoch_int_ok": True}, indent=1))


if __name__ == "__main__":
    main()
