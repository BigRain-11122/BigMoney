# r945 bm-a 5x HANDOVER stamp (r910 append-style precedent; double-write guarded; CRLF preserved)
import sys

PATH = "research/HANDOVER.md"

ENTRY = (
    "> bm-a round 945 五轮核对（2026-10-10 06:5x·增量窗 r941-r945·r940 单轮核对为基线·逐轮权威=round_reports-bm-a.md 全量在库·r941 死窗零 state/report 写=遗产由 r942 吸收如实注记）："
    "窗口主线=**THERMO-OVERLAY-P1 判决链全程闭环（T-181 slice-2·O-20261009-2340 承接③政体门情绪臂 overlay 判据面·多胞诚实负判决照报不粉饰）**——"
    "r941 死窗遗产（runner 多核改造=autofill single_core 拒收后 6 workers ProcessPool+烧录经 autofill 04:58 点火 262.86s·commit 335d51053 on origin）"
    "→r942 判决吸收（**0/6 full-chain 诚实多胞负**：G1' line_ok 6x False=P 轴 skill_line==passive 零增量+H 轴低于 max-skill 线·M1 4/6 过（t 3.18/3.41/3.48/3.11）H12 2.84/PH 2.92 落·"
    "F6 P1000 entries 17<30 与冻结 §5.3 预言精确命中·D6 零拒 max|corr| 0.3168·PBO 0.4 observe·best P1000 SR 0.6509 +0.047 vs passive 0.6035 且 maxdd 恒等 -1.1656=回撤零改善）"
    "+prereg §7/§8 机器回填（冻结 §5 预言 5/5 对账）+gate_attrition 判决行（**+1,206 trials·账本 860,945→862,151 实账推进**）"
    "+池关链（r497 先例 claim 回填+harvest flip 05:23:04+runner _pool_claim 腿修复自检 21/21 后）+T-2026-10-10-181 票 done"
    "+TREASURE +1（判决 runner 必带 worker claim-close 腿=TREASURE_REGISTRY 新行）"
    "→r943 P0 治愈（WM red=true 05:42:03 pool-batch-runnable-idle-low-cpu=THERMO stale-ready：r942 收尾只翻车道镜像漏翻共享 runnable_pool.json=inverse-r688 案"
    "→双层 done-flip 手术 _r943bma_flip.py·claim 件证据 closed-ok 05:02:41+entry+shard→done+done_at 回填实际完成时点→复探 05:48:03 red=false lane healthy 闭环当窗验证）"
    "+S0 风暴正典解（13 UU：merge_lane_views x7+双胞胎 x6+SatEngine live-wins x3）"
    "→r944 守望窗全绿（S0 0/0·S6 39 腿 rc0·watermark 绿·DEC b87a92b1 MATCH·四件套绿）"
    "→r945 本窗=5x 盖章+守望续（S6 39 腿驱动器在飞·receipt 本轮吸收）。"
    "窗口引擎面=W203 finalize（r938·账本 858,745+2,200=860,945 EXACT·K 444,520·skill_line 1.1887·§7/§8 回填·staircase SIXTY-THIRD instance）承上窗收口；"
    "**W204 席位=bm-c 锁定（MSG-20261010-0022-bmc·194th wave）bm-c owner 待 arm**——N1 永续供给线交棒他机窗（bm-a 下波=W205·derive 前置=W204 首烧落账）；"
    "W17 出场轴判决链=**bm-c 车道 RAM 门随行**（SCREEN 0-4 keepalive·SHARD-7/JUDGE ready-but-lane-pinned 不跨机认领）。"
    "CEO 令面=O-20261010-0058 Tailscale 改名 dasheng→bm-a（r938 幂等重执+回执三件全绿+checkbox 落令件）"
    "+jman LoRA 权重三件双通道传输 r933 开航→r937 superseded by bm-c ModelScope trio hash-gate PASS 收线"
    "+O-20261009-1105 update_options RETIRE（S6 链腿跳过·bm-c formal disposition due 10-16）。"
    "维护面=smoke 49/49 链+S6 38-39 腿 rc0 链（周六 no-new-bar 诚实 no-op 族·panel tail 2026-10-09）+attrition CLEAN 4 台账链"
    "+orders 双扫零未回执链（199 ack）+四件套绿链（pin=8）+DEC b87a92b1/ORD 0ddb01d9 python-raw MATCH 链+孤儿面=ComfyUI 8188 MV 车道豁免只读链。"
    "产品清单漂移=results/thermo_overlay_p1/ 8 件（thermo_overlay_p1_results.json 57,044B 判决头文件+6 cells CSV+nulls_detail）"
    "+research/THERMO-OVERLAY-P1.md §7/§8 回填+scripts/thermo_overlay_p1.py（claim-leg 修复后）"
    "+results/pool_claims/THERMO-OVERLAY-P1-BURN/+results/_r943bma_flip.py 官族+knowledge/TREASURE_REGISTRY.md 新行"
    "+state heal 940→942→945 诚实序列（r941 死窗零写）。"
    "指针：**PARKING-P1 烧录 due 10-14 12:00（bm-a 车道·SEED_REGISTRY parking_p1_null_base=94_300·watchdog 在节奏）**"
    "+W17 funnel bm-c（JUDGE 待 RAM 门≥4GB）+W204 五面冻结窗 bm-c owner+bm-a W205 席位链（W204 落地后）+月界首考 10-31（T-143 装配交付 10-29）；"
    "下一 5x=bm-a r950。[via bm-a r945]\r\n"
)

def main():
    with open(PATH, "rb") as f:
        b = f.read()
    text = b.decode("utf-8")
    guard_key = "bm-a round 945 五轮核对"
    if guard_key in text:
        print("GUARD: stamp already present, abort (idempotent no-op)")
        sys.exit(0)
    pre_size = len(b)
    assert b.endswith(b"\r\n"), "tail must be CRLF-terminated"
    add = ENTRY.encode("utf-8")
    assert add.replace(b"\r\n", b"").find(b"\n") == -1, "entry must be CRLF-only"
    with open(PATH, "ab") as f:
        f.write(add)
    with open(PATH, "rb") as f:
        post = f.read()
    assert len(post) == pre_size + len(add), "byte-exact append failed"
    assert guard_key in post.decode("utf-8"), "stamp missing post-append"
    assert post.replace(b"\r\n", b"").find(b"\n") == -1, "bare LF injected"
    print(f"APPEND OK: {pre_size} -> {len(post)} (+{len(add)} B), stamp landed, CRLF pure")

if __name__ == "__main__":
    main()
